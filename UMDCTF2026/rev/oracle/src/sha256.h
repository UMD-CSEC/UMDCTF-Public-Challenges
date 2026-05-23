#ifndef SHA256_H
#define SHA256_H
#include <stdint.h>
#include <stddef.h>

/* Non-standard SHA-256-like hash. Structurally identical (Merkle-Damgard,
   64 rounds, same padding), but with ENTIRELY custom K[64] round constants
   and custom H[8] initial state. Used to derive the flag decryption key
   from the ticket's signature state. A solver grepping for the usual
   0x428a2f98 won't find anything; they must recover K/H from the binary. */
void hash_x(const uint8_t *data, size_t len, uint8_t out[32]);

#endif
