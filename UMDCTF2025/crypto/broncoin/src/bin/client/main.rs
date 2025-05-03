use ark_groth16::ProvingKey;
use base64::{engine::general_purpose, Engine as _};

use std::{
    fs::File,
    io::{Read, Write},
};

use ark_bls12_381::Bls12_381 as E;
use ark_bls12_381::Fr as F;
use ark_ff::{AdditiveGroup, PrimeField};
use ark_serialize::{CanonicalDeserialize, CanonicalSerialize, Compress, Validate};
use broncoin::{
    coin::BronCoin,
    merkle::MerkleTree,
    transact::{
        decrypt_and_check, gen_sk_pk, mint, split, Privkey, Pubkey, Transaction, TransactionRequest,
    },
    DEPTH,
};
use clap::{Parser, Subcommand};
use rand::thread_rng;
use std::str::FromStr;

#[derive(CanonicalSerialize, CanonicalDeserialize)]
pub struct DataFile {
    sk: Privkey,
    pk: Pubkey,
    txs: Vec<Transaction>,
    coins: Vec<BronCoin>,
    scan_index: usize,
    total_value: u64,
    proving_key: ProvingKey<E>,
}

#[derive(Parser, Debug)]
#[command(version, about, long_about = "welcome to lecoin")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Debug, Subcommand)]
enum Commands {
    /// Create an account
    Create,

    /// Mint a zero coin
    Mint {
        #[arg(long, short)]
        val: u32,
    },

    /// Pay to another person.
    Pay {
        /// The address, encoded with base64.
        #[arg(long)]
        addr: String,

        /// The amount to pay.
        #[arg(long)]
        val: String,
    },

    /// Scan amounts to refresh amount of money.
    Scan,
}

fn read_df() -> DataFile {
    let mut f = File::open("wallet").unwrap();
    let mut data: Vec<u8> = Vec::new();
    f.read_to_end(&mut data).unwrap();
    drop(f);
    let df = DataFile::deserialize_with_mode(data.as_slice(), Compress::No, Validate::Yes).unwrap();
    df
}

fn write_df(df: DataFile) {
    let mut f = File::create("wallet").unwrap();
    let mut data: Vec<u8> = Vec::new();
    df.serialize_with_mode(&mut data, Compress::No).unwrap();
    f.write_all(&data).unwrap();
}

