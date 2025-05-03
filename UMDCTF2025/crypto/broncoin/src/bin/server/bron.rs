use std::{
    fs,
    sync::{Arc, RwLock},
};

use ark_bls12_381::Fr as F;
use ark_serialize::{CanonicalDeserialize, CanonicalSerialize, Compress, Validate};
use axum::{body::Bytes, extract::State, response::ErrorResponse, Json};
use broncoin::{
    coin::BronCoin,
    transact::{FlagRequest, FlagResponse},
};

use crate::{api::throw_err, ServerState};

pub async fn handle_query_bron(
    State(state): State<Arc<RwLock<ServerState>>>,
    Json(payload): Json<FlagRequest>,
) -> Result<Json<FlagResponse>, ErrorResponse> {
    let coin =
        BronCoin::deserialize_with_mode(payload.coin.as_slice(), Compress::No, Validate::Yes)
            .map_err(|_| throw_err())?;

    let com = coin.commit();

    let valid_coin = state.read().unwrap().tree.is_in(com);

    let bron_addr = state.read().unwrap().bron_account.1.clone();

    let response = if valid_coin && coin.value >= F::from(500) && coin.addr == bron_addr.addr {
        FlagResponse {
            flag: fs::read_to_string("flag.txt").map_err(|_| throw_err())?,
        }
    } else {
        FlagResponse {
            flag: "Not enough money buddy".to_string(),
        }
    };

    Ok(Json(response))
}

pub async fn handle_account_bron(
    State(state): State<Arc<RwLock<ServerState>>>,
) -> Result<Bytes, ErrorResponse> {
    let mut keybuf: Vec<u8> = Vec::new();
    state
        .read()
        .unwrap()
        .bron_account
        .1
        .serialize_with_mode(&mut keybuf, Compress::No)
        .map_err(|_| throw_err())?;
    Ok(keybuf.into())
}
