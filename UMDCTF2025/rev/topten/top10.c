#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <immintrin.h>

#define UBYTES 0
#define UWORDS 1
#define BYTES 2
#define WORDS 3

#define SUBSET 0
#define RANGES 4
#define MATCH 8
#define SUBSTR 12

#define INVERT 16
#define INVERT_VALID 48

#define BITMASK 0
#define BYTEMASK 64

#define FIRSTMATCH 0
#define FINALMATCH 64

#define printv16qi(result) printf("%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx\n", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10], result[11], result[12], result[13], result[14], result[15])
#define printv16hi(result) printf("%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx%04hx\n", result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10], result[11], result[12], result[13], result[14], result[15])

typedef float v8sf __attribute__ ((vector_size (32)));
typedef float v4sf __attribute__ ((vector_size (16)));
typedef char v8qi __attribute__ ((vector_size (8)));
typedef char v16qi __attribute__ ((vector_size (16)));
typedef char v32qi __attribute__ ((vector_size (32)));
typedef long long unsigned int v2di __attribute__ ((vector_size (16)));
typedef unsigned short v16hi __attribute__ ((vector_size (32)));
typedef unsigned short v8hi __attribute__ ((vector_size (16)));

inline void rdseed(long long unsigned int *seed) {
	int rc;
	while ((rc = _rdseed64_step(seed)) == 0);
}

int main(int argc, char **argv) {
	long long unsigned int seed;
	v16qi params16qi[4];
	v16hi *params16hi = (v16hi *)params16qi;
	v32qi *params32qi = (v32qi *)(params16qi+2);

	if (argc < 2) {
		printf("Usage: %s <flag>\n", argv[0]);
		return 0;
	}

	// check first 7 characters
	char* input = argv[1];
	v16qi ffmtmatch = {'U','M','D','C','T','F','{'};
	memcpy(&params16qi[0], input, 16);
	v16qi result16qi = __builtin_ia32_pcmpestrm128(ffmtmatch, 7, params16qi[0], 16, BITMASK | MATCH | UBYTES);
	if (result16qi[0] != 0x7f) goto fail;

	// check end brace and null byte
	short endflag = '}';
	if (!__atomic_compare_exchange_n((short *)(input + 71), &endflag, '}', false, __ATOMIC_SEQ_CST, __ATOMIC_SEQ_CST)) goto fail;

	memcpy(&params16qi[0], input + 7, 64);

	// check charset
	v16qi range = {'!','~'};
	v32qi expect = {0};
	for (int i = 0; i < 4; i++) {
		result16qi = __builtin_ia32_pcmpestrm128(range, 2, params16qi[i], 16, INVERT | BYTEMASK | RANGES | UBYTES);
		if (!__builtin_ia32_ptestz128(result16qi, result16qi)) goto fail;
	}

	// check first 128 bits (16 bytes)
	v16qi res = __builtin_ia32_pclmulqdq128(params16qi[0], params16qi[0], 0x10);
	v16qi shouldbe = {144, 228, 20, 182, 26, 221, 1, 168, 123, 208, 186, 15, 205, 132, 14, 14};
	if (__builtin_ia32_pcmpestri128(shouldbe, 16, res, 16, SUBSTR | UBYTES)) goto fail;
	// disambiguate order
	if (_pext_u64(*(unsigned long long *)&params16qi, *(((unsigned long long *)&params16qi)+1)) != 562026407ULL) goto fail;

	// check next 128 bits
	v4sf shuf1 = (v4sf)params16qi[1];
	*(unsigned int *)(&shuf1) = _pext_u64(((unsigned long long *)(&params16qi[1]))[1], 0xffffffffULL);
	((unsigned int *)(&shuf1))[1] = _pext_u64(((unsigned long long *)(&params16qi[1]))[0], 0xffffffffULL);
	((unsigned int *)(&shuf1))[2] = _pext_u64(((unsigned long long *)(&params16qi[1]))[0], 0xffffffff00000000ULL);
	v4sf result4sf = __builtin_ia32_addsubps((v4sf)params16qi[1], shuf1);
	v4sf expect4sf = {1.7268289610614863e+28, 1.7269343608586483e+28, 1.0539650845336378e+24, 3.6204573916620575e-07};
	if (__builtin_ia32_pcmpestri128(*(v16qi *)(&expect4sf), 16, *(v16qi *)(&result4sf), 16, SUBSTR | UBYTES)) goto fail;

	v4sf shuf2 = shuf1;
	v8qi shufmask = {4,5,6,7,0,1,2,3};
	((v8qi *)(&shuf2))[1] = __builtin_ia32_pshufb(((v8qi *)(&shuf1))[1], shufmask);
	result4sf = __builtin_ia32_dpps(shuf2, shuf1, (unsigned char)((12 << 4) | 3));
	v4sf expect4sf_2 = {5953314400000.0, 5953314400000.0, 0.0, 0.0};
	if (__builtin_ia32_pcmpestri128(*(v16qi *)(&expect4sf_2), 16, *(v16qi *)(&result4sf), 16, SUBSTR | UBYTES)) goto fail;

	// check next 256 bits
	v16hi dp = __builtin_ia32_pmaddwd256(params16hi[0], params16hi[1]);
	v16hi expect16hi = {16235, 17697, 20742, 16142, 14700, 13192, 46209, 16050, 58366, 17569, 50746, 14849, 312, 9925, 57332, 12695};
	if (__builtin_ia32_pcmpestri128(*(v16qi*)(&dp), 16, *(v16qi*)(&expect16hi), 16, SUBSTR | UBYTES)) goto fail;
	if (__builtin_ia32_pcmpestri128(((v16qi*)(&dp))[1], 16, ((v16qi*)(&expect16hi))[1], 16, SUBSTR | UBYTES)) goto fail;

	do {
		rdseed(&seed);
	} while ((seed & 0xff) != 228);
	v32qi search = {0xef, 0xbe, 0xad, 0xde, 0xde, 0xc0, 0x37, 0x13};
	v32qi result32qi = __builtin_ia32_mpsadbw256(*params32qi, search, 0);
	v16qi expect16qi = {14,2,67,2,76,2,25,2,2,1,167,1,170,1,151,1};
	expect16qi[8] = seed & 0xff;
	if (__builtin_ia32_pcmpestri128(*(v16qi *)(&expect16qi), 16, *(v16qi *)(&result32qi), 16, SUBSTR | UBYTES)) goto fail;
	result32qi = __builtin_ia32_mpsadbw256(*params32qi, search, 4 | 1);
	v16qi expect16qi2 = {136,1,95,1,90,1,89,1,46,1,30,1,97,1,71,1};
	if (__builtin_ia32_pcmpestri128(*(v16qi *)(&expect16qi2), 16, *(v16qi *)(&result32qi), 16, SUBSTR | UBYTES)) goto fail;

	// what the hell
	res = __builtin_ia32_pclmulqdq128(params16qi[3], params16qi[3], 0x10);
	v16qi shouldbe2 = {109, 247, 219, 94, 35, 204, 117, 41, 211, 17, 186, 227, 73, 87, 36, 16};
	if (__builtin_ia32_pcmpestri128(shouldbe2, 16, res, 16, SUBSTR | UBYTES)) goto fail;

	// idk anymore
	v8hi lastres = __builtin_ia32_phminposuw128(params16qi[3]);
	do {
		rdseed(&seed);
	} while ((seed & 0xffff) != lastres[0]);
	if ((seed & 0xffff) != 13156ULL) goto fail;
	if (lastres[1] != 5) goto fail;

	puts("yeah");
	return 0;
fail:
	puts("nah");
	return 0;
}
