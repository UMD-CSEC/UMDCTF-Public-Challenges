use rustls::pki_types::{CertificateDer, PrivateKeyDer};
use std::io;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::io::AsyncWriteExt;

pub async fn run_h1_server_https(
    certs: Vec<CertificateDer<'static>>,
    privkey: PrivateKeyDer<'static>,
    bind_address: SocketAddr,
) {
    let mut crypto = rustls::ServerConfig::builder()
        .with_no_client_auth()
        .with_single_cert(certs, privkey)
        .unwrap();
    crypto.alpn_protocols = vec![b"http/1.1".to_vec()];
    let mut tls_acceptor = tokio_rustls::TlsAcceptor::from(Arc::new(crypto));

    let tcp_listener = tokio::net::TcpListener::bind(bind_address)
        .await
        .unwrap_or_else(|e| panic!("Failed to bind to TCP {}: {e:?}", bind_address));
    println!("Listening on TCP {} for HTTPS, HTTP/1.1", bind_address);

    loop {
        let _ =
            accept_and_serve_h1_https_conn(&tcp_listener, &mut tls_acceptor, bind_address.port())
                .await;
    }
}

async fn accept_and_serve_h1_https_conn(
    tcp_listener: &tokio::net::TcpListener,
    tls_acceptor: &mut tokio_rustls::TlsAcceptor,
    h3_port: u16,
) -> Result<(), io::Error> {
    let (tcp_stream, _) = tcp_listener.accept().await?;
    let mut tls_stream = tls_acceptor.accept(tcp_stream).await?;

    tls_stream
        .write_all(
            format!(
                "HTTP/1.1 200 OK\r\nAlt-Svc: h3=\":{}\"\r\nContent-Length: 177\r\nConnection: close\r\n\r\nIf you can see this, try refreshing the page. We have migrated our infrastructure to HTTP/3. If you're using a custom HTTP client-you shouldn't be doing that in the first place!",
                h3_port
            ).as_bytes(),
        ).await?;
    tls_stream.shutdown().await?;

    Ok(())
}

pub async fn run_h1_server_http(bind_address: SocketAddr, https_url: &str, h3_port: u16) {
    let tcp_listener = tokio::net::TcpListener::bind(bind_address)
        .await
        .unwrap_or_else(|e| panic!("Failed to bind to TCP {}: {e:?}", bind_address));
    println!("Listening on TCP {} for HTTP, HTTP/1.1", bind_address);

    loop {
        let _ = accept_and_serve_h1_http_conn(&tcp_listener, https_url, h3_port).await;
    }
}

async fn accept_and_serve_h1_http_conn(
    tcp_listener: &tokio::net::TcpListener,
    https_url: &str,
    h3_port: u16,
) -> Result<(), io::Error> {
    let (mut tcp_stream, _) = tcp_listener.accept().await?;

    tcp_stream
        .write_all(
            format!(
                "HTTP/1.1 301 Moved Permanently\r\nAlt-Svc: h3=\":{}\"\r\nLocation: {}\r\nConnection: close\r\n\r\n",
                h3_port,
                https_url
            ).as_bytes()
        )
        .await?;
    tcp_stream.shutdown().await?;

    Ok(())
}
