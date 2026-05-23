#![no_std]
#![allow(static_mut_refs)]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_: &PanicInfo) -> ! {
    loop {}
}

// -------------------------------------------------------------------------
// Constants
// -------------------------------------------------------------------------

const SECRET: [u8; 32] = [
    0x7e, 0x15, 0xca, 0xfe, 0xd0, 0x0d, 0xfe, 0xed,
    0xb0, 0x0b, 0xfa, 0xce, 0x5b, 0xad, 0xa5, 0x50,
    0xc0, 0xff, 0xee, 0x11, 0x11, 0xde, 0xad, 0xbe,
    0xef, 0xab, 0xad, 0xca, 0xfe, 0x13, 0x37, 0xaa,
];

// 512-bit state IV (8 lanes of u64)
const IV: [u64; 8] = [
    0x37a5b2d94e6c8f71,
    0x8c1e3f5a7b0d2c4f,
    0x91d6b8e2a4f7c0d3,
    0xf4e7c0a3b6d9e2c5,
    0x13824a69cfd0b5e7,
    0x6fa09c43d527e8b1,
    0xbc58e1df0a6c3793,
    0x2ed47b9061a8c5f3,
];

// 16 round constants
const RC: [u64; 16] = [
    0xa0761d6478bd642f,
    0xe7037ed1a0b428db,
    0x8ebc6af09c88c6e3,
    0x589965cc75374cc3,
    0x1d8e4e27c39bc93a,
    0xeb44accab455d165,
    0x3b9dff8c52ef5f43,
    0x6b91fa824d69dfae,
    0x9d28a6d6c5a4c39f,
    0x4f6cdd1d45f12853,
    0x2d9cf5b73a6e8147,
    0xc831076b94a2ef5d,
    0x71e583ac4f09d6b2,
    0x58b0c7f9a3e1652d,
    0xfa203e857c91b46f,
    0x9e4d21fb60c83a75,
];

// Non-linear byte substitution — custom 8-bit permutation, not AES.
// Generated via Python random.seed(0xDEADBEEF) + random.shuffle(list(range(256))).
const SBOX: [u8; 256] = [
    0xec, 0xca, 0x0e, 0xf3, 0x08, 0xf0, 0x2a, 0xa2, 0x3b, 0x18, 0x2b, 0x5c, 0x37, 0xbd, 0x12, 0xa8,
    0x05, 0xd3, 0xa1, 0x57, 0x4f, 0x96, 0xfc, 0xf5, 0xa7, 0x14, 0x19, 0x66, 0x58, 0x9b, 0xbf, 0xb4,
    0x39, 0xd5, 0x1e, 0x1a, 0x30, 0xbc, 0x6c, 0x80, 0xb7, 0xed, 0x41, 0x06, 0xd9, 0x17, 0x67, 0xcd,
    0x1d, 0x2c, 0xae, 0x24, 0x03, 0x13, 0xc6, 0x53, 0x83, 0x11, 0x0a, 0xf7, 0xc0, 0x4d, 0xc4, 0x9e,
    0x8d, 0x00, 0x1f, 0xc3, 0x3f, 0x35, 0x9f, 0xcb, 0x72, 0x9d, 0x16, 0x6f, 0xac, 0xce, 0x3c, 0x5e,
    0xa6, 0xe1, 0x7b, 0x34, 0x36, 0x32, 0xb8, 0x95, 0x91, 0x89, 0x52, 0xc1, 0xe7, 0xa3, 0x33, 0x48,
    0x04, 0xcf, 0x10, 0xeb, 0x25, 0xbb, 0x8e, 0x0f, 0x81, 0x6e, 0xb3, 0x43, 0x45, 0x8f, 0x49, 0xf8,
    0x4b, 0x59, 0x07, 0x4a, 0xde, 0xfd, 0xc8, 0xd0, 0x84, 0x8b, 0xfb, 0xda, 0xdb, 0x28, 0xd4, 0x3e,
    0xa4, 0x2f, 0x56, 0xbe, 0xef, 0x86, 0xc7, 0x62, 0xea, 0x76, 0xe9, 0xd6, 0x74, 0xa5, 0x6b, 0xf9,
    0x98, 0x7d, 0x3a, 0x26, 0x5a, 0xaf, 0x87, 0x0d, 0x1b, 0x2e, 0xb2, 0xe3, 0x6a, 0xcc, 0xf1, 0xff,
    0xd7, 0xf6, 0x1c, 0xc9, 0xe8, 0x70, 0x20, 0x4e, 0x23, 0x3d, 0xc2, 0xaa, 0xdc, 0x0b, 0xf2, 0x5f,
    0x7a, 0xfa, 0x88, 0x97, 0x47, 0xd1, 0x0c, 0x02, 0x31, 0x7f, 0xf4, 0x75, 0x15, 0x93, 0x38, 0x8a,
    0x42, 0x90, 0x71, 0xdd, 0x73, 0x55, 0x7e, 0xb5, 0x5b, 0x29, 0x4c, 0x9a, 0xe0, 0x8c, 0xb0, 0xe5,
    0x64, 0x27, 0x01, 0xdf, 0xad, 0x21, 0x79, 0x94, 0x92, 0x51, 0x69, 0x7c, 0x22, 0x63, 0x50, 0x85,
    0x2d, 0xe2, 0x40, 0x46, 0x44, 0xa9, 0x82, 0xb6, 0x61, 0xd8, 0xd2, 0xb9, 0x68, 0xab, 0xb1, 0x5d,
    0x65, 0x54, 0x77, 0xa0, 0xc5, 0xba, 0x60, 0x9c, 0xe4, 0xfe, 0xee, 0x99, 0xe6, 0x78, 0x6d, 0x09,
];

