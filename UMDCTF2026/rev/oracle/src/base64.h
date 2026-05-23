#ifndef BASE64_H
#define BASE64_H
#include <stdint.h>
#include <stddef.h>

/* Decode base64 into caller-provided buffer. Returns decoded length or -1. */
int b64_decode(const char *in, size_t in_len, uint8_t *out, size_t out_cap);

#endif
