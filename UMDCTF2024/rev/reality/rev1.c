#include<stdio.h>
#include<stdlib.h>
#include<math.h>

struct used_mem {
    float op;
    float d1;
    float d2; 
    float location;
    struct used_mem *fd;
    struct used_mem *bk;
};

float traverse_exactly(struct used_mem ** ptr, float dest) {
    if ((*ptr)->location < dest) {
        while ((*ptr)->fd != NULL && (*ptr)->location < dest) {
            (*ptr) = (*ptr)->fd;
        }
    } else {
        while ((*ptr)->bk != NULL && (*ptr)->location > dest) {
            (*ptr) = (*ptr)->bk;
        }
    }
    if ((*ptr)->location != dest) {
        return 1.0f;
    }

    return 0.0f;
}

void traverse_and_create_block(struct used_mem ** ptr, float dst) {
    if ((*ptr)->location < dst) {
        while ((*ptr)->fd != NULL && (*ptr)->location < dst) {
            (*ptr) = (*ptr)->fd;
        }
        if ((*ptr)->location != dst && (*ptr)->fd != NULL) {
            struct used_mem * gen = malloc(sizeof(struct used_mem));
            gen->fd = (*ptr);
            gen->bk = (*ptr)->bk;
            (*ptr)->bk = gen;
            gen->bk->fd = gen;
            gen->d1 = 0.0f;
            gen->d2 = 0.0f;
            gen->op = 0.0f;
            gen->location = dst;
            (*ptr) = gen;
        } else if ((*ptr)->location != dst && (*ptr)->fd == NULL) {
            struct used_mem * gen = malloc(sizeof(struct used_mem));
            gen->bk = (*ptr);
            (*ptr)->fd = gen;
            gen->d1 = 0.0f;
            gen->d2 = 0.0f;
            gen->op = 0.0f;
            gen->location = dst;
            (*ptr) = gen;
        }
    } else {
        while ((*ptr)->bk != NULL && (*ptr)->location > dst) {
            (*ptr) = (*ptr)->bk;
        }
        if ((*ptr)->location != dst && (*ptr)->bk != NULL) {
            struct used_mem * gen = malloc(sizeof(struct used_mem));
            gen->bk = (*ptr);
            gen->fd = (*ptr)->fd;
            (*ptr)->fd = gen;
            gen->fd->bk = gen;
            gen->d1 = 0.0f;
            gen->d2 = 0.0f;
            gen->op = 0.0f;
            gen->location = dst;
            (*ptr) = gen;
        } else if ((*ptr)->location != dst && (*ptr)->bk == NULL) {
            struct used_mem * gen = malloc(sizeof(struct used_mem));
            gen->fd = (*ptr);
            (*ptr)->bk = gen;
            gen->d1 = 0.0f;
            gen->d2 = 0.0f;
            gen->op = 0.0f;
            gen->location = dst;
            (*ptr) = gen;
        }
    }
}

void map_into_space(struct used_mem ** ptr, float * prog, float * d1, float * d2, int len) {

    for (int i = 1; i < len; i++) {
        float location = sinf(i) / (i + 1.0f);

        struct used_mem *gen = malloc(sizeof(struct used_mem));
        gen->location = location;
        gen->d1 = d1[i];
        gen->d2 = d2[i];
        gen->op = prog[i];

        float out = traverse_exactly(ptr, location);

        if (out != 1.0f) {
            printf("Error.\n");
            return;
        }

        if ((*ptr)->location > location) {
            gen->fd = (*ptr);
            if ((*ptr)->bk != NULL) {
                (*ptr)->bk->fd = gen;
                gen->bk = (*ptr)->bk;
            }
            (*ptr)->bk = gen;
        } else {
            gen->bk = (*ptr);
            if ((*ptr)->fd != NULL) {
                (*ptr)->fd->bk = gen;
                gen->fd = (*ptr)->fd;
            }
            (*ptr)->fd = gen;
        }

    }

    traverse_exactly(ptr, -1.0f);
}