// Domain separators between absorb phases
const SEP_SECRET: u64 = 0x17a3e9b5c2d60481;
const SEP_SID:    u64 = 0x2e91c47d3f80a562;
const SEP_ROUND:  u64 = 0x4c6f2d85b913e7a0;

const GRID_SIZES: [u32; 4] = [5, 6, 7, 8];
const MIN_MINES: u32 = 3;
const CHICKEN_STEPS: u32 = 24;
const CAR_THRESHOLD: u64 = 7378697629483820646;
const NUM_RISK: u32 = 4;

const TYPE_MINES: u8 = 0;
const TYPE_CHICKEN: u8 = 1;

// -------------------------------------------------------------------------
// Permutation: 16 rounds of (ARX on pairs) → S-box → linear mix → lane perm
// -------------------------------------------------------------------------

fn sub_bytes(s: &mut [u64; 8]) {
    let mut i = 0;
    while i < 8 {
        let b = s[i].to_le_bytes();
        s[i] = u64::from_le_bytes([
            SBOX[b[0] as usize],
            SBOX[b[1] as usize],
            SBOX[b[2] as usize],
            SBOX[b[3] as usize],
            SBOX[b[4] as usize],
            SBOX[b[5] as usize],
            SBOX[b[6] as usize],
            SBOX[b[7] as usize],
        ]);
        i += 1;
    }
}

fn mix_lanes(s: &mut [u64; 8]) {
    let t0 = s[0] ^ s[3].rotate_left(13) ^ s[5];
    let t1 = s[1] ^ s[4].rotate_left(17) ^ s[6];
    let t2 = s[2] ^ s[5].rotate_left(19) ^ s[7];
    let t3 = s[3] ^ s[6].rotate_left(23) ^ s[0];
    let t4 = s[4] ^ s[7].rotate_left(29) ^ s[1];
    let t5 = s[5] ^ s[0].rotate_left(31) ^ s[2];
    let t6 = s[6] ^ s[1].rotate_left(37) ^ s[3];
    let t7 = s[7] ^ s[2].rotate_left(41) ^ s[4];
    s[0] = t0; s[1] = t1; s[2] = t2; s[3] = t3;
    s[4] = t4; s[5] = t5; s[6] = t6; s[7] = t7;
}

fn lane_perm(s: &mut [u64; 8]) {
    // [0,1,2,3,4,5,6,7] -> [3,5,7,1,2,4,6,0]
    let a = s[0]; let b = s[1]; let c = s[2]; let d = s[3];
    let e = s[4]; let f = s[5]; let g = s[6]; let h = s[7];
    s[0] = d; s[1] = f; s[2] = h; s[3] = b;
    s[4] = c; s[5] = e; s[6] = g; s[7] = a;
}

fn permute(s: &mut [u64; 8]) {
    let mut r = 0usize;
    while r < 16 {
        // ARX on four disjoint pairs
        let mut p = 0usize;
        while p < 4 {
            let a = p * 2;
            let b = a + 1;
            s[a] = s[a].wrapping_add(s[b]);
            s[b] = s[b].rotate_left(13) ^ s[a];
            s[a] = s[a].rotate_left(29);
            p += 1;
        }
        sub_bytes(s);
        mix_lanes(s);
        lane_perm(s);
        s[0] ^= RC[r];
        r += 1;
    }
}

// -------------------------------------------------------------------------
// Sponge init with domain separators
// -------------------------------------------------------------------------

