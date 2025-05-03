pub mod api;
pub mod bron;

use api::{
    handle_get_pk, handle_get_root, handle_get_tree, handle_get_tx, handle_get_vk, handle_transact,
};
use ark_bls12_381::Bls12_381 as E;
use ark_bls12_381::Fr as F;
use ark_crypto_primitives::snark::SNARK;
use ark_groth16::{Groth16, ProvingKey, VerifyingKey};
use axum::{
    response::{Html, IntoResponse},
    routing::{get, post},
    Router,
};
use bron::{handle_account_bron, handle_query_bron};
use broncoin::{
    merkle::MerkleTree,
    transact::{gen_sk_pk, Privkey, Pubkey, SplitCircuit, Transaction},
    DEPTH,
};
use rand::thread_rng;
use std::{
    error::Error,
    fs,
    sync::{Arc, RwLock},
};

pub struct ServerState {
    pub tree: MerkleTree<DEPTH>,
    pub tx: Vec<Transaction>,
    pub sns: Vec<F>,
    pub proving_key: ProvingKey<E>,
    pub verif_key: VerifyingKey<E>,

    pub bron_account: (Privkey, Pubkey),

    pub stripe_client: (),

    pub domain: String,
}

async fn root() -> impl IntoResponse {
    match fs::read_to_string("front.html") {
        Ok(content) => Html(content),
        Err(e) => Html(format!("Error : {}", e)),
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let mut rng = thread_rng();

    let domain = "http://0.0.0.0:3000";

    let split_circ = SplitCircuit::<DEPTH>::default();

    let (proving_key, verif_key) = Groth16::<E>::circuit_specific_setup(split_circ, &mut rng)?;

    println!("Key generation done.");

    // let secret_key = env::var("STRIPE_SECRET_KEY").expect("Missing STRIPE_SECRET_KEY");

    let state = ServerState {
        tree: MerkleTree::new_from_elements(vec![]),
        tx: vec![],
        sns: vec![],
        proving_key,
        verif_key,
        bron_account: gen_sk_pk(&mut rng),

        stripe_client: (),

        domain: domain.to_string(),
    };

    let state_lock = Arc::new(RwLock::new(state));

    let app = Router::new()
        .route("/", get(root))
        .route("/api/proving_key", get(handle_get_pk))
        .route("/api/verif_key", get(handle_get_vk))
        .route("/api/tree", get(handle_get_tree))
        .route("/api/root", get(handle_get_root))
        .route("/api/tx", get(handle_get_tx))
        .route("/api/transact", post(handle_transact))
        .route("/bron/account", get(handle_account_bron))
        .route("/bron/query", post(handle_query_bron))
        .with_state(state_lock);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    axum::serve(listener, app).await.unwrap();

    Ok(())
}
