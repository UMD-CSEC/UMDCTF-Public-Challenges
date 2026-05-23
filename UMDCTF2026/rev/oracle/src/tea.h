#ifndef TEA_H
#define TEA_H
#include <stdint.h>
#include <stddef.h>

/* 64-bit block TEA with 128-bit key. */
void tea_encrypt_block(const uint32_t key[4], uint32_t v[2]);
void tea_decrypt_block(const uint32_t key[4], uint32_t v[2]);

/* TEA in CFB mode: IV is 8 bytes, decrypt streams plaintext out of ciphertext.
   Used for runtime decryption of the .kitext section. */
void tea_cfb_decrypt(const uint32_t key[4], const uint8_t iv[8],
                     uint8_t *buf, size_t len);

#endif
