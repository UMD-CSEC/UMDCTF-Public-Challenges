use std::sync::{Arc, RwLock};

use ark_bls12_381::Fr as F;
use ark_ff::AdditiveGroup;
use ark_serialize::{CanonicalDeserialize, CanonicalSerialize, Compress, Validate};
use axum::{body::Bytes, extract::State, http::StatusCode, response::ErrorResponse, Json};
use broncoin::transact::{verify_mint, verify_split, Transaction, TransactionRequest};

use crate::ServerState;

pub fn throw_err() -> ErrorResponse {
    ErrorResponse::from((StatusCode::INTERNAL_SERVER_ERROR, "Something went wrong."))
}

pub async fn handle_get_pk(
    State(state): State<Arc<RwLock<ServerState>>>,
) -> Result<Bytes, ErrorResponse> {
    println!("Get pk");
    let mut keybuf: Vec<u8> = Vec::new();
    state
        .read()
        .unwrap()
        .proving_key
        .serialize_with_mode(&mut keybuf, Compress::No)
        .map_err(|_| throw_err())?;
    Ok(keybuf.into())
}

pub async fn handle_get_vk(
    State(state): State<Arc<RwLock<ServerState>>>,
) -> Result<Bytes, ErrorResponse> {
    println!("Get vk");
    let mut keybuf: Vec<u8> = Vec::new();
    state
        .read()
        .unwrap()
        .verif_key
        .serialize_with_mode(&mut keybuf, Compress::No)
        .map_err(|_| throw_err())?;
    Ok(keybuf.into())
}

pub async fn handle_get_tree(
    State(state): State<Arc<RwLock<ServerState>>>,
) -> Result<Bytes, ErrorResponse> {
    println!("Get tree");
    let mut keybuf: Vec<u8> = Vec::new();
    state
        .read()
        .unwrap()
        .tree
        .serialize_with_mode(&mut keybuf, Compress::No)
        .map_err(|_| throw_err())?;

    Ok(keybuf.into())
}

pub async fn handle_get_root(
    State(state): State<Arc<RwLock<ServerState>>>,
) -> Result<Bytes, ErrorResponse> {
    println!("Get root");
    let mut keybuf: Vec<u8> = Vec::new();
    state
        .read()
        .unwrap()
        .tree
        .get_root()
        .serialize_with_mode(&mut keybuf, Compress::No)
        .map_err(|_| throw_err())?;
    Ok(keybuf.into())
}

pub async fn handle_get_tx(
    State(state): State<Arc<RwLock<ServerState>>>,
) -> Result<Bytes, ErrorResponse> {
    println!("Get txs");
    let mut keybuf: Vec<u8> = Vec::new();
    state
        .read()
        .unwrap()
        .tx
        .serialize_with_mode(&mut keybuf, Compress::No)
        .map_err(|_| throw_err())?;

    Ok(keybuf.into())
}

pub async fn handle_transact(
    State(state): State<Arc<RwLock<ServerState>>>,
    Json(payload): Json<TransactionRequest>,
) -> Result<(), ErrorResponse> {
    let t = Transaction::deserialize_with_mode(
        payload.transaction.as_slice(),
        Compress::No,
        Validate::Yes,
    )
    .map_err(|_| throw_err())?;

    let tp = match (t.mz.clone(), t.s.clone()) {
        (None, None) => Err(throw_err()),
        (Some(_), Some(_)) => Err(throw_err()),
        _ => Ok(t),
    }?;

    if let Some(mint) = tp.mz.clone() {
        println!("Mint");
        if verify_mint(&mint) && mint.value == F::ZERO {
            state.write().unwrap().tree.append(mint.com);
            state.write().unwrap().tx.push(tp.clone());
            return Ok(());
        }
    }

    if let Some(split) = tp.s.clone() {
        println!("Split");
        let tree = state.read().unwrap().tree.clone();
        let root = tree.get_root();
        let prior_sns = state.read().unwrap().sns.clone();
        let verif_key = state.read().unwrap().verif_key.clone();
        if verify_split(root, prior_sns, verif_key, &split) {
            state.write().unwrap().tree.append(split.com1);
            state.write().unwrap().tree.append(split.com2);
            state.write().unwrap().sns.push(split.sn);
            state.write().unwrap().tx.push(tp.clone());
            return Ok(());
        }
    }

    Err(throw_err())
}
