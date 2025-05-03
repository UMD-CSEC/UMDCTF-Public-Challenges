mod h1;
mod h3;
mod h3_util;
mod router;
mod user;

use crate::router::Router;
use crate::user::UserDatabase;
use rustls::pki_types::pem::PemObject;
use rustls::pki_types::{CertificateDer, PrivateKeyDer};
use std::net::{Ipv4Addr, SocketAddr};
use std::str::FromStr;
use std::sync::Arc;
use tokio::task::JoinSet;

#[tokio::main]
async fn main() {
    let flag = std::env::var("FLAG").expect("FLAG environment variable missing");
    rustls::crypto::aws_lc_rs::default_provider()
        .install_default()
        .expect("Failed to install crypto provider");
    let certs: Vec<_> = CertificateDer::pem_file_iter("fullchain.pem")
        .expect("Failed to load fullchain.pem")
        .map(|result| result.expect("Failed to load fullchain.pem"))
        .collect();
    let privkey = PrivateKeyDer::from_pem_file("privkey.pem").expect("Failed to load privkey.pem");

    let database = Arc::new(UserDatabase::new());
    {
        let database = database.clone();
        tokio::spawn(async move {
            loop {
                tokio::time::sleep(std::time::Duration::from_secs(300)).await;
                database.reset();
            }
        });
    }
    let router = Router::new(flag, database);

    let https_port = std::env::var("HTTPS_PORT")
        .ok()
        .and_then(|port_str| u16::from_str(&port_str).ok())
        .unwrap_or(8443);
    let https_address = SocketAddr::from((Ipv4Addr::UNSPECIFIED, https_port));
    let http_port = std::env::var("HTTP_PORT")
        .ok()
        .and_then(|port_str| u16::from_str(&port_str).ok())
        .unwrap_or(8080);
    let http_address = SocketAddr::from((Ipv4Addr::UNSPECIFIED, http_port));
    let https_url = std::env::var("HTTPS_URL").expect("HTTPS_URL environment variable missing");

    let mut tasks = JoinSet::new();
    {
        let cert = certs.clone();
        let privkey = privkey.clone_key();
        tasks.spawn(async move { h1::run_h1_server_https(cert, privkey, https_address).await });
    }
    {
        tasks.spawn(
            async move { h1::run_h1_server_http(http_address, &https_url, https_port).await },
        );
    }
    {
        tasks.spawn(async move { h3::run_h3_server(router, certs, privkey, https_address).await });
    }

    tasks.join_all().await;
}
