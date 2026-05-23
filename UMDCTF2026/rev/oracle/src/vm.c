#include "vm.h"
#include "aes.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

/* Non-sequential opcode values; the assembler carries the same mapping. */
enum {
    OP_NOP        = 0x8A,
    OP_PUSH_I32   = 0x37,  /* +i32 */
    OP_PUSH_I64   = 0x6B,  /* +i64 */
    OP_PUSH_CONST = 0x9F,  /* +u16 const_idx */
    OP_PUSH_GLB   = 0xA2,  /* +u8 global_idx */
    OP_POP        = 0x15,
    OP_DUP        = 0x28,
    OP_SWAP       = 0x4D,
    OP_ADD        = 0x52,
    OP_SUB        = 0x79,
    OP_XOR        = 0xB1,
    OP_AND        = 0xC6,
    OP_OR         = 0xD7,
    OP_EQ         = 0x3C,
    OP_NEQ        = 0x89,
    OP_LT         = 0x5E,
    OP_GT         = 0x71,
    OP_JMP        = 0x62,  /* +i16 */
    OP_JZ         = 0xAB,  /* +i16 */
    OP_JNZ        = 0xDC,  /* +i16 */
    OP_CONCAT     = 0x93,
    OP_SUBSTR     = 0x47,  /* (bstr, off, len) -> bstr */
    OP_LEN        = 0x2A,  /* (bstr) -> i32 */
    OP_NATIVE     = 0x58,  /* +u8 helper +u8 nargs */
    OP_INVOKE     = 0xE4,  /* +u8 class_idx +u8 nargs */
    OP_RET        = 0x1D,
    OP_HALT       = 0xFE,
    /* 32-bit arithmetic / bitwise */
    OP_SHL        = 0x0B,  /* pops count, val -> val << count  (u32) */
    OP_SHR        = 0x1F,  /* pops count, val -> val >> count  (u32, logical) */
    OP_MUL        = 0x24,  /* pops b, a   -> (a * b) mod 2^32 */
    OP_ROL        = 0x34,  /* pops count, val -> rotate_left_u32 */
    OP_ROR        = 0x43,  /* pops count, val -> rotate_right_u32 */
    /* Register file */
    OP_LOAD_REG   = 0x5A,  /* +u8 idx -- pushes regs[idx] as int */
    OP_STORE_REG  = 0x66,  /* +u8 idx -- pops val, regs[idx] = val (u32-trunc) */
    /* bstr <-> u32 conversions (little-endian) */
    OP_BSTR_LOAD_U32 = 0x7E, /* pops offset, bstr -> u32 at bstr[offset..offset+4] */
    OP_U32_TO_BSTR   = 0x8C, /* pops u32 -> 4-byte bstr (LE) */
};

/* MWC stream cipher. Shared with blob.c (archive-body obfuscation). */
void mwc_decrypt(uint8_t *buf, size_t len, uint32_t magic_xor)
{
    uint32_t s1 = (0x7FFF7FFFu - magic_xor) & 0xFFFFFFFFu;
    uint32_t s2 = magic_xor;
    for(size_t i=0;i<len;i++){
        s1 = ((s1 & 0xFFFFu) * 36969u + (s1 >> 16)) & 0xFFFFFFFFu;
        s2 = ((s2 >> 16) + (s2 & 0xFFFFu) * 18000u) & 0xFFFFFFFFu;
        buf[i] ^= (uint8_t)(s2 & 0xFFu);
    }
}

/* Class file format:
     magic[4]            : "CAFE..." plaintext, or "BC3B??" MWC-encrypted body
     const_count         : u16 LE
     code_len            : u32 LE
     consts[const_count] : {len: u16 LE, data: bytes[len]}
     code                : code_len bytes
   For BC3B classes the whole body (including const_count/code_len/lengths)
   is MWC-encrypted with seed = magic ^ 0xBEBAFECA. */

