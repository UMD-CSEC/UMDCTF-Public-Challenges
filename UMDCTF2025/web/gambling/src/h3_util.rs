use bytes::{Buf, Bytes};
use http::StatusCode;
use serde::de::DeserializeOwned;

pub async fn send_response(
    stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    status_code: StatusCode,
) -> Result<(), h3::Error> {
    let response = http::Response::builder()
        .status(status_code)
        .body(())
        .unwrap();
    stream.send_response(response).await?;

    Ok(())
}

pub async fn send_body<B>(
    stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
    body: B,
) -> Result<(), h3::Error>
where
    Bytes: From<B>,
{
    let wrapped_body = Bytes::from(body);
    stream.send_data(wrapped_body).await?;
    Ok(())
}

pub async fn read_payload<T>(
    stream: &mut h3::server::RequestStream<h3_quinn::BidiStream<Bytes>, Bytes>,
) -> Result<Option<T>, h3::Error>
where
    T: DeserializeOwned,
{
    let mut body = Vec::new();
    while let Some(buf) = stream.recv_data().await? {
        body.extend_from_slice(buf.chunk());
    }

    let Ok(payload) = serde_json::from_slice::<T>(&body) else {
        send_response(stream, StatusCode::BAD_REQUEST).await?;
        return Ok(None);
    };

    Ok(Some(payload))
}