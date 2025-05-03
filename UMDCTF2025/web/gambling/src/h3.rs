use crate::router::Router;
use bytes::Bytes;
use http::Method;
use quinn::crypto::rustls::QuicServerConfig;
use rustls::pki_types::{CertificateDer, PrivateKeyDer};
use std::net::SocketAddr;
use std::sync::Arc;

pub async fn run_h3_server(
    router: Router,
    certs: Vec<CertificateDer<'static>>,
    privkey: PrivateKeyDer<'static>,
    bind_address: SocketAddr,
) {
    let mut crypto = rustls::ServerConfig::builder()
        .with_no_client_auth()
        .with_single_cert(certs, privkey)
        .unwrap();
    crypto.alpn_protocols = vec![b"h3".to_vec()];

    let quic_config =
        QuicServerConfig::try_from(crypto).expect("Failed to create QUIC server config");
    let quinn_config = quinn::ServerConfig::with_crypto(Arc::new(quic_config));
    let endpoint = quinn::Endpoint::server(quinn_config, bind_address)
        .expect("Failed to create Quinn server config");
    println!("Listening on UDP {} for HTTPS, HTTP/3", bind_address);

    let router = Arc::new(router);
    while let Some(incoming) = endpoint.accept().await {
        let router = router.clone();
        tokio::spawn(async move {
            if let Ok(conn) = incoming.await {
                handle_quic_connection(router, conn).await;
            };
        });
    }
}

async fn handle_quic_connection(router: Arc<Router>, quic_conn: quinn::Connection) {
    let mut h3_conn: h3::server::Connection<_, Bytes> = {
        let quinn_adapter = h3_quinn::Connection::new(quic_conn.clone());
        match h3::server::Connection::new(quinn_adapter).await {
            Ok(h3_conn) => h3_conn,
            Err(_) => return,
        }
    };

    loop {
        let Ok(Some((req, mut stream))) = h3_conn.accept().await else {
            return;
        };

        let router = router.clone();
        let quic_conn = quic_conn.clone();
        tokio::spawn(async move {
            let _ = handle_h3_request(&router, &quic_conn, &req, &mut stream).await;
        });
    }
}

async fn handle_h3_request(
    router: &Router,
    quic_conn: &quinn::Connection,
    req: &http::Request<()>,
    stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
) -> Result<(), h3::Error> {
    match (req.method(), req.uri().path()) {
        (&Method::GET, "/") => router.index(stream).await?,
        (&Method::GET, "/letsgo.mp3") => router.letsgo(stream).await?,
        (&Method::GET, "/dangit.mp3") => router.dangit(stream).await?,
        (&Method::POST, "/register") => router.register(quic_conn, stream).await?,
        (&Method::GET, "/login") => router.login(quic_conn, req, stream).await?,
        (&Method::POST, "/redeem") => router.redeem_code(quic_conn, req, stream).await?,
        (&Method::GET, "/credits") => router.credits(quic_conn, req, stream).await?,
        (&Method::POST, "/wager") => router.wager(quic_conn, req, stream).await?,
        (&Method::POST, "/flag") => router.flag(quic_conn, req, stream).await?,
        _ => router.not_found(stream).await?,
    }

    stream.finish().await?;
    Ok(())
}
