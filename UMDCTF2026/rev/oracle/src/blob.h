#ifndef BLOB_H
#define BLOB_H
#include <stdint.h>
#include <stddef.h>

#define KEY_TABLE_SIZE 32
#define BLOB_BLOCK_SIZE 64

/* Keys are stored XOR-masked at rest; the helper writes the unmasked key
   into the caller's buffer. This means there's no 512-byte contiguous
   high-entropy table sitting in .rodata, and extracting the keys requires
   reading the unmask formula. */
void blob_get_key(unsigned idx, uint8_t out[16]);

/* Decrypt one layer of the blob in place.
   Format: header[64] || ciphertext[...]. The header drives per-block key
   and IV selection out of BLOB_KEY_TABLE. Returns the number of plaintext
   bytes (== len - 64), or negative on error. */
int blob_decrypt_layer(uint8_t *buf, size_t len);

/* Fully decrypt a two-layer blob. Returns pointer to malloc'd inner ZIP and
   its length. Caller frees. */
int blob_decrypt(const uint8_t *buf, size_t len, uint8_t **out, size_t *out_len);

/* Custom archive lookup. Returns 0 and fills out_ptr/out_len on success,
   1 if not found, negative on malformed archive. Format:
     magic[4]  = "ARC\x01"
     seed[4]   : LE 32-bit MWC seed (body is MWC-encrypted with it)
     n_entries : u8
     for each  : name_len(u8), name, data_len(u32 LE), data */
int arc_find_entry(const uint8_t *arc, size_t arc_len, const char *name,
                   const uint8_t **out_ptr, uint32_t *out_len);

#endif