fn main() {
    let server: String = "https://lecoin.challs.umdctf.io".to_string();

    let cli = Cli::parse();

    match cli.command {
        Commands::Create => {
            let (sk, pk) = gen_sk_pk(&mut thread_rng());

            let pk_ser: Vec<u8> = reqwest::blocking::get(format!("{}/api/proving_key", server))
                .unwrap()
                .bytes()
                .unwrap()
                .into();

            let proving_key =
                ProvingKey::deserialize_with_mode(pk_ser.as_slice(), Compress::No, Validate::No)
                    .unwrap();
            let df = DataFile {
                sk,
                pk: pk.clone(),
                txs: vec![],
                coins: vec![],
                scan_index: 0,
                total_value: 0,
                proving_key,
            };
            write_df(df);

            let mut buf = Vec::new();
            pk.serialize_with_mode(&mut buf, Compress::No).unwrap();

            println!("pubkey: {}", general_purpose::STANDARD.encode(&buf));
        }
        Commands::Mint { val } => {
            let mut df = read_df();
            let (coin, tx) = mint(F::from(val), &mut thread_rng(), df.pk.clone());

            let t = Transaction {
                mz: Some(tx),
                s: None,
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
                df.txs.push(t);
                df.coins.push(coin);
                df.total_value += val as u64;
                println!("You have {} coins now.", df.total_value);
                write_df(df);
            } else {
                println!("An error occurred.");
            }
        }
        Commands::Pay { addr, val } => {
            let value = val;
            let bytes = general_purpose::STANDARD.decode(&addr).unwrap();

            let pk = Pubkey::deserialize_with_mode(bytes.as_slice(), Compress::No, Validate::No)
                .unwrap();

            let mut rng = thread_rng();
            let v = F::from_str(&value).unwrap();
            let mut df = read_df();
            println!("You have {} coins before payment.", df.total_value);
            if F::from(df.total_value) < v {
                println!("Error: insufficient funds. ");
            } else {
                let mut coins = vec![];
                let mut t = F::ZERO;
                let mut i = 0;

                let mut left = F::ZERO;

                while t < v {
                    if df.coins[i].value != F::ZERO {
                        coins.push(df.coins[i].clone());
                        t += df.coins[i].value;
                        if t > v {
                            left = df.coins[i].value - (t - v);
                        }
                    }
                    i += 1;
                }

                if coins.len() == 0 {
                    println!("Just say you're broke.");
                    return;
                }

                let last = coins[coins.len() - 1].clone();

                let mut c_used: Vec<BronCoin> = vec![];

                if coins.len() > 1 {
                    for c in 0..(coins.len() - 1) {
                        let tree: Vec<u8> = reqwest::blocking::get(format!("{}/api/tree", server))
                            .unwrap()
                            .bytes()
                            .unwrap()
                            .into();

                        let tree = MerkleTree::<DEPTH>::deserialize_with_mode(
                            tree.as_slice(),
                            Compress::No,
                            Validate::No,
                        )
                        .unwrap();

                        let (_c0, c1, tx) = split(
                            &mut rng,
                            coins[c].clone(),
                            df.sk.clone(),
                            pk.clone(),
                            df.pk.clone(),
                            coins[c].value,
                            F::ZERO,
                            tree.clone(),
                            df.proving_key.clone(),
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
                            c_used.push(coins[c].clone());
                            df.txs.push(t);
                            df.coins.push(c1);
                        } else {
                            println!("An error occurred.");
                            return;
                        }
                    }
                }

                let tree: Vec<u8> = reqwest::blocking::get(format!("{}/api/tree", server))
                    .unwrap()
                    .bytes()
                    .unwrap()
                    .into();

                let tree = MerkleTree::<DEPTH>::deserialize_with_mode(
                    tree.as_slice(),
                    Compress::No,
                    Validate::No,
                )
                .unwrap();
                let (_c0, c1, tx) = split(
                    &mut rng,
                    last.clone(),
                    df.sk.clone(),
                    pk.clone(),
                    df.pk.clone(),
                    left,
                    last.value - left,
                    tree.clone(),
                    df.proving_key.clone(),
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
                    c_used.push(last.clone());
                    df.txs.push(t);
                    df.coins.push(c1);
                } else {
                    println!("An error occurred.");
                    return;
                }

                let mut new = vec![];
                for i in df.coins {
                    if !c_used.contains(&i) {
                        new.push(i);
                    }
                }
                df.coins = new;
                let conv: u64 = <F as PrimeField>::BigInt::from(v).0[0];
                df.total_value -= conv;
                println!("You have {} coins now.", df.total_value);
                write_df(df);
            }
        }
        Commands::Scan => {
            let txs: Vec<u8> = reqwest::blocking::get(format!("{}/api/tx", server))
                .unwrap()
                .bytes()
                .unwrap()
                .into();

            let txs = <Vec<Transaction>>::deserialize_with_mode(
                txs.as_slice(),
                Compress::No,
                Validate::No,
            )
            .unwrap();
            let mut df = read_df();

            let mut amt = F::ZERO;

            for i in df.scan_index..txs.len() {
                if let Some(split) = txs[i].s.clone() {
                    if let Some(o) = decrypt_and_check(split.com1, split.data.0, df.sk.clone()) {
                        if !df.coins.contains(&o) {
                            amt += o.value;
                            df.coins.push(o);
                        }
                    }
                    if let Some(o) = decrypt_and_check(split.com2, split.data.1, df.sk.clone()) {
                        if !df.coins.contains(&o) {
                            amt += o.value;
                            df.coins.push(o);
                        }
                    }
                }
            }
            df.scan_index = txs.len();
            println!("You have {} more coins!", amt);
            let conv: u64 = <F as PrimeField>::BigInt::from(amt).0[0];
            df.total_value += conv;
            println!("You have {} coins in total.", df.total_value);
            write_df(df);
        }
    }
}
