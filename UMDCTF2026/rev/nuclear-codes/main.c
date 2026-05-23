#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <mpc.h>

const mpfr_prec_t PREC = 10000;

#define NUMARGS_(_,_1,_2,_3,_4,_5,_6,_7,_8,_9,_10,N,...) N
#define NUMARGS(...) NUMARGS_(,##__VA_ARGS__,10,9,8,7,6,5,4,3,2,1,0)
#define EACH0(f,x,...)
#define EACH1(f,x,...) f(x); EACH0(f,__VA_ARGS__)
#define EACH2(f,x,...) f(x); EACH1(f,__VA_ARGS__)
#define EACH3(f,x,...) f(x); EACH2(f,__VA_ARGS__)
#define EACH4(f,x,...) f(x); EACH3(f,__VA_ARGS__)
#define EACH5(f,x,...) f(x); EACH4(f,__VA_ARGS__)
#define EACH6(f,x,...) f(x); EACH5(f,__VA_ARGS__)
#define EACH_(n,f,...) EACH ## n (f,__VA_ARGS__)
#define EACH(n,f,...) EACH_(n,f,__VA_ARGS__)

#define PRINT(a) mpc_out_str(stdout, 10, 25, a, MPC_RNDNN);
#ifdef DO_DUMP
int indent = 0;
#define DBG(prefix, ...) for (int __i=0;__i<indent;putchar(' '),__i++){} printf(prefix " "); EACH(NUMARGS(__VA_ARGS__), PRINT, __VA_ARGS__); puts("")
#define START(prefix, ...) DBG(prefix, __VA_ARGS__);indent++
#define END(prefix, dst) indent--;DBG("END " prefix, dst)
#else
#define DBG(prefix, ...)
#define START(prefix, ...)
#define END(prefix, ...)
#endif

#define OUT(prefix, ...) printf(prefix " "); EACH(NUMARGS(__VA_ARGS__), PRINT, __VA_ARGS__); puts("");

#define TMP(x) tmp##x
#define WITH_TMP(tag, body) body

#define EXP(dst, a) START("EXP", a); eml(dst, a, ONE); END("EXP", dst)

#define LOG(dst, a) START("LOG", a); eml(dst, ONE, a); EXP(dst, dst); eml(dst, ONE, dst); END("LOG", dst)

#define ZERO(dst) START("ZERO"); LOG(dst, ONE); END("ZERO", dst)

#define SUB_(dst, a, b, tag, ...) LOG(TMP(tag), a); EXP(dst, b); eml(dst, TMP(tag), dst)
#define SUB(dst, a, b, ...) START("SUB", a, b); SUB_(dst, a, b, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("SUB", dst)

#define NEG_(dst, a, tag, ...) ZERO(TMP(tag)); SUB(dst, TMP(tag), a, ##__VA_ARGS__)
#define NEG(dst, a, ...) START("NEG", a); NEG_(dst, a, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("NEG", dst)

#define ADD_(dst, a, b, tag, ...) NEG(TMP(tag), b, ##__VA_ARGS__); SUB(dst, a, TMP(tag), ##__VA_ARGS__)
#define ADD(dst, a, b, ...) START("ADD", a, b); ADD_(dst, a, b, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("ADD", dst)

#define INV(dst, a, ...) START("INV", a); LOG(dst, a); NEG(dst, dst, ##__VA_ARGS__); EXP(dst, dst); END("INV", dst)

#define MUL_(dst, a, b, tag, ...) LOG(TMP(tag), b); LOG(dst, a); ADD(dst, dst, TMP(tag), ##__VA_ARGS__); EXP(dst, dst)
#define MUL(dst, a, b, ...) START("MUL", a, b); MUL_(dst, a, b, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("MUL", dst)

#define DIV_(dst, a, b, tag, ...) LOG(TMP(tag), b); LOG(dst, a); SUB(dst, dst, TMP(tag), ##__VA_ARGS__); EXP(dst, dst)
#define DIV(dst, a, b, ...) START("DIV", a, b); DIV_(dst, a, b, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("DIV", dst)

#define POW_(dst, a, b, tag, ...) LOG(TMP(tag), a); MUL(dst, b, TMP(tag), ##__VA_ARGS__); EXP(dst, dst)
#define POW(dst, a, b, ...) START("POW", a, b); POW_(dst, a, b, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("POW", dst)

#define TWO(dst, ...) START("TWO"); ADD(dst, ONE, ONE, ##__VA_ARGS__); END("TWO", dst)

#define NEG_ONE(dst, ...) START("NEG_ONE"); NEG(dst, ONE, ##__VA_ARGS__); END("NEG_ONE", dst)

#define COPIUM_ADD_(dst, a, b, tag, ...) DIV(TMP(tag), a, b, ##__VA_ARGS__); ADD(TMP(tag), TMP(tag), ONE, ##__VA_ARGS__); MUL(dst, TMP(tag), b, ##__VA_ARGS__)
#define COPIUM_ADD(dst, a, b, ...) START("COPIUM_ADD", a, b); COPIUM_ADD_(dst, a, b, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("COPIUM_ADD", dst)

