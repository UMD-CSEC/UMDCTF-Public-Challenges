/*
 * Compile: clang -o loader loader.c
 */

#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/ptrace.h>
#include <unistd.h>

int (*cleffa)();

char shellcode[] = "\x61\x6f\x8c\xf2\x81\xca\xa8\xf2\x81\x68\xc8\xf2\xa1\xaa\xe9\xf2\xe1\x83\x1f\xf8\x81\x0d\x86\xf2\x81\xe6\xab\xf2\xc1\xcc\xcc\xf2\x81\xad\xec\xf2\xe1\x03\x1f\xf8\x61\x86\x8d\xf2\xa1\x06\xad\xf2\x61\xee\xcb\xf2\xc1\x6e\xe6\xf2\xe1\x83\x1e\xf8\x21\xa4\x8f\xf2\x61\x26\xa4\xf2\x01\x86\xcc\xf2\x81\x6d\xec\xf2\xe1\x03\x1e\xf8\x01\x04\x80\xd2\xa1\x15\x02\xd4";

// Decrypt Shellcode
// Iterate over shellcode and apply user changes
// Run the shellcode
// Profit

// Flag: UMDCTF{cleff4_l0v3s_5h3llc0d3}

int main(int argc, char **argv)
{
    printf("\033[95m ██████╗██╗     ███████╗███████╗███████╗ █████╗ ███████╗    \033[0m\n");
    printf("\033[95m██╔════╝██║     ██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝    \033[0m\n");
    printf("\033[95m██║     ██║     █████╗  █████╗  █████╗  ███████║███████╗    \033[0m\n");
    printf("\033[95m██║     ██║     ██╔══╝  ██╔══╝  ██╔══╝  ██╔══██║╚════██║    \033[0m\n");
    printf("\033[95m╚██████╗███████╗███████╗██║     ██║     ██║  ██║███████║    \033[0m\n");
    printf("\033[95m ╚═════╝╚══════╝╚══════╝╚═╝     ╚═╝     ╚═╝  ╚═╝╚══════╝    \033[0m\n");
    printf("\033[95m                                                            \033[0m\n");
    printf("\033[95m███████╗██╗   ██╗██████╗ ██████╗ ██████╗ ██╗███████╗███████╗\033[0m\n");
    printf("\033[95m██╔════╝██║   ██║██╔══██╗██╔══██╗██╔══██╗██║██╔════╝██╔════╝\033[0m\n");
    printf("\033[95m███████╗██║   ██║██████╔╝██████╔╝██████╔╝██║███████╗█████╗  \033[0m\n");
    printf("\033[95m╚════██║██║   ██║██╔══██╗██╔═══╝ ██╔══██╗██║╚════██║██╔══╝  \033[0m\n");
    printf("\033[95m███████║╚██████╔╝██║  ██║██║     ██║  ██║██║███████║███████╗\033[0m\n");
    printf("\033[95m╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝\033[0m\n");

    ptrace(PT_DENY_ATTACH, 0, 0, 0);

    void *ptr = mmap(0, 0x1000, PROT_WRITE | PROT_READ, MAP_ANON | MAP_PRIVATE | MAP_JIT, -1, 0);
    if (ptr == MAP_FAILED)
    {
        exit(-1);
    }

    void *dst = memcpy(ptr, shellcode, sizeof(shellcode));
    int status = mprotect(ptr, 0x1000, PROT_EXEC | PROT_READ);

    if (status == -1)
    {
        exit(-1);
    }

    cleffa = ptr;
    cleffa();

    return 0;
}
