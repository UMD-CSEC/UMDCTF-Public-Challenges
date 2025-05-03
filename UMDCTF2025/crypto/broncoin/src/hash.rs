use ark_crypto_primitives::sponge::poseidon::{
    find_poseidon_ark_and_mds, PoseidonConfig, PoseidonDefaultConfigEntry,
};
use ark_ff::PrimeField;

pub fn gen_poseidon_params<F: PrimeField>(
    rate: usize,
    optimized_for_weights: bool,
) -> PoseidonConfig<F> {
    let params_set = if !optimized_for_weights {
        [
            PoseidonDefaultConfigEntry::new(2, 17, 8, 31, 0),
            PoseidonDefaultConfigEntry::new(3, 5, 8, 56, 0),
            PoseidonDefaultConfigEntry::new(4, 5, 8, 56, 0),
            PoseidonDefaultConfigEntry::new(5, 5, 8, 57, 0),
            PoseidonDefaultConfigEntry::new(6, 5, 8, 57, 0),
            PoseidonDefaultConfigEntry::new(7, 5, 8, 57, 0),
            PoseidonDefaultConfigEntry::new(8, 5, 8, 57, 0),
        ]
    } else {
        [
            PoseidonDefaultConfigEntry::new(2, 257, 8, 13, 0),
            PoseidonDefaultConfigEntry::new(3, 257, 8, 13, 0),
            PoseidonDefaultConfigEntry::new(4, 257, 8, 13, 0),
            PoseidonDefaultConfigEntry::new(5, 257, 8, 13, 0),
            PoseidonDefaultConfigEntry::new(6, 257, 8, 13, 0),
            PoseidonDefaultConfigEntry::new(7, 257, 8, 13, 0),
            PoseidonDefaultConfigEntry::new(8, 257, 8, 13, 0),
        ]
    };

    for param in params_set.iter() {
        if param.rate == rate {
            let (ark, mds) = find_poseidon_ark_and_mds::<F>(
                F::MODULUS_BIT_SIZE as u64,
                rate,
                param.full_rounds as u64,
                param.partial_rounds as u64,
                param.skip_matrices as u64,
            );

            return PoseidonConfig {
                full_rounds: param.full_rounds,
                partial_rounds: param.partial_rounds,
                alpha: param.alpha as u64,
                ark,
                mds,
                rate: param.rate,
                capacity: 1,
            };
        }
    }

    panic!("could not generate poseidon params");
    // F::get_default_poseidon_parameters(rate, optimized_for_weights).unwrap()
}