float vm_step(struct used_mem ** ip) {
    if ((*ip)->op == 00.0f) {
    } else if ((*ip)->op == -3.141f) {
        if ((*ip)->d1 == 00.0f) {
            return 1.3f;
        }
        return (*ip)->d1;
    } else if ((*ip)->op == 10.103f) {

        // Move A[D1].d1 into A[D2].d1

        float get = (*ip)->d1;
        float dst = (*ip)->d2;
        struct used_mem * traversal = (*ip);
        traverse_exactly(&traversal, get);

        float data = traversal->d1;

        traverse_and_create_block(&traversal, dst);

        traversal->d1 = data;


    } else if ((*ip)->op == 23.221891f) {

        // A[D2].d1 += A[D1].d1

        float get = (*ip)->d1;
        float dst = (*ip)->d2;
        struct used_mem * traversal = (*ip);
        traverse_exactly(&traversal, get);

        float data = traversal->d1;

        traverse_and_create_block(&traversal, dst);

        traversal->d1 += data;

    } else if ((*ip)->op == 21.8917f) {

        // A[D2].d1 -= A[D1].d1

        float get = (*ip)->d1;
        float dst = (*ip)->d2;
        struct used_mem * traversal = (*ip);
        traverse_exactly(&traversal, get);

        float data = traversal->d1;

        traverse_and_create_block(&traversal, dst);

        traversal->d1 -= data;

    } else if ((*ip)->op == 22.3313f) {

        // A[D2].d1 *= A[D1].d1

        float get = (*ip)->d1;
        float dst = (*ip)->d2;
        struct used_mem * traversal = (*ip);
        traverse_exactly(&traversal, get);

        float data = traversal->d1;

        traverse_and_create_block(&traversal, dst);

        traversal->d1 *= data;

    } else if ((*ip)->op == 20.32f) {

        // A[D2].d1 = sign A[D1].d1

        float get = (*ip)->d1;
        float dst = (*ip)->d2;
        struct used_mem * traversal = (*ip);
        traverse_exactly(&traversal, get);

        float data = traversal->d1;

        traverse_and_create_block(&traversal, dst);

        traversal->d1 = (float)((data > 0) - (data < 0));

    } else if ((*ip)->op == 28.393f) {
        float get = (*ip)->d1;
        struct used_mem * traversal = (*ip);
        traverse_exactly(&traversal, get);

        float data = traversal->d1;
        traversal->d1 = traversal->d2;
        traversal->d2 = traversal->op;
        traversal->op = data;

    } else if ((*ip)->op == 8329.113f) {
        float cmp = (*ip)->d1;
        float swp = (*ip)->d2;
        struct used_mem * traversal = (*ip);
        float out = traverse_exactly(&traversal, cmp);
        if (out == 1.0f) {
            return 1.4f;
        } else {
            if (traversal->d1 != 0.0f) {
                traversal->d1 = swp;
            }
        }

    } else if ((*ip)->op == 22.190f) {
        float jmpto = (*ip)->d1;
        struct used_mem * traversal = (*ip);
        float out = traverse_exactly(&traversal, jmpto);
        if (out == 1.0f) {
            return 1.5f;
        } else {
            (*ip) = traversal->bk;
        }
    } else if ((*ip)->op == 4554.1337f) {
        float store_loc = (*ip)->d1;
        struct used_mem * traversal = (*ip);
        traverse_and_create_block(&traversal, store_loc);
        char inp[30];
        fgets(inp, 30, stdin);
        traversal->d1 = atof(inp);

    } else {
        return 1.6f;
    }

    (*ip) = (*ip)->fd;
    return 0.0f;
}

float vm_execute(float * prog, float * d1, float * d2, int len) {

    struct used_mem * init = malloc(sizeof(struct used_mem));
    init->op = prog[0];
    init->d1 = d1[0];
    init->d2 = d2[0];
    init->location = -1.0f;

    map_into_space(&init, prog, d1, d2, len);

    float out = 00.0f;
    struct used_mem ** ip = &init;

    while (out == 00.0f) {
        out = vm_step(ip);
    }

    return out;
}

int main() {

	setvbuf(stdout, NULL, _IOLBF, BUFSIZ);

    // { prog }
    // { d1 }
    // { d2 }
    // { size }  

    printf("Welcome to reality.\n");

    float out = vm_execute(prog, d1, d2, size);

    if (out == 40) {
        FILE *f;
        f = fopen("flag.txt", "r");
        if (f == NULL) {
            puts("Couldn't open flag file.");
            exit(1);
        }
        char flag[128];
        if (fgets(flag, sizeof(flag), f) == NULL) {
            puts("Couldn't read flag file.");
            exit(1);
        }
        fclose(f);
        puts(flag);
        exit(0);
    }
}
