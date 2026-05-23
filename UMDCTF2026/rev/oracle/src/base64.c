#include "base64.h"

static int dv(int c){
    if(c>='A'&&c<='Z') return c-'A';
    if(c>='a'&&c<='z') return 26+c-'a';
    if(c>='0'&&c<='9') return 52+c-'0';
    if(c=='+') return 62;
    if(c=='/') return 63;
    return -1;
}

int b64_decode(const char *in, size_t in_len, uint8_t *out, size_t out_cap){
    uint32_t acc = 0; int bits = 0; size_t o = 0;
    for(size_t i=0;i<in_len;i++){
        char c = in[i];
        if(c==' '||c=='\r'||c=='\n'||c=='\t') continue;
        if(c=='=') break;
        int v = dv((unsigned char)c);
        if(v < 0) return -1;
        acc = (acc << 6) | (uint32_t)v;
        bits += 6;
        if(bits >= 8){
            bits -= 8;
            if(o >= out_cap) return -1;
            out[o++] = (uint8_t)((acc >> bits) & 0xff);
        }
    }
    return (int)o;
}
