#include "xorstr.h"
#include <string.h>

/* Tamper is folded into output instead of gated by a branch: wrong args
   produce scrambled bytes but the function still returns normally. */
static char *decode(const uint8_t *pool, uint32_t xor_const,
                    uint32_t v20_0, uint32_t v20_1,
                    char *buf, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3)
{
    uint32_t off = (a0 ^ a2 ^ xor_const);
    uint32_t len = (a3 ^ a1 ^ v20_0);
    uint32_t ml0 = (a1 ^ v20_0);
    uint32_t ml1 = (a2 ^ v20_1);
    uint8_t mask[8];
    mask[0]=(uint8_t)ml0; mask[1]=(uint8_t)(ml0>>8); mask[2]=(uint8_t)(ml0>>16); mask[3]=(uint8_t)(ml0>>24);
    mask[4]=(uint8_t)ml1; mask[5]=(uint8_t)(ml1>>8); mask[6]=(uint8_t)(ml1>>16); mask[7]=(uint8_t)(ml1>>24);

    const uint8_t *p = pool + off;
    uint16_t hdr = (uint16_t)p[0] | ((uint16_t)p[1] << 8);
    uint16_t tamper = (uint16_t)(hdr ^ (uint16_t)a1) ^ (uint16_t)0x7DD1;
    uint8_t t_lo = (uint8_t)tamper, t_hi = (uint8_t)(tamper >> 8);
    const uint8_t *enc = p + 2;
    for(uint32_t i=0; i<len; i++){
        uint8_t c = enc[i] ^ mask[i & 7];
        c ^= (i & 1) ? t_hi : t_lo;
        buf[i] = (char)c;
    }
    buf[len] = 0;
    return buf;
}

char *xsA(char *buf, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3){
    return decode(xsA_pool, XSA_XOR_CONST, XSA_V20_0, XSA_V20_1, buf, a0,a1,a2,a3);
}
char *xsB(char *buf, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3){
    return decode(xsB_pool, XSB_XOR_CONST, XSB_V20_0, XSB_V20_1, buf, a0,a1,a2,a3);
}
