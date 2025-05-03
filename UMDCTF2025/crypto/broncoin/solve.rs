use ark_bls12_381::Bls12_381 as E;
use ark_bls12_381::Fr as F;
use ark_crypto_primitives::crh::poseidon::CRH;
use ark_crypto_primitives::crh::CRHScheme;
use ark_crypto_primitives::snark::SNARK;
use ark_ff::AdditiveGroup;
use ark_ff::Field;
use ark_groth16::Groth16;
use ark_groth16::ProvingKey;
use ark_relations::r1cs::ConstraintSynthesizer;
use ark_relations::r1cs::ConstraintSystem;
use ark_serialize::CanonicalDeserialize;
use ark_serialize::CanonicalSerialize;
use ark_serialize::Compress;
use ark_serialize::Validate;
use broncoin::hash::gen_poseidon_params;
use broncoin::transact::encrypt_coin_data;
use broncoin::transact::gen_sk_pk;
use broncoin::transact::FlagRequest;
use broncoin::transact::FlagResponse;
use broncoin::transact::SplitCircuit;
use broncoin::transact::Transaction;
use broncoin::transact::TransactionRequest;
use broncoin::transact::TxSplit;
use broncoin::DEPTH;
use broncoin::{
    coin::BronCoin,
    merkle::MerkleTree,
    transact::{Privkey, Pubkey},
};
use rand::thread_rng;
use rand::Rng;
use rand::{CryptoRng, RngCore};

pub fn malicious_split<const N: usize>(
    rng: &mut (impl CryptoRng + RngCore),
    coin: BronCoin,
    secret_key: Privkey,
    pubkey1: Pubkey,
    pubkey2: Pubkey,
    value1: F,
    value2: F,
    tree: MerkleTree<N>,
    proving_key: ProvingKey<E>,
) -> (BronCoin, BronCoin, TxSplit) {
    let commitment = coin.commit();

    let (mut path, r) = tree.construct_merkle_path(0);

    let out_val = CRH::evaluate(
        &gen_poseidon_params(2, false),
        [
            tree.elements.get(0).unwrap_or(&F::ZERO).clone(),
            tree.elements.get(1).unwrap_or(&F::ZERO).clone(),
        ],
    )
    .unwrap();

    let v0 = out_val
        - CRH::evaluate(&gen_poseidon_params(2, false), [commitment, path.list[0].0]).unwrap();

    let v1 = -CRH::evaluate(&gen_poseidon_params(2, false), [commitment, path.list[0].0]).unwrap()
        + CRH::evaluate(&gen_poseidon_params(2, false), [path.list[0].0, commitment]).unwrap();

    let a = v0 * v1.inverse().unwrap();

    path.list[0].1 = a;
    path.val = commitment;

    let sn = CRH::evaluate(
        &gen_poseidon_params(2, false),
        [F::ONE, secret_key.sk, coin.pre_sn],
    )
    .unwrap();

    let coin1 = BronCoin {
        addr: pubkey1.addr,
        value: value1,
        pre_sn: rng.gen(),
        rand: (rng.gen(), rng.gen()),
    };

    let coin2 = BronCoin {
        addr: pubkey2.addr,
        value: value2,
        pre_sn: rng.gen(),
        rand: (rng.gen(), rng.gen()),
    };

    let e0 = encrypt_coin_data(rng, coin1.clone(), pubkey1);
    let e1 = encrypt_coin_data(rng, coin2.clone(), pubkey2);

    let com1 = coin1.commit();
    let com2 = coin2.commit();

    let circ = SplitCircuit {
        root: r,
        sn,
        com1,
        com2,

        path,
        coin,
        split1: coin1.clone(),
        split2: coin2.clone(),
        secret_key: secret_key.sk,
    };

    let new_cs = ConstraintSystem::<F>::new_ref();
    circ.clone().generate_constraints(new_cs.clone()).unwrap();
    new_cs.is_satisfied().unwrap();

    let proof = Groth16::<E>::prove(&proving_key, circ, rng).unwrap();

    let tx = TxSplit {
        root: r,
        sn,
        com1,
        com2,
        proof,
        data: (e0, e1),
    };

    (coin1, coin2, tx)
}

fn main() {
    let server: String = "https://lecoin.challs.umdctf.io".to_string();

    let addr_ser: Vec<u8> = reqwest::blocking::get(format!("{}/bron/account", server))
        .unwrap()
        .bytes()
        .unwrap()
        .into();

    let bron_addr =
        Pubkey::deserialize_with_mode(addr_ser.as_slice(), Compress::No, Validate::No).unwrap();

    let (sk, pk) = gen_sk_pk(&mut thread_rng());

    let pk_ser: Vec<u8> = reqwest::blocking::get(format!("{}/api/proving_key", server))
        .unwrap()
        .bytes()
        .unwrap()
        .into();

    let proving_key: ProvingKey<E> =
        ProvingKey::deserialize_with_mode(pk_ser.as_slice(), Compress::No, Validate::No).unwrap();

    let tree: Vec<u8> = reqwest::blocking::get(format!("{}/api/tree", server))
        .unwrap()
        .bytes()
        .unwrap()
        .into();

    let tree =
        MerkleTree::<DEPTH>::deserialize_with_mode(tree.as_slice(), Compress::No, Validate::No)
            .unwrap();

    let fake_coin = BronCoin {
        addr: pk.addr,
        value: F::from(5000),
        pre_sn: F::from(87687),
        rand: (F::from(33), F::from(34)),
    };

    let (c0, c1, tx) = malicious_split(
        &mut thread_rng(),
        fake_coin,
        sk,
        bron_addr,
        pk,
        F::from(5000),
        F::ZERO,
        tree,
        proving_key,
    );

    let t = Transaction {
        mz: None,
        s: Some(tx),
    };

    let mut buf = Vec::new();
    t.serialize_with_mode(&mut buf, Compress::No).unwrap();

    let request = TransactionRequest { transaction: buf };
    let client = reqwest::blocking::Client::new();
    let response = client
        .post(format!("{}/api/transact", server))
        .json(&request)
        .send()
        .unwrap();

    if response.status().is_success() {
        println!("Woag it works");

        let mut buf = Vec::new();
        c0.serialize_with_mode(&mut buf, Compress::No).unwrap();

        let request = FlagRequest { coin: buf };
        let client = reqwest::blocking::Client::new();
        let response = client
            .post(format!("{}/bron/query", server))
            .json(&request)
            .send()
            .unwrap();

        println!("{:?}", response.json::<FlagResponse>());
    } else {
        println!("An error occurred.");
        return;
    }
}
