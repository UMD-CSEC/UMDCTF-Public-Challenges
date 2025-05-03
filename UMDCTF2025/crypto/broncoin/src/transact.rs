use crate::coin::BronCoinVar;
use crate::merkle::{PathProof, PathProofVar};
use crate::{coin::BronCoin, hash::gen_poseidon_params, merkle::MerkleTree};
use ark_bls12_381::Bls12_381 as E;
use ark_bls12_381::Fr as F;
use ark_bls12_381::G1Projective as G;
use ark_crypto_primitives::crh::{poseidon, CRHSchemeGadget};
use ark_crypto_primitives::crh::{poseidon::CRH, CRHScheme};
use ark_crypto_primitives::snark::SNARK;
use ark_crypto_primitives::sponge::poseidon::PoseidonConfig;
use ark_ec::PrimeGroup;
use ark_ff::{AdditiveGroup, BigInteger, Field, PrimeField};
use ark_groth16::data_structures::Proof;
use ark_groth16::{Groth16, ProvingKey, VerifyingKey};
use ark_r1cs_std::alloc::AllocVar;
use ark_r1cs_std::eq::EqGadget;
use ark_r1cs_std::fields::fp::FpVar;
use ark_r1cs_std::prelude::Boolean;
use ark_relations::ns;
use ark_relations::r1cs::{ConstraintSynthesizer, ConstraintSystemRef};
use ark_relations::r1cs::{ConstraintSystem, Result as ArkResult};
use ark_serialize::{CanonicalDeserialize, CanonicalSerialize, Compress, Validate};
use rand::{CryptoRng, Rng, RngCore};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TransactionRequest {
    pub transaction: Vec<u8>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FlagRequest {
    pub coin: Vec<u8>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FlagResponse {
    pub flag: String,
}

#[derive(Clone, Debug, CanonicalSerialize, CanonicalDeserialize)]
pub struct Transaction {
    pub mz: Option<TxMint>,
    pub s: Option<TxSplit>,
}

#[derive(Clone, Debug, CanonicalSerialize, CanonicalDeserialize)]
pub struct Pubkey {
    pub addr: F,
    pub key: G,
}

#[derive(Clone, Debug, CanonicalSerialize, CanonicalDeserialize)]
pub struct Privkey {
    pub sk: F,
    pub s: F,
}

#[derive(Clone, Debug, CanonicalSerialize, CanonicalDeserialize)]
pub struct EncCoin {
    pub value: (G, F),
    pub pre_sn: (G, F),
    pub rand_0: (G, F),
    pub rand_1: (G, F),
}

pub fn gen_sk_pk(rng: &mut (impl CryptoRng + RngCore)) -> (Privkey, Pubkey) {
    let sk = rng.gen();
    let vec = vec![F::ONE + F::ONE, sk, F::ZERO];
    let addr = CRH::evaluate(&gen_poseidon_params(2, false), vec).unwrap();

    let s = rng.gen();

    let key = G::generator() * s;

    (Privkey { sk, s }, Pubkey { addr, key })
}

pub fn encrypt_coin_data(rng: &mut (impl CryptoRng + RngCore), c: BronCoin, k: Pubkey) -> EncCoin {
    fn egm_enc(rng: &mut (impl CryptoRng + RngCore), v: F, key: G) -> (G, F) {
        let mut ser = Vec::new();
        key.serialize_with_mode(&mut ser, Compress::No).unwrap();
        let key = G::deserialize_with_mode(ser.as_slice(), Compress::No, Validate::No).unwrap();

        let rand: F = rng.gen();
        let gen = G::generator();

        let nonce = gen * rand;

        let mut ser = Vec::new();
        nonce.serialize_with_mode(&mut ser, Compress::No).unwrap();
        let nonce = G::deserialize_with_mode(ser.as_slice(), Compress::No, Validate::No).unwrap();

        let blinded_key = key * rand;

        let mut ser = Vec::new();
        blinded_key
            .serialize_with_mode(&mut ser, Compress::No)
            .unwrap();
        let blinded_key =
            G::deserialize_with_mode(ser.as_slice(), Compress::No, Validate::No).unwrap();

        let bits = blinded_key.x.into_bigint().to_bits_le();
        let x = F::from_bigint(<F as PrimeField>::BigInt::from_bits_le(&bits[0..128])).unwrap();

        let enc = v + CRH::evaluate(&gen_poseidon_params(2, false), [x]).unwrap();
        (nonce, enc)
    }
    let value = egm_enc(rng, c.value, k.key);
    let pre_sn = egm_enc(rng, c.pre_sn, k.key);
    let rand_0 = egm_enc(rng, c.rand.0, k.key);
    let rand_1 = egm_enc(rng, c.rand.1, k.key);

    EncCoin {
        value,
        pre_sn,
        rand_0,
        rand_1,
    }
}

pub fn decrypt_and_check(com: F, data: EncCoin, key: Privkey) -> Option<BronCoin> {
    fn egm_dec(ct: (G, F), key: F) -> F {
        let blinded_key = ct.0 * key;

        let mut ser = Vec::new();
        blinded_key
            .serialize_with_mode(&mut ser, Compress::No)
            .unwrap();
        let blinded_key =
            G::deserialize_with_mode(ser.as_slice(), Compress::No, Validate::No).unwrap();

        let bits = blinded_key.x.into_bigint().to_bits_le();
        let x = F::from_bigint(<F as PrimeField>::BigInt::from_bits_le(&bits[0..128])).unwrap();
        let dec = ct.1 - CRH::evaluate(&gen_poseidon_params(2, false), [x]).unwrap();
        dec
    }

    let b = BronCoin {
        addr: CRH::evaluate(
            &gen_poseidon_params(2, false),
            [F::ONE + F::ONE, key.sk, F::ZERO],
        )
        .unwrap(),
        value: egm_dec(data.value, key.s),
        pre_sn: egm_dec(data.pre_sn, key.s),
        rand: (egm_dec(data.rand_0, key.s), egm_dec(data.rand_1, key.s)),
    };

    if b.commit() == com {
        Some(b)
    } else {
        None
    }
}

#[derive(Debug, Clone, PartialEq, Eq, CanonicalSerialize, CanonicalDeserialize)]
pub struct TxMint {
    pub value: F,
    pub addr_com: F,
    pub rand: F,
    pub com: F,
}

pub fn mint(value: F, rng: &mut (impl CryptoRng + RngCore), pubkey: Pubkey) -> (BronCoin, TxMint) {
    let coin = BronCoin {
        addr: pubkey.addr,
        value,
        pre_sn: rng.gen(),
        rand: (rng.gen(), rng.gen()),
    };

    let inps = vec![pubkey.addr, coin.pre_sn, coin.rand.0];

    let addr_com = CRH::evaluate(&gen_poseidon_params(2, false), inps).unwrap();

    let tx = TxMint {
        value,
        addr_com,
        rand: coin.rand.1,
        com: coin.commit(),
    };

    (coin, tx)
}

pub fn verify_mint(tx: &TxMint) -> bool {
    let vals = vec![tx.value, tx.addr_com, tx.rand];
    let com = CRH::evaluate(&gen_poseidon_params(2, false), vals).unwrap();
    com == tx.com
}

#[derive(Clone, Debug, CanonicalDeserialize, CanonicalSerialize)]
pub struct TxSplit {
    pub root: F,
    pub sn: F,
    pub com1: F,
    pub com2: F,
    pub proof: Proof<E>,
    pub data: (EncCoin, EncCoin),
}

fn get_merkle_proof<const N: usize>(tree: MerkleTree<N>, element: F) -> (PathProof<N>, F) {
    tree.construct_merkle_path(tree.find_element(element))
}

pub fn split<const N: usize>(
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
    let (path, r) = get_merkle_proof(tree, coin.commit());

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

#[derive(Clone, Default)]
pub struct SplitCircuit<const N: usize> {
    // public
    pub root: F,
    pub sn: F,
    pub com1: F,
    pub com2: F,

    // private
    pub path: PathProof<N>,
    pub coin: BronCoin,
    pub split1: BronCoin,
    pub split2: BronCoin,
    pub secret_key: F,
}

impl<const N: usize> ConstraintSynthesizer<F> for SplitCircuit<N> {
    fn generate_constraints(self, cs: ConstraintSystemRef<F>) -> ArkResult<()> {
        let root = FpVar::<F>::new_input(ns!(cs, "root"), || Ok(self.root))?;
        let sn = FpVar::<F>::new_input(ns!(cs, "sn"), || Ok(self.sn))?;
        let com1 = FpVar::<F>::new_input(ns!(cs, "com1"), || Ok(self.com1))?;
        let com2 = FpVar::<F>::new_input(ns!(cs, "com2"), || Ok(self.com2))?;

        let path = PathProofVar::new_witness(ns!(cs, "path"), || Ok(&self.path))?;
        let coin = BronCoinVar::new_witness(ns!(cs, "coin"), || Ok(&self.coin))?;
        let split1 = BronCoinVar::new_witness(ns!(cs, "split1"), || Ok(&self.split1))?;
        let split2 = BronCoinVar::new_witness(ns!(cs, "split2"), || Ok(&self.split2))?;
        let secret_key = FpVar::<F>::new_witness(ns!(cs, "secret_key"), || Ok(&self.secret_key))?;

        let params: PoseidonConfig<F> = gen_poseidon_params(2, false);
        let params_var = poseidon::constraints::CRHParametersVar { parameters: params };

        let com = coin.commit()?;
        path.val.enforce_equal(&com)?;
        path.verify_path(root)?.enforce_equal(&Boolean::TRUE)?;

        let c1 = split1.commit()?;
        com1.enforce_equal(&c1)?;

        let c2 = split2.commit()?;
        com2.enforce_equal(&c2)?;

        coin.addr
            .enforce_equal(&poseidon::constraints::CRHGadget::evaluate(
                &params_var,
                &[
                    FpVar::Constant(F::ONE + F::ONE),
                    secret_key.clone(),
                    FpVar::Constant(F::ZERO),
                ],
            )?)?;

        sn.enforce_equal(&poseidon::constraints::CRHGadget::evaluate(
            &params_var,
            &[FpVar::Constant(F::ONE), secret_key, coin.pre_sn],
        )?)?;

        (split1.value + split2.value).enforce_equal(&coin.value)?;

        Ok(())
    }
}

pub fn verify_split(
    cur_root: F,
    prior_sns: Vec<F>,
    verif_key: VerifyingKey<E>,
    tx: &TxSplit,
) -> bool {
    let b1 = cur_root == tx.root;
    let b2 = !(prior_sns.contains(&tx.sn));

    let inputs = vec![tx.root, tx.sn, tx.com1, tx.com2];

    let out = Groth16::<E>::verify(&verif_key, &inputs, &tx.proof).unwrap();

    b1 & b2 & out
}
