#include "tea.h"
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

extern uint8_t __xtext_start[];
extern uint8_t __xtext_end[];
extern uint8_t __chk_start[];
extern uint8_t __chk_end[];

/* Raw mprotect syscall so the binary doesn't import the libc symbol. */
#define SYS_mprotect 10

static long raw_syscall3(long n, long a, long b, long c){
    long ret;
    asm volatile("syscall"
                 : "=a"(ret)
                 : "0"(n), "D"(a), "S"(b), "d"(c)
                 : "rcx", "r11", "memory");
    return ret;
}

/* KXK_M is XOR-masked by KXK_MASK and by the build-time chk-section hash;
   main re-hashes chk and XORs back to recover the real TEA key, so any
   byte patch inside chk desynchronises the key and .xtext decrypts to
   garbage. `volatile` keeps the storage in .rodata so encrypt_kitext.py's
   post-link placeholder patch survives -O2 constant-folding. */
static volatile const uint32_t KXK_M[4] = {
    0xAA550001u, 0xAA550002u, 0xAA550003u, 0xAA550004u
};
static const uint32_t KXK_MASK[4] = {
    0x12345678u, 0x9abcdef0u, 0xfedcba98u, 0x87654321u
};
static const uint8_t KXV_M[8] = {
    0x5a, 0x4b, 0x78, 0x69, 0x1e, 0x0f, 0x3c, 0x2d
};

extern int chk_is_traced(void);

static uint32_t chk_hash(const uint8_t *begin, const uint8_t *end){
    uint32_t h = 0xC0DEF1ABu;
    for(const uint8_t *p = begin; p < end; p++){
        h ^= *p;
        h *= 0x5BD1E995u;
        h ^= h >> 15;
    }
    return h;
}

int main(int argc, char **argv){
    uint32_t h = chk_hash(__chk_start, __chk_end);
    int traced = chk_is_traced();

    volatile uint8_t vmk = 0x5a;
    uint8_t mk = vmk;
    uint32_t k[4];
    for(int i = 0; i < 4; i++)
        k[i] = KXK_M[i] ^ KXK_MASK[i] ^ h;
    if(traced) k[0] ^= 0xDEADBEEFu;

    uint8_t iv[8];
    for(int i = 0; i < 8; i++) iv[i] = KXV_M[i] ^ mk;

    size_t len = (size_t)(__xtext_end - __xtext_start);
    uintptr_t start = (uintptr_t)__xtext_start;
    long ps = sysconf(_SC_PAGESIZE);
    uintptr_t page_start = start & ~(uintptr_t)(ps - 1);
    size_t page_len = ((start + len) - page_start + (size_t)ps - 1) & ~(size_t)(ps - 1);

    if(raw_syscall3(SYS_mprotect, (long)page_start, (long)page_len, 7) != 0)
        _exit(3);
    tea_cfb_decrypt(k, iv, (uint8_t*)__xtext_start, len);
    if(raw_syscall3(SYS_mprotect, (long)page_start, (long)page_len, 5) != 0)
        _exit(3);

    extern int __attribute__((section(".xtext"))) x_entry(int argc, char **argv);
    return x_entry(argc, argv);
}
