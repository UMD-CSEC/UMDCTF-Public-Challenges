/* Lives in section "chk", whose bytes are FNV-hashed by main() and folded
   into the .xtext decryption key. Uses only raw syscalls + local static
   data so there are no GOT/PLT relocations — the on-disk bytes match the
   in-memory bytes, and a byte-level patch here breaks the key. */
#include <stdint.h>
#include <stddef.h>

#define CHK __attribute__((section("chk"), noinline))

/* "/proc/self/status\0" XOR 0x5A */
static const uint8_t PS_OBF[] = {
    0x75,0x2a,0x28,0x35,0x39,0x75,0x29,0x3f,
    0x36,0x3c,0x75,0x29,0x2e,0x3b,0x2e,0x2f,0x29,0x5a
};
/* "TracerPid:" XOR 0x5A */
static const uint8_t TG_OBF[] = {
    0x0e,0x28,0x3b,0x39,0x3f,0x28,0x0a,0x33,0x3e,0x60
};

#define SYS_read     0
#define SYS_open     2
#define SYS_close    3
#define SYS_ptrace 101

static long CHK sc3(long n, long a, long b, long c){
    long ret;
    asm volatile("syscall"
                 : "=a"(ret)
                 : "0"(n), "D"(a), "S"(b), "d"(c)
                 : "rcx", "r11", "memory");
    return ret;
}
static long CHK sc4(long n, long a, long b, long c, long d){
    register long r10 asm("r10") = d;
    long ret;
    asm volatile("syscall"
                 : "=a"(ret)
                 : "0"(n), "D"(a), "S"(b), "d"(c), "r"(r10)
                 : "rcx", "r11", "memory");
    return ret;
}

/* Order matters: read /proc/self/status BEFORE PTRACE_TRACEME. Once
   TRACEME succeeds the parent becomes the kernel-recorded tracer and
   TracerPid flips non-zero even for a normal shell parent. */
int CHK chk_is_traced(void){
    volatile uint8_t vm = 0x5a;
    uint8_t m = vm;
    char path[sizeof(PS_OBF)];
    for(size_t i = 0; i < sizeof(PS_OBF); i++) path[i] = (char)(PS_OBF[i] ^ m);

    long fd = sc3(SYS_open, (long)path, 0 /*O_RDONLY*/, 0);
    if(fd >= 0){
        char buf[4096];
        long n = sc3(SYS_read, fd, (long)buf, (long)(sizeof(buf) - 1));
        sc3(SYS_close, fd, 0, 0);
        if(n > 0){
            buf[n] = 0;
            char tag[sizeof(TG_OBF)];
            for(size_t i = 0; i < sizeof(TG_OBF); i++) tag[i] = (char)(TG_OBF[i] ^ m);
            const char *p = buf;
            while(*p){
                int match = 1;
                for(size_t i = 0; i < sizeof(tag); i++)
                    if(p[i] != tag[i]){ match = 0; break; }
                if(match){
                    p += sizeof(tag);
                    while(*p == ' ' || *p == '\t') p++;
                    int v = 0;
                    while(*p >= '0' && *p <= '9'){ v = v*10 + (*p - '0'); p++; }
                    if(v != 0) return 1;
                    break;
                }
                while(*p && *p != '\n') p++;
                if(*p) p++;
            }
        }
    }

    /* PTRACE_TRACEME also blocks later external attaches once it succeeds. */
    if(sc4(SYS_ptrace, 0, 0, 0, 0) == -1) return 1;
    return 0;
}
