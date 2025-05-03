#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>

#define THE_CHUNK_SIZE (0x600-8)
#define NUM_CHUNKS 100
#define MAX_SIZE 0x600

char *the_chunk = NULL;
char *chunks[NUM_CHUNKS] = {0};

void my_print(char *str) {
    size_t len = strlen(str);
    write(STDOUT_FILENO, str, len);
}

int get_int(void) {
    char buf[16];
    size_t len = read(STDIN_FILENO, buf, sizeof(buf));
    return atoi(buf);
}

int prompt(void) {
    my_print("1. Alloc\n");
    my_print("2. Free\n");
    my_print("3. Write\n");
    my_print("4. Show\n");
    my_print("5. Exit\n");
    my_print("> ");

    return get_int();
}

void alloc_chunk(void) {
    my_print("idx: ");
    uint32_t idx = get_int();
    if (idx >= NUM_CHUNKS)
        _exit(1);

    my_print("size: ");
    uint32_t size = get_int();
    if (size >= 0x600)
        _exit(1);

    chunks[idx] = malloc(size);

    my_print("done!\n");
    my_print("...what? did you think you would get a write?\n");
}

void free_chunk(void) {
    my_print("idx: ");
    uint32_t idx = get_int();
    if (idx >= NUM_CHUNKS)
        _exit(1);

    free(chunks[idx]);
}

void write_chunk(void) {
    my_print("data: ");
    read(STDIN_FILENO, the_chunk, THE_CHUNK_SIZE);
}

void read_chunk(void) {
    write(STDOUT_FILENO, the_chunk, THE_CHUNK_SIZE);
}

int main(void) {
    the_chunk = malloc(THE_CHUNK_SIZE);
    free(the_chunk);

    while (1) {
        switch (prompt()) {
        case 1:
            alloc_chunk();
            break;
        case 2:
            free_chunk();
            break;
        case 3:
            write_chunk();
            break;
        case 4:
            read_chunk();
            break;
        default:
            _exit(1);
            break;
        }
    }
}
