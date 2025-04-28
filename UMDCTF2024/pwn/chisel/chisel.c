#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

enum choice {
    ALLOC = 1,
    FREE = 2,
    EDIT = 3,
    PRINT = 4,
    CHISEL = 5,
    EXIT = 6
};

long read_long(void) {
    char buf[20];
    fgets(buf, sizeof(buf), stdin);
    return atol(buf);
}

enum choice prompt(void) {
    printf("1) Alloc\n");
    printf("2) Free\n");
    printf("3) Edit\n");
    printf("4) Print\n");
    printf("5) Chisel\n");
    printf("6) Exit\n");
    printf("> ");

    return read_long();
}

int main(void) {
    long *chunk = NULL;

    setbuf(stdin, NULL);
    setbuf(stdout, NULL);

    while(1) {
        switch (prompt()) {
        case ALLOC:
            printf("size: ");
            chunk = malloc(read_long());
            break;
        case FREE:
            free(chunk);
            break;
        case EDIT:
            printf("data: ");
            *chunk = read_long();
            break;
        case PRINT:
            printf("data: %ld\n", *chunk);
            break;
        case CHISEL:
            malloc(0x500 - 8);
            break;
        default:
            goto done;
        }
    }
done:
    printf("cya!\n");

    return 0;
}