#define COPIUM_NEG_(dst, a, tag, ...) NEG_ONE(TMP(tag), ##__VA_ARGS__); MUL(dst, TMP(tag), a, ##__VA_ARGS__)
#define COPIUM_NEG(dst, a, ...) START("COPIUM_NEG", a); COPIUM_NEG_(dst, a, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("COPIUM_NEG", dst)

#define COPIUM_SUB_(dst, a, b, tag, ...) DIV(TMP(tag), a, b, ##__VA_ARGS__); SUB(TMP(tag), TMP(tag), ONE, ##__VA_ARGS__); MUL(dst, TMP(tag), b, ##__VA_ARGS__)
#define COPIUM_SUB(dst, a, b, ...) START("COPIUM_SUB", a, b); COPIUM_SUB_(dst, a, b, NUMARGS(__VA_ARGS__), X, ##__VA_ARGS__); END("COPIUM_SUB", dst)

void eml(mpc_t dst, mpc_t a, mpc_t b) {
	mpc_t tmp;
	mpc_init2(tmp, PREC);
	DBG("a,b =", a, b);
	mpc_exp(tmp, a, MPC_RNDNN);
	mpc_log(dst, b, MPC_RNDNN);
	mpc_sub(dst, tmp, dst, MPC_RNDNN);
	DBG("exp(a) - ln(b) =", dst);
	mpc_clear(tmp);
}

int is_positive(const char* s) {
	size_t length = strlen(s);

	int seen_nonzero = 0;

	for (size_t i = 0; i < length; i++) {
		if (!isdigit(s[i])) {
			return 0;
		}
		seen_nonzero |= s[i] != '0';
	}
	return seen_nonzero;
}

int main() {
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	char in1[501], in2[501], in3[501];
	printf("enter positive integers a,b,c; one per line:\n");
	if (fgets(in1, 501, stdin) == NULL) {
		printf("could not read input\n");
	}
	if (fgets(in2, 501, stdin) == NULL) {
		printf("could not read input\n");
	}
	if (fgets(in3, 501, stdin) == NULL) {
		printf("could not read input\n");
	}
	in1[strcspn(in1, "\n")] = 0;
	in2[strcspn(in2, "\n")] = 0;
	in3[strcspn(in3, "\n")] = 0;

	if (!is_positive(in1) || !is_positive(in2) || !is_positive(in3)) {
		printf("inputs should be positive integers\n");
		return 1;
	}
	char buf1[501], buf2[501], buf3[501];
	memset(buf1, '0', 501);
	memset(buf2, '0', 501);
	memset(buf3, '0', 501);
	strcpy(buf1 + 500 - strlen(in1), in1);
	strcpy(buf2 + 500 - strlen(in2), in2);
	strcpy(buf3 + 500 - strlen(in3), in3);
	if (strcmp(buf1, buf2) <= 0 || strcmp(buf2, buf3) <= 0) {
		printf("need a > b > c\n");
		return 1;
	}

	mpc_t ONE, a, b, c, x1, x2, x3, tmp0, tmp1, tmp2, tmp3, tmp4;
	mpc_init2(ONE, PREC);
	mpc_init2(a, PREC);
	mpc_init2(b, PREC);
	mpc_init2(c, PREC);
	mpc_init2(x1, PREC);
	mpc_init2(x2, PREC);
	mpc_init2(x3, PREC);
	mpc_init2(tmp0, PREC);
	mpc_init2(tmp1, PREC);
	mpc_init2(tmp2, PREC);
	mpc_init2(tmp3, PREC);
	mpc_init2(tmp4, PREC);
	mpc_set_ui(ONE, 1, MPC_RNDNN);
	mpc_set_str(a, in1, 10, MPC_RNDNN);
	mpc_set_str(b, in2, 10, MPC_RNDNN);
	mpc_set_str(c, in3, 10, MPC_RNDNN);

	COPIUM_SUB(x1,a,c);
	DIV(x1,a,x1);
	COPIUM_ADD(x2,a,b);
	COPIUM_SUB(x3,a,b);
	COPIUM_SUB(x2,x2,c);
	DIV(x2,x3,x2);
	COPIUM_ADD(x1,x1,x2);
	COPIUM_SUB(x2,b,c);
	COPIUM_ADD(x3,a,x3);
	DIV(x3,x2,x3);
	COPIUM_ADD(x1,x3,x1);
	ADD(x2,ONE,ONE);
	ADD(x3,x2,x2);
	ADD(x3,x2,x3);
	SUB(x1,x1,x3);

	// OUT("out", x1);

	ADD(x2,ONE,ONE); // 2
	ADD(x2,x2,x2); // 4
	MUL(x2,x2,x2); // 16
	MUL(x2,x2,x2); // 256
	POW(x2,x2,x2); // 2^2048
	MUL(x2,x2,x2); // 2^4096
	INV(x2,x2); // 2^-4096
	// OUT("eps", x2);

	if (mpc_cmp_abs(x1, x2) >= 0) {
		printf("incorrect\n");
		return 1;
	}

	FILE *fp = fopen("flag.txt", "r");
	if (fp == NULL) {
		printf("Could not open flag file. If you're seeing this error on remote, open a ticket.\n");
		return 1;
	}
	if (fgets(buf1, 501, fp) == NULL) {
		printf("Could not read flag file. If you're seeing this error on remote, open a ticket.\n");
		return 1;
	}
	printf("flag: %s\n", buf1);

	return 0;
}
