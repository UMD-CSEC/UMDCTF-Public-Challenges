use ark_bls12_381::Fr as F;
use ark_crypto_primitives::crh::{
    poseidon::{self, CRH},
    CRHScheme, CRHSchemeGadget,
};
use ark_r1cs_std::{
    alloc::{AllocVar, AllocationMode},
    fields::fp::FpVar,
    R1CSVar,
};
use ark_relations::ns;
use ark_relations::r1cs::Namespace;
use ark_relations::r1cs::{ConstraintSystemRef, SynthesisError};
use ark_serialize::{CanonicalDeserialize, CanonicalSerialize};

use crate::hash::gen_poseidon_params;

#[derive(
    Clone,
    Debug,
    PartialEq,
    Eq,
    PartialOrd,
    Ord,
    Hash,
    CanonicalSerialize,
    CanonicalDeserialize,
    Default,
)]
pub struct BronCoin {
    pub addr: F,
    pub value: F,
    pub pre_sn: F,
    pub rand: (F, F),
}

#[derive(Clone, Debug)]
pub struct BronCoinVar {
    pub addr: FpVar<F>,
    pub value: FpVar<F>,
    pub pre_sn: FpVar<F>,
    pub rand: (FpVar<F>, FpVar<F>),
}

impl AllocVar<BronCoin, F> for BronCoinVar {
    fn new_variable<T: std::borrow::Borrow<BronCoin>>(
        cs: impl Into<Namespace<F>>,
        f: impl FnOnce() -> Result<T, SynthesisError>,
        mode: AllocationMode,
    ) -> Result<Self, SynthesisError> {
        let ns = cs.into();
        let cs = ns.cs();
        let res = f();

        res.and_then(|coin| {
            let coin = coin.borrow();

            let addr = FpVar::new_variable(ns!(cs, "addr"), || Ok(coin.addr), mode)?;
            let value = FpVar::new_variable(ns!(cs, "value"), || Ok(coin.value), mode)?;
            let pre_sn = FpVar::new_variable(ns!(cs, "pre_sn"), || Ok(coin.pre_sn), mode)?;
            let rand_0 = FpVar::new_variable(ns!(cs, "rand_0"), || Ok(coin.rand.0), mode)?;
            let rand_1 = FpVar::new_variable(ns!(cs, "rand_1"), || Ok(coin.rand.1), mode)?;

            Ok(BronCoinVar {
                addr,
                value,
                pre_sn,
                rand: (rand_0, rand_1),
            })
        })
    }
}

impl R1CSVar<F> for BronCoinVar {
    type Value = BronCoin;

    fn cs(&self) -> ConstraintSystemRef<F> {
        self.addr
            .cs()
            .or(self.value.cs())
            .or(self.pre_sn.cs())
            .or(self.rand.0.cs())
            .or(self.rand.1.cs())
    }

    fn value(&self) -> Result<Self::Value, SynthesisError> {
        Ok(BronCoin {
            addr: self.addr.value()?,
            value: self.value.value()?,
            pre_sn: self.pre_sn.value()?,
            rand: (self.rand.0.value()?, self.rand.1.value()?),
        })
    }
}

impl BronCoin {
    pub fn commit(&self) -> F {
        let phase1 = vec![self.addr, self.pre_sn, self.rand.0];
        let p1_out = CRH::evaluate(&gen_poseidon_params(2, false), phase1).unwrap();
        let phase2 = vec![self.value, p1_out, self.rand.1];
        let p2_out = CRH::evaluate(&gen_poseidon_params(2, false), phase2).unwrap();
        p2_out
    }
}

impl BronCoinVar {
    pub fn commit(&self) -> Result<FpVar<F>, SynthesisError> {
        let params = gen_poseidon_params(2, false);
        let params_var = poseidon::constraints::CRHParametersVar { parameters: params };

        let phase1 = vec![self.addr.clone(), self.pre_sn.clone(), self.rand.0.clone()];

        let p1_out = poseidon::constraints::CRHGadget::evaluate(&params_var, &phase1)?;
        let phase2 = vec![self.value.clone(), p1_out, self.rand.1.clone()];
        let p2_out = poseidon::constraints::CRHGadget::evaluate(&params_var, &phase2);
        p2_out
    }
}