int vm_load_class(vm *V, const char *name, uint8_t *buf, size_t len)
{
    if(len < 10) return -1;

    uint32_t magic = (uint32_t)buf[0] | ((uint32_t)buf[1]<<8) |
                     ((uint32_t)buf[2]<<16) | ((uint32_t)buf[3]<<24);


    if(buf[0]==0xCA && buf[1]==0xFE){
        /* plaintext body */
    } else if(buf[0]==0xBC && buf[1]==0x3B){
        uint32_t magic_xor = magic ^ 0xBEBAFECAu;
        mwc_decrypt(buf + 4, len - 4, magic_xor);
    } else {
        return -2;
    }

    uint32_t const_count = (uint32_t)buf[4] | ((uint32_t)buf[5]<<8);
    uint32_t code_len = (uint32_t)buf[6] | ((uint32_t)buf[7]<<8) |
                        ((uint32_t)buf[8]<<16) | ((uint32_t)buf[9]<<24);

    uint32_t pos = 10;
    struct { uint32_t data_off; uint32_t data_len; } *cs =
        calloc(const_count, sizeof(*cs));
    if(!cs) return -3;
    for(uint32_t i=0; i<const_count; i++){
        if(pos + 2 > len){ free(cs); return -4; }
        uint32_t cl = (uint32_t)buf[pos] | ((uint32_t)buf[pos+1]<<8);
        pos += 2;
        if(pos + cl > len){ free(cs); return -5; }
        cs[i].data_off = pos;
        cs[i].data_len = cl;
        pos += cl;
    }
    if(pos + code_len > len){ free(cs); return -6; }
    uint32_t code_off = pos;

    V->classes = realloc(V->classes, sizeof(vm_class) * (V->n_classes + 1));
    vm_class *cl = &V->classes[V->n_classes++];
    memset(cl, 0, sizeof(*cl));
    size_t nlen = 0; while(nlen < sizeof(cl->name) - 1 && name[nlen]) nlen++;
    memcpy(cl->name, name, nlen); cl->name[nlen] = 0;
    cl->bytes = buf;
    cl->const_count = const_count;
    cl->const_ptrs = calloc(const_count, sizeof(uint8_t*));
    cl->const_lens = calloc(const_count, sizeof(uint32_t));
    for(uint32_t i=0; i<const_count; i++){
        cl->const_ptrs[i] = buf + cs[i].data_off;
        cl->const_lens[i] = cs[i].data_len;
    }
    cl->code = buf + code_off;
    cl->code_len = code_len;
    free(cs);
    return 0;
}

void vm_init(vm *V, size_t arena_bytes){
    memset(V, 0, sizeof(*V));   /* zero regs[] too */
    V->arena_cap = arena_bytes;
    V->arena = (uint8_t*)malloc(arena_bytes);
    V->arena_used = 0;
}
void vm_destroy(vm *V){
    for(uint32_t i=0;i<V->n_classes;i++){
        free(V->classes[i].const_ptrs);
        free(V->classes[i].const_lens);
    }
    free(V->classes);
    free(V->arena);
    memset(V, 0, sizeof(*V));
}

static uint8_t *arena_alloc(vm *V, size_t n){
    if(V->arena_used + n > V->arena_cap) return NULL;
    uint8_t *p = V->arena + V->arena_used;
    V->arena_used += n;
    return p;
}

static int push_global(vm *V, uint8_t idx, vm_val *sp){
    switch(idx){
      case VG_INNER_MSG:
        sp->tag = VT_BSTR;
        sp->b = V->ctx.inner_msg;
        sp->n = V->ctx.inner_msg_len;
        break;
      default: return -1;
    }
    return 0;
}

#define VM_STACK_SIZE 128

