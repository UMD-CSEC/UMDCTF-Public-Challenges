#ifndef XORSTR_H
#define XORSTR_H
#include <stdint.h>

/* Two decoder variants. Each call site passes 4 args that combine with
   the pool's XOR_CONST / V20_0 / V20_1 to derive a pool offset, length,
   and 8-byte XOR mask. A 2-byte header at the pool entry XORs with a1
   to 0x7DD1; a mismatch silently scrambles output rather than branching. */

extern const uint8_t xsA_pool[];
extern const uint8_t xsB_pool[];

char *xsA(char *buf, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3);
char *xsB(char *buf, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3);

#define XSA_XOR_CONST 0x3BF1F5AAu
#define XSA_V20_0     0x7154F8C0u
#define XSA_V20_1     0x9B27C67Fu

#define XSB_XOR_CONST 0xB44E2B42u
#define XSB_V20_0     0x474F87D2u
#define XSB_V20_1     0x329BD061u

#endif
