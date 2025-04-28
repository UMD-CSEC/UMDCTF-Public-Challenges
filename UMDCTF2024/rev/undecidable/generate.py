import random

start = """#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define get(s) ((s<0)?neg[-(s)/8]&(1<<((-(s))%8)):pos[s/8]&(1<<((s)%8)))
int64_t lb = -10000, ub = 10000; unsigned char *pos, *neg;
"""

with open("generated.c", "w") as f, open("combined.txt") as g:
	lines = g.read().splitlines()
	n_lines = len(lines)
	mapping = list(range(1, n_lines + 1))
	random.shuffle(mapping)
	mapping.insert(0, 0)
	f.write(start)
	f.write("void (*fps[" + str(len(mapping)) + "])(int64_t);\n")
	f.write("void bounds(int64_t s) {if (s/8 < lb) {neg = realloc(neg, -lb*2); memset(neg-lb, 0, -lb); lb *= 2;} if (s/8 > ub) {pos = realloc(pos, ub*2); memset(pos+ub, 0, ub); ub *= 2;}};\n")
	f.write("void flip(int64_t s) {if (s<0) {neg[-(s)/8]^=(1<<((-(s))%8));} else {pos[s/8]^=(1<<((s)%8));}};\n")
	f.write('void fp_0(int64_t s) { puts("correct"); exit(0); }\n')
	for i in range(1, len(mapping)):
		f.write("void fp_" + str(i) + "(int64_t s) { bounds(s); ")
		i = mapping.index(i)
		state, w0, d0, n0, w1, d1, n1 = lines[i-1].split()
		f.write("if(get(s)){ " + ["flip(s); ", ""][w1=='1'] + "s" + '-+'[d1=='R'] + "=1; fps[" + str(mapping[int(n1)]) + "](s); }")
		f.write(" else { "     + ["", "flip(s); "][w0=='1'] + "s" + '-+'[d0=='R'] + "=1; fps[" + str(mapping[int(n0)]) + "](s); }")
		f.write("}\n")
	f.write("void (*fps[" + str(len(mapping)) + "])(int64_t) = {" + ",".join(f"fp_{i}" for i in range(len(mapping))) + "};\n")
	f.write("int main(int argc, char** argv) { ")
	f.write('if (argc < 2) { printf("usage: %s <flag>\\n", argv[0]); exit(0); } ')
	f.write("neg = calloc(-lb, 1); pos = calloc(ub, 1); flip((-1)); ")
	f.write("for (char* c = argv[1]; *c; c++) { for (int i = 0; i < 8; i++) { if ((*c)&(1<<i)) { flip((2*((c-argv[1])*8+i))); } } } flip((strlen(argv[1])*16-1));")
	f.write("fps["+str(mapping[1])+"](0); ")
	f.write("return 0; }")