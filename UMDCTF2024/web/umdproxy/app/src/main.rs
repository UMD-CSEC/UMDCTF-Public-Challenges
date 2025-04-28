use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;
use anyhow::anyhow;
use axum::{extract, Router};
use axum::http::{HeaderMap, StatusCode};
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use bytes::Bytes;
use http_body_util::{Empty, Full};
use hyper::Request;
use hyper_util::rt::TokioIo;
use rustls::{ClientConfig, RootCertStore};
use rustls::pki_types::ServerName;
use tokio::net::{TcpListener, TcpStream};
use serde::Deserialize;
use serde_json::json;
use tokio::io::{AsyncRead, AsyncWrite};
use tokio::sync::Mutex;
use tokio_rustls::TlsConnector;
use tower_http::services::ServeDir;
use tower_sessions::{MemoryStore, Session, SessionManagerLayer};
use url::Url;

#[derive(Clone)]
struct AppState {
    users: Arc<Mutex<HashMap<String, Account>>>,
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .nest(
            "/api",
            Router::new()
                .route("/contact", post(contact))
                .route("/register", post(register))
                .route("/login", post(login))
                .route("/info", get(info))
                .route("/flag", post(flag))
                .route("/guess/pl", post(guess_pl))
                .route("/guess/movie", post(guess_movie))
                .route("/redeem-proxy", post(redeem_proxy))
                .route("/redeem-proxy/check", get(redeem_proxy_check))
                .route("/add-credits", post(add_credits)),
        )
        .fallback_service(ServeDir::new("static"))
        .with_state(AppState {
            users: Arc::new(Mutex::new(HashMap::new())),
        })
        .layer(SessionManagerLayer::new(MemoryStore::default()));

    let listener = TcpListener::bind("0.0.0.0:80").await
        .expect("Failed to bind to 0.0.0.0:80");
    axum::serve(listener, app.into_make_service()).await.expect("Failed to serve HTTP server");
}

async fn contact() -> impl IntoResponse {
    (StatusCode::OK, "Message received")
}

struct Account {
    username: String,
    password: String,
    credits: i32,
    has_flag: bool,
    redeemed_pl: bool,
    redeemed_movie: bool,
    redeemed_proxy: bool,
    currently_redeeming_proxy: bool,
    proxy_redeem_result: Option<bool>,
}

impl Account {
    fn new(username: String, password: String) -> Self {
        Account {
            username,
            password,
            credits: 0,
            has_flag: false,
            redeemed_pl: false,
            redeemed_movie: false,
            redeemed_proxy: false,
            currently_redeeming_proxy: false,
            proxy_redeem_result: None,
        }
    }
}

#[derive(Deserialize)]
struct RegisterUser {
    username: String,
    password: String,
}

async fn register(extract::State(state): extract::State<AppState>, extract::Json(payload): extract::Json<RegisterUser>) -> impl IntoResponse {
    let mut users = state.users.lock().await;
    if users.contains_key(&payload.username) {
        return (StatusCode::BAD_REQUEST, "User already exists");
    }

    users.insert(payload.username.clone(), Account::new(payload.username, payload.password));
    (StatusCode::OK, "Account created").into()
}

#[derive(Deserialize)]
struct LoginUser {
    username: String,
    password: String,
}

async fn login(extract::State(state): extract::State<AppState>, session: Session, extract::Json(payload): extract::Json<LoginUser>) -> impl IntoResponse {
    let users = state.users.lock().await;
    match users.get(&payload.username) {
        Some(user) => {
            if user.password != payload.password {
                return (StatusCode::BAD_REQUEST, "Invalid password");
            }

            session.insert("username", payload.username).await.unwrap();
            (StatusCode::OK, "Successfully logged in")
        }
        None => {
            (StatusCode::BAD_REQUEST, "User does not exist")
        }
    }
}

async fn acquire_user_from_session<F>(state: AppState, session: Session, callback: F) -> Response
    where F: FnOnce(&Account) -> Response {
    match session.get::<String>("username").await {
        Ok(Some(username)) => {
            let users = state.users.lock().await;
            match users.get(&username) {
                Some(account) => {
                    callback(account)
                }
                None => {
                    let _ = session.remove::<String>("username").await;
                    (StatusCode::UNAUTHORIZED, "unknown account").into_response()
                }
            }
        }
        Ok(None) => {
            (StatusCode::UNAUTHORIZED, "not logged in").into_response()
        }
        Err(_) => {
            (StatusCode::INTERNAL_SERVER_ERROR, "internal server error").into_response()
        }
    }
}

async fn info(extract::State(state): extract::State<AppState>, session: Session) -> Response {
    acquire_user_from_session(state, session, |account| {
        extract::Json(&json!({ "credits": account.credits })).into_response()
    }).await
}

