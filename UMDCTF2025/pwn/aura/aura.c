#include <stdio.h>
#include <unistd.h>

int aura = 0;

int main(int argc, char **argv) {
        setbuf(stdin, NULL);
        setbuf(stdout, NULL);
        setbuf(stderr, NULL);

        printf("my aura: %p\nur aura? ", &aura);

        char flag[17];
        FILE *fp = fopen("/dev/null", "r");

        read(0, fp, 0x100);

        char buf[0x100];
        fread(buf, 1, 8, fp);

        if (aura) {
                FILE *f = fopen("flag.txt", "r");
                fread(flag, 1, 17, f);
                printf("%s\n ", flag);
        }  else {
                printf("u have no aura.\n");
        }

        return 0;
}

