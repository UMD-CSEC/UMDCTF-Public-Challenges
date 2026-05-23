#include "blob.h"
#include "aes.h"
#include "vm.h"   /* for mwc_decrypt */
#include <stdlib.h>
#include <string.h>

int blob_decrypt_layer(uint8_t *buf, size_t len){
    if(len < BLOB_BLOCK_SIZE + 16 || ((len - BLOB_BLOCK_SIZE) % 16) != 0)
        return -1;
    const uint8_t *hdr = buf;
    uint8_t *body = buf + BLOB_BLOCK_SIZE;
    size_t body_len = len - BLOB_BLOCK_SIZE;
    size_t blocks = body_len / BLOB_BLOCK_SIZE;
    size_t tail_bytes = body_len - blocks * BLOB_BLOCK_SIZE;
    (void)tail_bytes;

    /* Process in BLOB_BLOCK_SIZE (64-byte) chunks. Each chunk is an integral
       number of AES blocks (4). Any partial tail must be block-aligned (16B). */

    size_t off = 0;
    size_t block_idx = 0;
    while(off < body_len){
        size_t chunk_len = body_len - off;
        if(chunk_len > BLOB_BLOCK_SIZE) chunk_len = BLOB_BLOCK_SIZE;
        if(chunk_len % 16 != 0) return -2;

        uint8_t idx1 = hdr[(block_idx + 11) & 63] % KEY_TABLE_SIZE;
        uint8_t idx2 = hdr[(block_idx + 17) & 63] % KEY_TABLE_SIZE;
        uint8_t idx3 = hdr[block_idx & 63]        % KEY_TABLE_SIZE;

        /* derived_key = AES_ECB_DEC(key=TABLE[idx3], data=TABLE[idx1]) */
        uint8_t k3[16], k1[16], k2[16], rk[176], dk[16];
        blob_get_key(idx3, k3);
        blob_get_key(idx1, k1);
        blob_get_key(idx2, k2);
        aes128_key_expand(k3, rk);
        aes128_decrypt_block(rk, k1, dk);

        /* AES-128-CBC decrypt chunk with key=dk, iv=k2, no pad strip. */
        int nl = aes128_cbc_decrypt(dk, k2, body + off, chunk_len, 0);
        if(nl < 0) return -3;

        off += chunk_len;
        block_idx++;
    }
    /* Shift plaintext to start-of-buffer: drop the header. */
    memmove(buf, body, body_len);
    return (int)body_len;
}

int blob_decrypt(const uint8_t *buf, size_t len, uint8_t **out, size_t *out_len)
{
    uint8_t *work = (uint8_t*)malloc(len);
    if(!work) return -10;
    memcpy(work, buf, len);
    int n = blob_decrypt_layer(work, len);
    if(n < 0){ free(work); return n; }
    int n2 = blob_decrypt_layer(work, (size_t)n);
    if(n2 < 0){ free(work); return n2; }

    /* Undo the archive-body MWC layer and collapse the 4 seed bytes
       out of the visible buffer so arc_find_entry sees plaintext TLV. */
    if(n2 >= 8 && work[0]=='A' && work[1]=='R' && work[2]=='C' && work[3]==0x01){
        uint32_t seed = (uint32_t)work[4] | ((uint32_t)work[5]<<8) |
                        ((uint32_t)work[6]<<16) | ((uint32_t)work[7]<<24);
        size_t body_len = (size_t)n2 - 8;
        mwc_decrypt(work + 8, body_len, seed);
        memmove(work + 4, work + 8, body_len);
        n2 -= 4;
    }

    *out = work;
    *out_len = (size_t)n2;
    return 0;
}

int arc_find_entry(const uint8_t *arc, size_t alen, const char *name,
                   const uint8_t **out_ptr, uint32_t *out_len)
{
    if(alen < 5) return -1;
    if(arc[0] != 'A' || arc[1] != 'R' || arc[2] != 'C' || arc[3] != 0x01)
        return -2;
    size_t pos = 4;
    uint8_t n = arc[pos++];
    size_t nlen = strlen(name);
    for(uint8_t i = 0; i < n; i++){
        if(pos + 1 > alen) return -3;
        uint8_t name_len = arc[pos++];
        if(pos + name_len + 4 > alen) return -3;
        const uint8_t *nm = arc + pos; pos += name_len;
        uint32_t data_len = (uint32_t)arc[pos] | ((uint32_t)arc[pos+1]<<8) |
                            ((uint32_t)arc[pos+2]<<16) | ((uint32_t)arc[pos+3]<<24);
        pos += 4;
        if(pos + data_len > alen) return -3;
        if(name_len == nlen && memcmp(nm, name, nlen) == 0){
            *out_ptr = arc + pos;
            *out_len = data_len;
            return 0;
        }
        pos += data_len;
    }
    return 1;
}