async fn acquire_user_mut_from_session<F>(state: AppState, session: Session, callback: F) -> Response
    where F: FnOnce(&mut Account) -> Response {
    match session.get::<String>("username").await {
        Ok(Some(username)) => {
            let mut users = state.users.lock().await;
            match users.get_mut(&username) {
                Some(account) => {
                    callback(account)
                }
                None => {
                    let _ = session.remove::<String>("username").await;
                    (StatusCode::UNAUTHORIZED, "unknown account").into_response()
                }
            }
        }
        Ok(None) => {
            (StatusCode::UNAUTHORIZED, "not logged in").into_response()
        }
        Err(_) => {
            (StatusCode::INTERNAL_SERVER_ERROR, "internal server error").into_response()
        }
    }
}

const FLAG: &'static str = "UMDCTF{YoU_w1lL_n3Ver_rEaCh_7H3_tRuTh}";

async fn flag(extract::State(state): extract::State<AppState>, session: Session) -> Response {
    acquire_user_mut_from_session(state, session, |account| {
        if account.has_flag {
            return (StatusCode::OK, FLAG).into_response();
        }

        if account.credits < 10_000 {
            return (StatusCode::BAD_REQUEST, "you're too poor").into_response();
        }

        account.credits -= 10_000;
        account.has_flag = true;

        (StatusCode::OK, FLAG).into_response()
    }).await
}

#[derive(Deserialize)]
struct GuessProgrammingLanguage {
    guess: String,
}

async fn guess_pl(extract::State(state): extract::State<AppState>, session: Session, extract::Json(payload): extract::Json<GuessProgrammingLanguage>) -> Response {
    acquire_user_mut_from_session(state, session, |account| {
        if account.redeemed_pl {
            (StatusCode::BAD_REQUEST, "you have already redeemed this reward").into_response()
        } else if payload.guess.to_lowercase() != "rust" {
            (StatusCode::BAD_REQUEST, "incorrect").into_response()
        } else {
            account.redeemed_pl = true;
            account.credits += 69;
            extract::Json(&json!({ "credits": account.credits })).into_response()
        }
    }).await
}

#[derive(Deserialize)]
struct GuessMovie {
    guess: String,
}

async fn guess_movie(extract::State(state): extract::State<AppState>, session: Session, extract::Json(payload): extract::Json<GuessMovie>) -> Response {
    acquire_user_mut_from_session(state, session, |account| {
        if account.redeemed_movie {
            (StatusCode::BAD_REQUEST, "you have already redeemed this reward").into_response()
        } else if payload.guess.to_lowercase() != "dune" {
            (StatusCode::BAD_REQUEST, "incorrect").into_response()
        } else {
            account.redeemed_movie = true;
            account.credits += 420;
            extract::Json(&json!({ "credits": account.credits })).into_response()
        }
    }).await
}

#[derive(Deserialize)]
struct RedeemProxy {
    proxy_url: String,
}

async fn redeem_proxy(extract::State(state): extract::State<AppState>, session: Session, extract::Json(payload): extract::Json<RedeemProxy>) -> Response {
    let users = state.users.clone();

    acquire_user_mut_from_session(state, session, |account| {
        if account.redeemed_proxy {
            return (StatusCode::BAD_REQUEST, "you have already redeemed this reward").into_response();
        }
        if account.currently_redeeming_proxy {
            return (StatusCode::BAD_REQUEST, "you are currently redeeming the reward, wait for it to finish").into_response();
        }

        return match Url::parse(&payload.proxy_url) {
            Ok(proxy_url) => {
                let is_https = match proxy_url.scheme() {
                    "http" => false,
                    "https" => true,
                    _ => return (StatusCode::BAD_REQUEST, "invalid proxy scheme").into_response()
                };
                let proxy_host = match proxy_url.host_str() {
                    Some(host) => host.to_string(),
                    None => return (StatusCode::BAD_REQUEST, "missing host").into_response()
                };
                let proxy_port = match proxy_url.port_or_known_default() {
                    Some(port) => port,
                    None => return (StatusCode::BAD_REQUEST, "missing port").into_response()
                };

                account.currently_redeeming_proxy = true;
                account.proxy_redeem_result = None;

                let username = account.username.clone();
                let original_credits = account.credits;
                tokio::spawn(async move {
                    let mut success = false;
                    let tls_connector = create_tls_connector();
                    for _ in 0..5 {
                        let result = tokio::time::timeout(Duration::from_secs(5), try_proxy(proxy_host.clone(), proxy_port, is_https, &tls_connector, &users, &username, original_credits)).await;
                        if let Ok(Ok(_)) = result {
                            success = true;
                            break;
                        }
                    }

                    let mut refreshed_account = users.lock().await;
                    if let Some(account) = refreshed_account.get_mut(&username) {
                        account.currently_redeeming_proxy = false;
                        account.proxy_redeem_result = Some(success);
                        if success {
                            account.redeemed_proxy = true;
                        }
                    }
                });

                (StatusCode::OK, "please wait").into_response()
            }
            Err(_) => {
                (StatusCode::BAD_REQUEST, "invalid proxy url").into_response()
            }
        };
    }).await
}

