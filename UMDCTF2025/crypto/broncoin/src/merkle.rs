use std::{borrow::Borrow, marker::PhantomData};

use ark_bls12_381::Fr as F;
use ark_crypto_primitives::crh::{
    poseidon::{self, CRH},
    CRHScheme, CRHSchemeGadget,
};
use ark_ff::{AdditiveGroup, Field};
use ark_r1cs_std::{
    alloc::{AllocVar, AllocationMode},
    eq::EqGadget,
    fields::fp::FpVar,
    prelude::Boolean,
    R1CSVar,
};
use ark_relations::r1cs::{ConstraintSystemRef, Namespace, SynthesisError};
use ark_serialize::{CanonicalDeserialize, CanonicalSerialize};

use crate::hash::gen_poseidon_params;

#[derive(Clone, Debug, CanonicalSerialize, CanonicalDeserialize)]
pub struct MerkleTree<const N: usize> {
    pub elements: Vec<F>,

    pub index: usize,

    // pub past_roots: Vec<F>, // loses anonymity but w/e
    // pub past_elements: Vec<Vec<F>>,
    _depth: PhantomData<[F; N]>,
}

impl<const N: usize> MerkleTree<N> {
    pub fn new_from_elements(v: Vec<F>) -> Self {
        if v.len() > (1 << N) {
            panic!("Too many elements for initial merkle tree");
        } else {
            Self {
                elements: v,
                index: 0,
                _depth: PhantomData,
            }
        }
    }

    pub fn get_root(&self) -> F {
        let params = gen_poseidon_params(2, false);

        let mut current_stage: Vec<F> = self.elements[self.index..].to_vec();

        for i in (0..N).rev() {
            let num_elements = 1 << (i + 1);
            while current_stage.len() < num_elements {
                current_stage.push(F::ZERO);
            }

            let mut next_stage = vec![];

            for j in 0..(num_elements >> 1) {
                next_stage.push(
                    CRH::evaluate(&params, [current_stage[2 * j], current_stage[2 * j + 1]])
                        .unwrap(),
                );
            }

            current_stage = next_stage;
        }

        current_stage[0]
    }

    pub fn append(&mut self, value: F) {
        if self.elements.len() >= (1 << N) {
            self.elements.push(value);
            self.index += 1;
        } else if self.elements.len() < (1 << N) {
            self.elements.push(value);
        }
    }

    pub fn find_element(&self, value: F) -> usize {
        self.elements[self.index..]
            .to_vec()
            .iter()
            .position(|v| *v == value)
            .unwrap()
    }

    pub fn is_in(&self, value: F) -> bool {
        self.elements[self.index..].contains(&value)
    }

    pub fn construct_merkle_path(&self, index: usize) -> (PathProof<N>, F) {
        merkle_path_proof(&self.elements[self.index..].to_vec(), index)
    }
}

pub fn merkle_path_proof<const N: usize>(elements: &Vec<F>, index: usize) -> (PathProof<N>, F) {
    let mut valid_list = vec![];

    let mut n_index = index;

    let mut future_index = n_index;

    let params = gen_poseidon_params(2, false);

    let mut current_stage = elements.clone();

    for i in (0..N).rev() {
        let num_elements = 1 << (i + 1);
        while current_stage.len() < num_elements {
            current_stage.push(F::ZERO);
        }

        let mut next_stage = vec![];

        for j in 0..(num_elements >> 1) {
            if 2 * j == n_index {
                valid_list.push((current_stage[2 * j + 1], F::ZERO));
                future_index = n_index >> 1;
            } else if 2 * j + 1 == n_index {
                valid_list.push((current_stage[2 * j], F::ONE));
                future_index = (n_index - 1) >> 1;
            }

            next_stage.push(
                CRH::evaluate(&params, [current_stage[2 * j], current_stage[2 * j + 1]]).unwrap(),
            );
        }

        n_index = future_index;
        current_stage = next_stage;
    }

    (
        PathProof {
            val: elements[index],
            list: valid_list.try_into().unwrap(),
        },
        current_stage[0],
    )
}

