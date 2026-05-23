"""SHA-256 compression structure (Merkle-Damgard, 64 rounds, same sigmas)
with non-standard K[64] round constants and non-standard H[8] initial state.
Must stay byte-for-byte consistent with hash_x() in src/sha256.c."""
import struct

KX = [
    0xba534ebe, 0x451a0b24, 0x3113e886, 0xfc8a22e5,
    0x4c428926, 0xa4cba63d, 0x29d689f6, 0x6609dfe7,
    0xbf25df24, 0x5f01eeef, 0x379fba1d, 0xb54f6ec4,
    0xbbde166d, 0x4f2d4ff8, 0xb7aac2c5, 0xdbd93483,
    0xf59c35cb, 0x0dbdc1ff, 0x22a2f34f, 0x8edb414c,
    0x615f892f, 0x904002ec, 0xe35503bf, 0xeb0bdf6a,
    0x2950c909, 0x77f7ba76, 0xb4f85a14, 0xc15143fd,
    0x355616f7, 0x98b87e23, 0xa7a1142e, 0x337d8923,
    0x13f46f2c, 0xbee4f777, 0x30e1f2c5, 0x1f462d09,
    0xac8f7cd4, 0xbd186224, 0x070bdab5, 0xc8a42f16,
    0x5f67e67e, 0x00121103, 0xeaa9cd42, 0x60e8d19d,
    0x0674d93c, 0x8b6efd55, 0x6ba9c3d1, 0xaed201dc,
    0x366d9a66, 0x47dac77b, 0x62996643, 0x7c530bbe,
    0x5241c776, 0x2bda0269, 0x771f29bb, 0xd9c2f81a,
    0xb2344acf, 0x768b20c1, 0x9b30e7cb, 0xc5894040,
    0x69293317, 0x9fe9ae5c, 0x4715a0c0, 0x0a0a3aac,
]
HX_INIT = [
    0xf312fe7f, 0x0fa6f542, 0x22123753, 0x8e113d20,
    0x9006103d, 0xe977352a, 0x92888328, 0xe20df0cb,
]

def _ror(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xffffffff

def _compress(H, blk):
    w = [0]*64
    for i in range(16):
        w[i] = struct.unpack('>I', blk[i*4:i*4+4])[0]
    for i in range(16, 64):
        s0 = _ror(w[i-15], 7) ^ _ror(w[i-15], 18) ^ (w[i-15] >> 3)
        s1 = _ror(w[i-2], 17) ^ _ror(w[i-2], 19) ^ (w[i-2] >> 10)
        w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xffffffff
    a, b, c, d, e, f, g, h = H
    for i in range(64):
        S1 = _ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)
        ch = (e & f) ^ ((~e & 0xffffffff) & g)
        t1 = (h + S1 + ch + KX[i] + w[i]) & 0xffffffff
        S0 = _ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)
        mj = (a & b) ^ (a & c) ^ (b & c)
        t2 = (S0 + mj) & 0xffffffff
        h = g; g = f; f = e; e = (d + t1) & 0xffffffff
        d = c; c = b; b = a; a = (t1 + t2) & 0xffffffff
    return [(x + y) & 0xffffffff for x, y in zip(H, (a, b, c, d, e, f, g, h))]

def hash_x(data: bytes) -> bytes:
    H = list(HX_INIT)
    bits = len(data) * 8
    off = 0
    while len(data) - off >= 64:
        H = _compress(H, data[off:off+64])
        off += 64
    rem = data[off:]
    pad = rem + b'\x80'
    # pad to 56 mod 64 then append 8-byte big-endian bit length
    if len(pad) % 64 < 57:
        pad += b'\x00' * (56 - (len(pad) % 64))
    else:
        pad += b'\x00' * (64 + 56 - (len(pad) % 64))
    pad += struct.pack('>Q', bits)
    for i in range(0, len(pad), 64):
        H = _compress(H, pad[i:i+64])
    return b''.join(struct.pack('>I', h) for h in H)
