#include "sha256.h"
#include <string.h>

#define ROR(x,n) (((x)>>(n)) | ((x)<<(32-(n))))

/* Non-standard hash — SHA-256 structure, custom K and H. K is re-used by an
   internal compression function. We keep the mixing function identical, only
   the round constants and initial state change. A solver cannot identify
   this as SHA-256 by its constants. */
static const uint32_t KX[64] = {
    0xba534ebeu, 0x451a0b24u, 0x3113e886u, 0xfc8a22e5u,
    0x4c428926u, 0xa4cba63du, 0x29d689f6u, 0x6609dfe7u,
    0xbf25df24u, 0x5f01eeefu, 0x379fba1du, 0xb54f6ec4u,
    0xbbde166du, 0x4f2d4ff8u, 0xb7aac2c5u, 0xdbd93483u,
    0xf59c35cbu, 0x0dbdc1ffu, 0x22a2f34fu, 0x8edb414cu,
    0x615f892fu, 0x904002ecu, 0xe35503bfu, 0xeb0bdf6au,
    0x2950c909u, 0x77f7ba76u, 0xb4f85a14u, 0xc15143fdu,
    0x355616f7u, 0x98b87e23u, 0xa7a1142eu, 0x337d8923u,
    0x13f46f2cu, 0xbee4f777u, 0x30e1f2c5u, 0x1f462d09u,
    0xac8f7cd4u, 0xbd186224u, 0x070bdab5u, 0xc8a42f16u,
    0x5f67e67eu, 0x00121103u, 0xeaa9cd42u, 0x60e8d19du,
    0x0674d93cu, 0x8b6efd55u, 0x6ba9c3d1u, 0xaed201dcu,
    0x366d9a66u, 0x47dac77bu, 0x62996643u, 0x7c530bbeu,
    0x5241c776u, 0x2bda0269u, 0x771f29bbu, 0xd9c2f81au,
    0xb2344acfu, 0x768b20c1u, 0x9b30e7cbu, 0xc5894040u,
    0x69293317u, 0x9fe9ae5cu, 0x4715a0c0u, 0x0a0a3aacu,
};
static const uint32_t HX[8] = {
    0xf312fe7fu, 0x0fa6f542u, 0x22123753u, 0x8e113d20u,
    0x9006103du, 0xe977352au, 0x92888328u, 0xe20df0cbu,
};

static void compress_x(uint32_t H[8], const uint8_t blk[64]){
    uint32_t w[64];
    for(int i=0;i<16;i++){
        w[i]=((uint32_t)blk[i*4]<<24)|((uint32_t)blk[i*4+1]<<16)|
             ((uint32_t)blk[i*4+2]<<8)|(uint32_t)blk[i*4+3];
    }
    for(int i=16;i<64;i++){
        uint32_t s0 = ROR(w[i-15],7)^ROR(w[i-15],18)^(w[i-15]>>3);
        uint32_t s1 = ROR(w[i-2],17)^ROR(w[i-2],19)^(w[i-2]>>10);
        w[i]=w[i-16]+s0+w[i-7]+s1;
    }
    uint32_t a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
    for(int i=0;i<64;i++){
        uint32_t S1=ROR(e,6)^ROR(e,11)^ROR(e,25);
        uint32_t ch=(e&f)^((~e)&g);
        uint32_t t1=h+S1+ch+KX[i]+w[i];
        uint32_t S0=ROR(a,2)^ROR(a,13)^ROR(a,22);
        uint32_t mj=(a&b)^(a&c)^(b&c);
        uint32_t t2=S0+mj;
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    H[0]+=a;H[1]+=b;H[2]+=c;H[3]+=d;H[4]+=e;H[5]+=f;H[6]+=g;H[7]+=h;
}

void hash_x(const uint8_t *data, size_t len, uint8_t out[32]){
    uint32_t H[8];
    for(int i=0;i<8;i++) H[i] = HX[i];
    uint64_t bits = (uint64_t)len * 8;
    size_t off=0;
    while(len-off >= 64){ compress_x(H, data+off); off+=64; }
    uint8_t buf[128]={0};
    size_t r = len-off;
    memcpy(buf, data+off, r);
    buf[r] = 0x80;
    size_t total = (r<56)?64:128;
    for(int i=0;i<8;i++) buf[total-1-i] = (uint8_t)(bits>>(8*i));
    compress_x(H, buf);
    if(total==128) compress_x(H, buf+64);
    for(int i=0;i<8;i++){
        out[i*4]  =(uint8_t)(H[i]>>24);
        out[i*4+1]=(uint8_t)(H[i]>>16);
        out[i*4+2]=(uint8_t)(H[i]>>8);
        out[i*4+3]=(uint8_t)H[i];
    }
}