#[derive(Clone, PartialEq, Eq, Debug)]
pub struct PathProof<const N: usize> {
    pub val: F,
    pub list: [(F, F); N],
}

impl<const N: usize> Default for PathProof<N> {
    fn default() -> Self {
        Self {
            val: F::default(),
            list: [(F::default(), F::default()); N],
        }
    }
}

pub struct PathProofVar<const N: usize> {
    pub val: FpVar<F>,
    pub list: [(FpVar<F>, FpVar<F>); N],
}

impl<const N: usize> R1CSVar<F> for PathProofVar<N> {
    type Value = PathProof<N>;

    fn cs(&self) -> ConstraintSystemRef<F> {
        let mut cs = ConstraintSystemRef::None;
        cs = self.val.cs().or(cs.clone());
        for (a, b) in &self.list {
            cs = a.cs().or(cs.clone());
            cs = b.cs().or(cs.clone());
        }
        cs
    }

    fn value(&self) -> Result<Self::Value, SynthesisError> {
        Ok(PathProof {
            val: self.val.value().unwrap(),
            list: core::array::from_fn(|i| {
                (
                    self.list[i].0.value().unwrap(),
                    self.list[i].1.value().unwrap(),
                )
            }),
        })
    }
}

impl<const N: usize> AllocVar<PathProof<N>, F> for PathProofVar<N> {
    fn new_variable<T: Borrow<PathProof<N>>>(
        cs: impl Into<Namespace<F>>,
        f: impl FnOnce() -> Result<T, SynthesisError>,
        mode: AllocationMode,
    ) -> Result<Self, SynthesisError> {
        let ns = cs.into();
        let cs = ns.cs();

        let value = f()?;
        let value = value.borrow();

        let val = FpVar::new_variable(cs.clone(), || Ok(value.val), mode)?;

        let list = core::array::from_fn(|i| {
            let (ref a, ref b) = value.list[i];
            let a_var = FpVar::<F>::new_variable(cs.clone(), || Ok(a), mode).unwrap();
            let b_var = FpVar::<F>::new_variable(cs.clone(), || Ok(b), mode).unwrap();
            (a_var, b_var)
        });

        Ok(Self { val, list })
    }
}

impl<const N: usize> PathProofVar<N> {
    pub fn verify_path(&self, root: FpVar<F>) -> Result<Boolean<F>, SynthesisError> {
        let params = gen_poseidon_params(2, false);
        let params_var = poseidon::constraints::CRHParametersVar { parameters: params };

        let mut curr_value = self.val.clone();

        for i in 0..N {
            curr_value = {
                (FpVar::Constant(F::ONE) - self.list[i].1.clone())
                    * poseidon::constraints::CRHGadget::evaluate(
                        &params_var,
                        &[curr_value.clone(), self.list[i].0.clone()],
                    )?
                    + self.list[i].1.clone()
                        * poseidon::constraints::CRHGadget::evaluate(
                            &params_var,
                            &[self.list[i].0.clone(), curr_value],
                        )?
            };
        }
        curr_value.is_eq(&root)
    }
}

#[test]
fn testing123() {
    use ark_relations::ns;
    use ark_relations::r1cs::ConstraintSystem;
    let arr = vec![F::from(1), F::from(2), F::from(3)];

    let merkle_tree = MerkleTree::<4>::new_from_elements(arr);

    let (path, root) = merkle_tree.construct_merkle_path(1);

    let cs = ConstraintSystem::<F>::new_ref();

    let path_proof = PathProofVar::new_witness(ns!(cs, "path"), || Ok(&path)).unwrap();
    let root = FpVar::<F>::new_input(ns!(cs, "root"), || Ok(&root)).unwrap();

    let verif = path_proof.verify_path(root).unwrap();

    verif.enforce_equal(&Boolean::TRUE).unwrap();

    assert!(cs.is_satisfied().unwrap());
}
