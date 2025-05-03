#include <stdio.h>
#include <stdlib.h>

#define N 10000
#define BINS 10

int compare (const void *a, const void *b) { return *(float*)a == *(float*)b ? 0 : *(float*)a > *(float*)b ? 1 : -1; }

void vuln() {
	float data[N];
	short counts[BINS] = {0};
	printf("Enter %d floats: ", N);
	for (int i = 0; i < N; i++) {
		if (scanf("%f", &data[i]) < 1) {
			puts("not enough data");
			exit(-1);
		}
	}
	qsort(data, N, sizeof(float), compare);
	float min = data[0], max = data[N-1];
	for (int i = 0; i < N; i++) {
		int bin = BINS * (data[i] - min) / (max - min);
		counts[bin]++;
	}
	puts("Histogram below:");
	for (int i = 0; i < BINS; i++) {
		printf("%d ", i);
		for (short j = 0; j < counts[i]; j++) putchar('#');
		putchar('\n');
	}
}

int main() {
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
	vuln();
}