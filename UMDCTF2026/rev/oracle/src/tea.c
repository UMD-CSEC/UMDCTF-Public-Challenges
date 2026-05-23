#include "tea.h"
#include <string.h>

#define TEA_DELTA 0x9e3779b9
#define TEA_ROUNDS 32

void tea_encrypt_block(const uint32_t k[4], uint32_t v[2]){
    uint32_t v0=v[0], v1=v[1], sum=0;
    for(int i=0;i<TEA_ROUNDS;i++){
        sum += TEA_DELTA;
        v0 += ((v1<<4) + k[0]) ^ (v1 + sum) ^ ((v1>>5) + k[1]);
        v1 += ((v0<<4) + k[2]) ^ (v0 + sum) ^ ((v0>>5) + k[3]);
    }
    v[0]=v0; v[1]=v1;
}

void tea_decrypt_block(const uint32_t k[4], uint32_t v[2]){
    uint32_t v0=v[0], v1=v[1], sum=(uint32_t)(TEA_DELTA * (uint32_t)TEA_ROUNDS);
    for(int i=0;i<TEA_ROUNDS;i++){
        v1 -= ((v0<<4) + k[2]) ^ (v0 + sum) ^ ((v0>>5) + k[3]);
        v0 -= ((v1<<4) + k[0]) ^ (v1 + sum) ^ ((v1>>5) + k[1]);
        sum -= TEA_DELTA;
    }
    v[0]=v0; v[1]=v1;
}

/* CFB with 64-bit blocks. Keystream block = TEA_ENCRYPT(prev_ct).
   Since we're decrypting, prev_ct is the ciphertext we just consumed. */
void tea_cfb_decrypt(const uint32_t k[4], const uint8_t iv[8],
                     uint8_t *buf, size_t len){
    uint32_t fb[2];
    memcpy(fb, iv, 8);
    size_t off=0;
    while(off + 8 <= len){
        uint32_t ks[2] = {fb[0], fb[1]};
        tea_encrypt_block(k, ks);
        uint8_t ct_block[8];
        memcpy(ct_block, buf+off, 8);
        for(int i=0;i<8;i++){
            uint8_t ksb = (uint8_t)(ks[i/4] >> (8*(i%4)));
            buf[off+i] = ct_block[i] ^ ksb;
        }
        memcpy(fb, ct_block, 8);
        off += 8;
    }
    if(off < len){
        uint32_t ks[2] = {fb[0], fb[1]};
        tea_encrypt_block(k, ks);
        for(size_t i=0; off+i<len; i++){
            uint8_t ksb = (uint8_t)(ks[i/4] >> (8*(i%4)));
            buf[off+i] ^= ksb;
        }
    }
}