fn create_tls_connector() -> TlsConnector {
    let mut root_store = RootCertStore::empty();
    for cert in rustls_native_certs::load_native_certs().expect("Failed to load native certs") {
        root_store.add(cert).expect("Failed to add native cert");
    }

    let mut rustls_config = ClientConfig::builder_with_protocol_versions(&[&rustls::version::TLS13])
        .with_root_certificates(root_store)
        .with_no_client_auth();
    rustls_config.alpn_protocols = vec![b"http/1.1".to_vec()];
    rustls_config.enable_early_data = true;
    TlsConnector::from(Arc::new(rustls_config)).early_data(true)
}

async fn try_proxy(proxy_host: String, proxy_port: u16, is_https: bool, tls_connector: &TlsConnector, users: &Mutex<HashMap<String, Account>>, user: &str, original_credits: i32) -> Result<(), anyhow::Error> {
    let tcp_stream = TcpStream::connect(format!("{}:{}", proxy_host, proxy_port)).await?;
    tcp_stream.set_nodelay(true)?;

    if is_https {
        let tls_stream = tls_connector.connect(ServerName::try_from(proxy_host)?, tcp_stream).await?;
        return Ok(connect_via_stream(tls_stream, tls_connector, users, user, original_credits).await?);
    }

    Ok(connect_via_stream(tcp_stream, tls_connector, users, user, original_credits).await?)
}

const SERVER_SECRET: &'static str = "noBOdY w!1L 9U3$S 7Hi$ s3Cr37 u317rsf79dfsd9f";

async fn connect_via_stream<T>(stream: T, tls_connector: &TlsConnector, users: &Mutex<HashMap<String, Account>>, username: &str, original_credits: i32) -> Result<(), anyhow::Error>
    where T: AsyncRead + AsyncWrite + Unpin + Send + 'static {
    let (mut proxy_sender, proxy_connection) = hyper::client::conn::http1::handshake(TokioIo::new(stream)).await?;
    tokio::spawn(proxy_connection.with_upgrades());

    let connect_request = Request::connect("challs.umdctf.io:31111")
        .header(hyper::header::HOST, "challs.umdctf.io:31111")
        .body(Empty::<Bytes>::new())
        .unwrap();
    let connect_response = proxy_sender.send_request(connect_request).await?;
    if connect_response.status() != StatusCode::OK {
        return Err(anyhow!("Failed to proxy"));
    }

    let upgraded = hyper::upgrade::on(connect_response).await?;
    let tls_stream = tls_connector.connect(ServerName::try_from("challs.umdctf.io").unwrap(), TokioIo::new(upgraded)).await?;

    let (mut sender, connection) = hyper::client::conn::http1::handshake(TokioIo::new(tls_stream))
        .await?;
    tokio::spawn(connection);

    let body = serde_json::to_vec(&json!({
        "username": username,
        "credits": 2000
    }))?;

    let add_credits_request = Request::post("/api/add-credits")
        .header(hyper::header::HOST, "challs.umdctf.io:31111")
        .header(hyper::header::AUTHORIZATION, SERVER_SECRET)
        .header(hyper::header::CONTENT_TYPE, "application/json")
        .body(Full::<Bytes>::new(Bytes::from(body)))?;

    let _ = sender.send_request(add_credits_request).await;

    let users = users.lock().await;
    if let Some(account) = users.get(username) {
        if account.credits <= original_credits {
            return Err(anyhow!("Failed to add credits"));
        }
    }

    Ok(())
}

async fn redeem_proxy_check(extract::State(state): extract::State<AppState>, session: Session) -> Response {
    acquire_user_from_session(state, session, |account| {
        match &account.proxy_redeem_result {
            Some(true) => {
                (StatusCode::OK, "success").into_response()
            }
            Some(false) => {
                (StatusCode::OK, "failure").into_response()
            }
            None => {
                (StatusCode::OK, "pending").into_response()
            }
        }
    }).await
}

#[derive(Deserialize)]
struct AddCredits {
    username: String,
    credits: i32,
}

async fn add_credits(extract::State(state): extract::State<AppState>, headers: HeaderMap, extract::Json(payload): extract::Json<AddCredits>) -> Response {
    if !headers.get(axum::http::header::AUTHORIZATION)
        .map(|value| value == SERVER_SECRET)
        .unwrap_or(false) {
        return (StatusCode::UNAUTHORIZED, "unauthorized").into_response();
    }

    let mut users = state.users.lock().await;
    match users.get_mut(&payload.username) {
        Some(account) => {
            account.credits += payload.credits;
            (StatusCode::OK, "credits added").into_response()
        }
        None => {
            (StatusCode::BAD_REQUEST, "unknown account").into_response()
        }
    }
}