fn init_state(sid: &[u8], round_idx: u32) -> [u64; 8] {
    let mut s = IV;

    // Phase 1: SECRET (32 bytes → 4 lanes)
    let mut i = 0;
    while i < 4 {
        let mut b = [0u8; 8];
        let mut j = 0;
        while j < 8 { b[j] = SECRET[i * 8 + j]; j += 1; }
        s[i] ^= u64::from_le_bytes(b);
        i += 1;
    }
    s[7] ^= SEP_SECRET;
    permute(&mut s);

    // Phase 2: sid (8 bytes per lane, permute every 8 lanes = 64 bytes)
    let mut idx: usize = 0;
    let mut off: usize = 0;
    while off < sid.len() {
        let mut b = [0u8; 8];
        let mut k = 0usize;
        while k < 8 && off + k < sid.len() {
            b[k] = sid[off + k];
            k += 1;
        }
        s[idx & 7] ^= u64::from_le_bytes(b);
        idx += 1;
        off += 8;
        if idx & 7 == 0 { permute(&mut s); }
    }
    s[7] ^= SEP_SID;
    permute(&mut s);

    // Phase 3: round_idx
    s[0] ^= round_idx as u64;
    s[7] ^= SEP_ROUND;
    permute(&mut s);

    s
}

// -------------------------------------------------------------------------
// Sponge-squeeze RNG (rate = 8 lanes per permutation)
// -------------------------------------------------------------------------

struct Rng {
    s: [u64; 8],
    pos: usize,
}

impl Rng {
    fn new(s: [u64; 8]) -> Self { Rng { s, pos: 8 } }

    fn next_u64(&mut self) -> u64 {
        if self.pos >= 8 {
            permute(&mut self.s);
            self.pos = 0;
        }
        let v = self.s[self.pos];
        self.pos += 1;
        v
    }

    fn range(&mut self, n: u64) -> u64 { self.next_u64() % n }
}

// -------------------------------------------------------------------------
// Game generation (output encoding unchanged)
// -------------------------------------------------------------------------

fn generate_game(sid: &[u8], round_idx: u32, out: &mut [u8]) -> usize {
    let state = init_state(sid, round_idx);
    let mut rng = Rng::new(state);

    let gtype = rng.next_u64() & 1;
    if gtype == 0 {
        let gs_idx = rng.range(GRID_SIZES.len() as u64) as usize;
        let grid_size = GRID_SIZES[gs_idx];
        let total = grid_size * grid_size;
        let num_mines = MIN_MINES + rng.range(1 + (total as u64) / 4) as u32;

        let mut positions = [0u8; 64];
        let mut i: u32 = 0;
        while i < total { positions[i as usize] = i as u8; i += 1; }

        let mut i: u32 = 0;
        while i < num_mines {
            let j = i + rng.range((total - i) as u64) as u32;
            let tmp = positions[i as usize];
            positions[i as usize] = positions[j as usize];
            positions[j as usize] = tmp;
            i += 1;
        }

        // insertion sort the first num_mines positions
        let mut i: u32 = 1;
        while i < num_mines {
            let mut j = i as usize;
            while j > 0 && positions[j - 1] > positions[j] {
                positions.swap(j - 1, j);
                j -= 1;
            }
            i += 1;
        }

        out[0] = TYPE_MINES;
        out[1] = grid_size as u8;
        out[2] = num_mines as u8;
        let mut i: u32 = 0;
        while i < num_mines {
            out[3 + i as usize] = positions[i as usize];
            i += 1;
        }
        3 + num_mines as usize
    } else {
        let risk_idx = rng.range(NUM_RISK as u64) as u8;
        let mut cars = [0u8; 32];
        let mut num_cars: usize = 0;
        let mut step: u32 = 0;
        while step < CHICKEN_STEPS {
            if rng.next_u64() < CAR_THRESHOLD {
                cars[num_cars] = step as u8;
                num_cars += 1;
            }
            step += 1;
        }
        out[0] = TYPE_CHICKEN;
        out[1] = risk_idx;
        out[2] = num_cars as u8;
        let mut i: usize = 0;
        while i < num_cars {
            out[3 + i] = cars[i];
            i += 1;
        }
        3 + num_cars
    }
}

// -------------------------------------------------------------------------
// WASM exports
// -------------------------------------------------------------------------

static mut SID_BUF: [u8; 64] = [0; 64];
static mut OUT_BUF: [u8; 64] = [0; 64];

#[no_mangle]
pub extern "C" fn sid_buf_ptr() -> *mut u8 {
    unsafe { SID_BUF.as_mut_ptr() }
}

#[no_mangle]
pub extern "C" fn out_buf_ptr() -> *mut u8 {
    unsafe { OUT_BUF.as_mut_ptr() }
}

#[no_mangle]
pub extern "C" fn generate(sid_len: usize, round_idx: u32) -> usize {
    let n = if sid_len > 64 { 64 } else { sid_len };
    unsafe {
        let sid_ref: &[u8] = &SID_BUF[..n];
        let out_ref: &mut [u8] = &mut OUT_BUF[..];
        generate_game(sid_ref, round_idx, out_ref)
    }
}
