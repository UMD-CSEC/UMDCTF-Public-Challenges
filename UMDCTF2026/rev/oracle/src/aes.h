#ifndef AES_H
#define AES_H
#include <stdint.h>
#include <stddef.h>

void aes128_key_expand(const uint8_t key[16], uint8_t round_keys[176]);
void aes128_encrypt_block(const uint8_t rk[176], const uint8_t in[16], uint8_t out[16]);
void aes128_decrypt_block(const uint8_t rk[176], const uint8_t in[16], uint8_t out[16]);

/* CBC decrypt in place; strips PKCS7 and returns new length, or -1 on error */
int aes128_cbc_decrypt(const uint8_t key[16], const uint8_t iv[16],
                       uint8_t *buf, size_t len, int strip_pkcs7);

#endif
