#ifndef VM_H
#define VM_H
#include <stdint.h>
#include <stddef.h>

enum {
    VG_INNER_MSG = 0,       /* ticket content — the only exposed global */
    VG_COUNT = 1
};

enum {
    NH_HASH_X = 2,          /* (bstr) -> bstr32 */
    NH_COUNT = 5
};

typedef enum { VT_INT = 0, VT_BSTR = 1 } vt_tag;
typedef struct {
    vt_tag tag;
    int64_t i;
    const uint8_t *b;     /* VT_BSTR: arena-owned */
    uint32_t n;
} vm_val;

typedef struct {
    const uint8_t *inner_msg; uint32_t inner_msg_len;
} vm_context;

typedef struct {
    char name[32];
    const uint8_t *bytes;
    uint32_t const_count;
    const uint8_t **const_ptrs;
    uint32_t     *const_lens;
    const uint8_t *code;
    uint32_t code_len;
} vm_class;

#define VM_REG_COUNT 16

typedef struct vm {
    vm_class *classes;
    uint32_t n_classes;
    vm_context ctx;
    uint8_t *arena;
    size_t arena_cap;
    size_t arena_used;
    uint32_t regs[VM_REG_COUNT];
} vm;

/* Shared with blob.c for archive-body obfuscation. */
void mwc_decrypt(uint8_t *buf, size_t len, uint32_t magic_xor);

/* Parse a .vmc in place. For BC3B magic, decrypts body via MWC first. */
int vm_load_class(vm *V, const char *name, uint8_t *buf, size_t len);

int vm_run_main(vm *V, vm_val *out_final);
void vm_init(vm *V, size_t arena_bytes);
void vm_destroy(vm *V);

#endif
