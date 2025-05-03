use crate::user::{User, UserDatabase};
use bytes::Bytes;
use http::StatusCode;
use serde::Deserialize;
use serde_json::json;
use std::sync::atomic::Ordering;
use std::sync::Arc;

const REDEMPTION_CODE: &'static str =
    "eW91IHRoaW5rIHlvdSdyZSBzcGVjaWFsIGJlY2F1c2UgeW91IGtub3cgaG93IHRvIGRlY29kZSBiYXNlNjQ/";

const INDEX_HTML: &'static str = include_str!("index.html");

const LETSGO_MP3: &'static [u8] = include_bytes!("letsgo.mp3");

const DANGIT_MP3: &'static [u8] = include_bytes!("dangit.mp3");

pub struct Router {
    database: Arc<UserDatabase>,
    flag: String,
}

impl Router {
    pub fn new(flag: String, database: Arc<UserDatabase>) -> Self {
        Self { database, flag }
    }

    async fn check_valid_user(
        &self,
        quic_conn: &quinn::Connection,
        req: &http::Request<()>,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<Option<Arc<User>>, h3::Error> {
        #[derive(Deserialize)]
        struct AuthorizationHeader {
            username: String,
            password: String,
        }

        let user_opt = req
            .headers()
            .get(http::header::AUTHORIZATION)
            .and_then(|value| serde_json::from_slice::<AuthorizationHeader>(value.as_bytes()).ok())
            .and_then(|parsed_header| {
                self.database
                    .find_user(&parsed_header.username, &parsed_header.password)
            });
        let Some(user) = user_opt else {
            crate::h3_util::send_response(stream, StatusCode::UNAUTHORIZED).await?;
            crate::h3_util::send_body(stream, "invalid username + password").await?;
            return Ok(None);
        };

        if user.signup_ip != quic_conn.remote_address().ip() {
            crate::h3_util::send_response(stream, StatusCode::FORBIDDEN).await?;
            let warning = format!(
                "Please use the IP address that you signed up with ({}).",
                user.signup_ip
            );
            crate::h3_util::send_body(stream, warning).await?;
            return Ok(None);
        }

        Ok(Some(user))
    }

    pub async fn index(
        &self,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        crate::h3_util::send_response(stream, StatusCode::OK).await?;
        crate::h3_util::send_body(stream, INDEX_HTML).await?;
        Ok(())
    }

    pub async fn letsgo(
        &self,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        let response = http::Response::builder()
            .status(StatusCode::OK)
            .header(http::header::CONTENT_TYPE, "audio/mpeg")
            .body(())
            .unwrap();
        stream.send_response(response).await?;
        crate::h3_util::send_body(stream, LETSGO_MP3).await?;
        Ok(())
    }

    pub async fn dangit(
        &self,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        let response = http::Response::builder()
            .status(StatusCode::OK)
            .header(http::header::CONTENT_TYPE, "audio/mpeg")
            .body(())
            .unwrap();
        stream.send_response(response).await?;
        crate::h3_util::send_body(stream, DANGIT_MP3).await?;
        Ok(())
    }

    pub async fn register(
        &self,
        quic_conn: &quinn::Connection,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        #[derive(Deserialize)]
        struct RegisterPayload {
            username: String,
            password: String,
        }
        let Some(payload) = crate::h3_util::read_payload::<RegisterPayload>(stream).await? else {
            return Ok(());
        };

        if payload.username.len() < 8 || payload.password.len() < 8 {
            crate::h3_util::send_response(stream, StatusCode::FORBIDDEN).await?;
            crate::h3_util::send_body(stream, "username and password must be at least 8 characters").await?;
            return Ok(());
        }

        let user = User::new(
            payload.username.to_owned(),
            payload.password.to_owned(),
            quic_conn.remote_address().ip(),
        );
        if self.database.create_user(user) {
            crate::h3_util::send_response(stream, StatusCode::CREATED).await?;
        } else {
            crate::h3_util::send_response(stream, StatusCode::FORBIDDEN).await?;
            crate::h3_util::send_body(stream, "this user already exists").await?;
        }

        Ok(())
    }

    pub async fn login(
        &self,
        quic_conn: &quinn::Connection,
        req: &http::Request<()>,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        if self.check_valid_user(quic_conn, req, stream).await?.is_some() {
            crate::h3_util::send_response(stream, StatusCode::NO_CONTENT).await?;
        }

        Ok(())
    }

    pub async fn redeem_code(
        &self,
        quic_conn: &quinn::Connection,
        req: &http::Request<()>,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        let Some(user) = self.check_valid_user(quic_conn, req, stream).await? else {
            return Ok(());
        };
        let Some(payload) = crate::h3_util::read_payload::<String>(stream).await? else {
            return Ok(());
        };

        if payload != REDEMPTION_CODE {
            crate::h3_util::send_response(stream, StatusCode::BAD_REQUEST).await?;
            crate::h3_util::send_body(stream, "invalid code").await?;
            return Ok(());
        }

        if user.test_ratelimited(quic_conn.remote_address().ip()) {
            crate::h3_util::send_response(stream, StatusCode::TOO_MANY_REQUESTS).await?;
            crate::h3_util::send_body(stream, "a high number of requests are coming from your device. you are ratelimited").await?;
            return Ok(());
        }

        user.credits.fetch_add(100, Ordering::SeqCst);
        crate::h3_util::send_response(stream, StatusCode::NO_CONTENT).await?;

        Ok(())
    }

    pub async fn credits(
        &self,
        quic_conn: &quinn::Connection,
        req: &http::Request<()>,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        let Some(user) = self.check_valid_user(quic_conn, req, stream).await? else {
            return Ok(());
        };

        let response = http::Response::builder()
            .status(StatusCode::OK)
            .header(http::header::CONTENT_TYPE, "application/json")
            .body(())
            .unwrap();
        stream.send_response(response).await?;
        crate::h3_util::send_body(
            stream,
            json!(user.credits.load(Ordering::SeqCst)).to_string(),
        )
        .await?;
        Ok(())
    }

    pub async fn wager(
        &self,
        quic_conn: &quinn::Connection,
        req: &http::Request<()>,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        let Some(user) = self.check_valid_user(quic_conn, req, stream).await? else {
            return Ok(());
        };
        let Some(payload) = crate::h3_util::read_payload::<i32>(stream).await? else {
            return Ok(());
        };

        if payload < 0 {
            crate::h3_util::send_response(stream, StatusCode::BAD_REQUEST).await?;
            crate::h3_util::send_body(stream, "you can't wager negative credits").await?;
            return Ok(());
        }
        if payload > 100 {
            crate::h3_util::send_response(stream, StatusCode::BAD_REQUEST).await?;
            crate::h3_util::send_body(stream, "that's too much").await?;
            return Ok(());
        }

        if user.use_credits(payload, true) {
            crate::h3_util::send_response(stream, StatusCode::NO_CONTENT).await?;
        } else {
            crate::h3_util::send_response(stream, StatusCode::BAD_REQUEST).await?;
            crate::h3_util::send_body(stream, "you went bankrupt :/").await?;
        }

        Ok(())
    }

    pub async fn flag(
        &self,
        quic_conn: &quinn::Connection,
        req: &http::Request<()>,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        let Some(user) = self.check_valid_user(quic_conn, req, stream).await? else {
            return Ok(());
        };

        if user.use_credits(300, false) {
            crate::h3_util::send_response(stream, StatusCode::OK).await?;
            crate::h3_util::send_body(stream, self.flag.clone()).await?;
        } else {
            crate::h3_util::send_response(stream, StatusCode::FORBIDDEN).await?;
            crate::h3_util::send_body(stream, "not enough credits").await?;
        }

        Ok(())
    }

    pub async fn not_found(
        &self,
        stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    ) -> Result<(), h3::Error> {
        crate::h3_util::send_response(stream, StatusCode::NOT_FOUND).await?;
        Ok(())
    }
}
