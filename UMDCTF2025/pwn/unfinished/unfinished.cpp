#include <cstdio>
#include <cstdlib>

char number[128];

void sigma_mode() {
    system("/bin/sh");
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    printf("What size allocation?\n");
    fgets(number, 500, stdin);

    long n = atol(number);
    int *chunk = new int[n];
    // TODO: finish the heap chal
}