static int run_code(vm *V, const vm_class *cl, const vm_val *args, int nargs,
                    vm_val *ret_out, int depth)
{
    if(depth > 16) return -101;
    vm_val stack[VM_STACK_SIZE];
    int sp = 0;
    for(int i=0;i<nargs;i++){
        if(sp >= VM_STACK_SIZE) return -102;
        stack[sp++] = args[i];
    }
    const uint8_t *code = cl->code;
    uint32_t code_len = cl->code_len;
    uint32_t pc = 0;

    #define POP(v) do { if(sp<=0){ return -103;} (v) = stack[--sp]; } while(0)
    #define PUSH(v) do { if(sp>=VM_STACK_SIZE) return -104; stack[sp++] = (v); } while(0)
    #define NEED(n) do { if(pc + (n) > code_len) return -105; } while(0)

    while(pc < code_len){
        uint8_t op = code[pc++];
        switch(op){
          case OP_NOP: break;
          case OP_PUSH_I32: {
              NEED(4);
              uint32_t v = code[pc] | ((uint32_t)code[pc+1]<<8) | ((uint32_t)code[pc+2]<<16) | ((uint32_t)code[pc+3]<<24);
              pc += 4;
              vm_val x = { VT_INT, (int32_t)v, NULL, 0 };
              PUSH(x);
              break;
          }
          case OP_PUSH_I64: {
              NEED(8);
              uint64_t v = 0;
              for(int i=0;i<8;i++) v |= (uint64_t)code[pc+i] << (8*i);
              pc += 8;
              vm_val x = { VT_INT, (int64_t)v, NULL, 0 };
              PUSH(x);
              break;
          }
          case OP_PUSH_CONST: {
              NEED(2);
              uint16_t idx = code[pc] | ((uint16_t)code[pc+1]<<8);
              pc += 2;
              if(idx >= cl->const_count) return -106;
              vm_val x = { VT_BSTR, 0, cl->const_ptrs[idx], cl->const_lens[idx] };
              PUSH(x);
              break;
          }
          case OP_PUSH_GLB: {
              NEED(1);
              uint8_t g = code[pc++];
              if(sp >= VM_STACK_SIZE) return -107;
              if(push_global(V, g, &stack[sp])) return -108;
              sp++;
              break;
          }
          case OP_POP: { vm_val t; POP(t); break; }
          case OP_DUP: {
              if(sp<=0) return -109;
              vm_val t = stack[sp-1]; PUSH(t); break;
          }
          case OP_SWAP: {
              if(sp<2) return -110;
              vm_val t = stack[sp-1]; stack[sp-1] = stack[sp-2]; stack[sp-2] = t;
              break;
          }
          case OP_ADD: case OP_SUB: case OP_XOR: case OP_AND: case OP_OR:
          case OP_EQ:  case OP_NEQ: case OP_LT:  case OP_GT: {
              vm_val b, a; POP(b); POP(a);
              if(op == OP_EQ || op == OP_NEQ){
                  int eq;
                  if(a.tag == VT_BSTR && b.tag == VT_BSTR){
                      eq = (a.n == b.n) && (memcmp(a.b, b.b, a.n) == 0);
                  } else if(a.tag == VT_INT && b.tag == VT_INT){
                      eq = (a.i == b.i);
                  } else return -111;
                  vm_val r = { VT_INT, (op==OP_EQ ? eq : !eq), NULL, 0 };
                  PUSH(r);
              } else {
                  if(a.tag != VT_INT || b.tag != VT_INT) return -112;
                  int64_t x = a.i, y = b.i, z = 0;
                  switch(op){
                    case OP_ADD: z = x + y; break;
                    case OP_SUB: z = x - y; break;
                    case OP_XOR: z = x ^ y; break;
                    case OP_AND: z = x & y; break;
                    case OP_OR:  z = x | y; break;
                    case OP_LT:  z = (x < y); break;
                    case OP_GT:  z = (x > y); break;
                  }
                  vm_val r = { VT_INT, z, NULL, 0 };
                  PUSH(r);
              }
              break;
          }
          case OP_JMP: case OP_JZ: case OP_JNZ: {
              NEED(2);
              int16_t off = (int16_t)(code[pc] | ((uint16_t)code[pc+1]<<8));
              pc += 2;
              int take = 0;
              if(op == OP_JMP) take = 1;
              else {
                  vm_val t; POP(t);
                  if(t.tag != VT_INT) return -113;
                  take = (op == OP_JZ) ? (t.i == 0) : (t.i != 0);
              }
              if(take){
                  int64_t npc = (int64_t)pc + off;
                  if(npc < 0 || npc > (int64_t)code_len) return -114;
                  pc = (uint32_t)npc;
              }
              break;
          }
          case OP_CONCAT: {
              vm_val b, a; POP(b); POP(a);
              if(a.tag != VT_BSTR || b.tag != VT_BSTR) return -115;
              uint8_t *dst = arena_alloc(V, a.n + b.n);
              if(!dst) return -116;
              memcpy(dst, a.b, a.n);
              memcpy(dst + a.n, b.b, b.n);
              vm_val r = { VT_BSTR, 0, dst, a.n + b.n };
              PUSH(r);
              break;
          }
          case OP_SUBSTR: {
              vm_val len_v, off_v, src; POP(len_v); POP(off_v); POP(src);
              if(src.tag != VT_BSTR || off_v.tag != VT_INT || len_v.tag != VT_INT) return -117;
              if(off_v.i < 0 || len_v.i < 0 || off_v.i + len_v.i > src.n) return -118;
              vm_val r = { VT_BSTR, 0, src.b + off_v.i, (uint32_t)len_v.i };
              PUSH(r);
              break;
          }
          case OP_LEN: {
              vm_val t; POP(t);
              if(t.tag != VT_BSTR) return -119;
              vm_val r = { VT_INT, (int64_t)t.n, NULL, 0 };
              PUSH(r);
              break;
          }
          case OP_NATIVE: {
              NEED(2);
              uint8_t helper = code[pc++];
              uint8_t na = code[pc++];
              if(na > sp) return -120;
              vm_val *a = &stack[sp - na];
              vm_val r = { VT_INT, 0, NULL, 0 };
              switch(helper){
                case NH_HASH_X: {
                    if(na != 1 || a[0].tag != VT_BSTR) return -126;
                    uint8_t *dst = arena_alloc(V, 32);
                    if(!dst) return -127;
                    hash_x(a[0].b, a[0].n, dst);
                    r.tag = VT_BSTR; r.b = dst; r.n = 32;
                    break;
                }
                default:
                    return -135;
              }
              sp -= na;
              PUSH(r);
              break;
          }
          case OP_INVOKE: {
              NEED(2);
              uint8_t cidx = code[pc++];
              uint8_t na = code[pc++];
              if(cidx >= V->n_classes) return -140;
              if(na > sp) return -141;
              vm_val sub_ret;
              int rc = run_code(V, &V->classes[cidx], &stack[sp-na], na, &sub_ret, depth+1);
              if(rc) return rc;
              sp -= na;
              PUSH(sub_ret);
              break;
          }
          case OP_RET: {
              if(sp > 0){
                  *ret_out = stack[sp-1];
              } else {
                  vm_val z = { VT_INT, 0, NULL, 0 };
                  *ret_out = z;
              }
              return 0;
          }
          case OP_HALT:
              return -199;

          case OP_SHL: case OP_SHR: case OP_MUL: case OP_ROL: case OP_ROR: {
              vm_val b, a; POP(b); POP(a);
              if(a.tag != VT_INT || b.tag != VT_INT) return -160;
              uint32_t x = (uint32_t)a.i;
              uint32_t y = (uint32_t)b.i;
              uint32_t r = 0;
              switch(op){
                case OP_SHL: r = x << (y & 31); break;
                case OP_SHR: r = x >> (y & 31); break;
                case OP_MUL: r = x * y;         break;
                case OP_ROL: { unsigned n = (unsigned)(y & 31);
                               r = (x << n) | (x >> ((32 - n) & 31));
                               if(n == 0) r = x; break; }
                case OP_ROR: { unsigned n = (unsigned)(y & 31);
                               r = (x >> n) | (x << ((32 - n) & 31));
                               if(n == 0) r = x; break; }
              }
              vm_val v = { VT_INT, (int64_t)(uint64_t)r, NULL, 0 };
              PUSH(v);
              break;
          }

          case OP_LOAD_REG: {
              NEED(1);
              uint8_t idx = code[pc++];
              if(idx >= VM_REG_COUNT) return -161;
              vm_val v = { VT_INT, (int64_t)(uint64_t)V->regs[idx], NULL, 0 };
              PUSH(v);
              break;
          }
          case OP_STORE_REG: {
              NEED(1);
              uint8_t idx = code[pc++];
              if(idx >= VM_REG_COUNT) return -162;
              vm_val v; POP(v);
              if(v.tag != VT_INT) return -163;
              V->regs[idx] = (uint32_t)v.i;
              break;
          }

          case OP_BSTR_LOAD_U32: {
              vm_val off_v, src; POP(off_v); POP(src);
              if(src.tag != VT_BSTR || off_v.tag != VT_INT) return -164;
              if(off_v.i < 0 || off_v.i + 4 > src.n) return -165;
              const uint8_t *p = src.b + off_v.i;
              uint32_t r = (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
                           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
              vm_val v = { VT_INT, (int64_t)(uint64_t)r, NULL, 0 };
              PUSH(v);
              break;
          }
          case OP_U32_TO_BSTR: {
              vm_val v; POP(v);
              if(v.tag != VT_INT) return -166;
              uint8_t *dst = arena_alloc(V, 4);
              if(!dst) return -167;
              uint32_t x = (uint32_t)v.i;
              dst[0] = (uint8_t)x;
              dst[1] = (uint8_t)(x >> 8);
              dst[2] = (uint8_t)(x >> 16);
              dst[3] = (uint8_t)(x >> 24);
              vm_val r = { VT_BSTR, 0, dst, 4 };
              PUSH(r);
              break;
          }

          default:
              return -150;
        }
    }
    if(sp > 0) *ret_out = stack[sp-1];
    else { vm_val z = { VT_INT, 0, NULL, 0 }; *ret_out = z; }
    return 0;
    #undef POP
    #undef PUSH
    #undef NEED
}

int vm_run_main(vm *V, vm_val *out_final){
    if(V->n_classes == 0) return -1;
    return run_code(V, &V->classes[0], NULL, 0, out_final, 0);
}
