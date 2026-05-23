/* Lives in section ".xtext" — TEA-CFB encrypted post-link, decrypted by
   main.c at startup before x_entry() is called. All failure paths print
   "ticket rejected" and exit 1, with no signal about which stage rejected. */
#include "xorstr.h"
#include "strings.inc.h"
#include "aes.h"
#include "sha256.h"
#include "tea.h"
#include "blob.h"
#include "vm.h"
#include "base64.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define KITEXT __attribute__((section(".xtext"), noinline))

static uint8_t *KITEXT slurp(const char *path, size_t *out_len){
    FILE *f = fopen(path, "rb");
    if(!f) return NULL;
    fseek(f, 0, SEEK_END); long L = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t *buf = (uint8_t*)malloc((size_t)L);
    if(!buf){ fclose(f); return NULL; }
    if(fread(buf, 1, (size_t)L, f) != (size_t)L){ free(buf); fclose(f); return NULL; }
    fclose(f);
    *out_len = (size_t)L;
    return buf;
}

static int KITEXT strip_pem(const uint8_t *src, size_t src_len,
                            const char *begin, const char *end,
                            char *out, size_t out_cap)
{
    const uint8_t *e = src + src_len;
    size_t blen = strlen(begin), elen = strlen(end);
    const uint8_t *pb = NULL, *pe = NULL;
    for(const uint8_t *q = src; q + blen <= e; q++){
        if(memcmp(q, begin, blen) == 0){ pb = q + blen; break; }
    }
    if(!pb) return -1;
    for(const uint8_t *q = pb; q + elen <= e; q++){
        if(memcmp(q, end, elen) == 0){ pe = q; break; }
    }
    if(!pe) return -1;
    size_t n = (size_t)(pe - pb);
    if(n >= out_cap) return -1;
    memcpy(out, pb, n);
    out[n] = 0;
    return (int)n;
}

static void KITEXT reject(void){
    char b[XS_MAX_LEN + 1];
    fprintf(stderr, "%s\n", S_REJECT(b));
    exit(1);
}

int KITEXT x_entry(int argc, char **argv){
    (void)argc; (void)argv;
    char sbuf[XS_MAX_LEN + 1];
    printf("%s\n", S_BANNER(sbuf));

    char lic_name[XS_MAX_LEN+1]; S_OPEN_LICENSE(lic_name);
    size_t llen;
    uint8_t *lic_text = slurp(lic_name, &llen);
    if(!lic_text) reject();

    char begin[XS_MAX_LEN+1], end[XS_MAX_LEN+1];
    S_PEM_BEGIN(begin); S_PEM_END(end);
    char *b64 = malloc(llen + 1);
    int b64_len = strip_pem(lic_text, llen, begin, end, b64, llen + 1);
    free(lic_text);
    if(b64_len < 0){ free(b64); reject(); }
    uint8_t *tlv = malloc((size_t)b64_len);
    int tlv_len = b64_decode(b64, (size_t)b64_len, tlv, (size_t)b64_len);
    free(b64);
    if(tlv_len < 0){ free(tlv); reject(); }

    /* Ticket TLV: magic "TKT\x01" | content_len:u32 | content (32B exact). */
    if(tlv_len < 4 + 4 + 32 ||
       tlv[0] != 'T' || tlv[1] != 'K' || tlv[2] != 'T' || tlv[3] != 0x01){
        free(tlv); reject();
    }
    uint32_t content_len = (uint32_t)tlv[4] | ((uint32_t)tlv[5]<<8) |
                           ((uint32_t)tlv[6]<<16) | ((uint32_t)tlv[7]<<24);
    if(content_len != 32 || (size_t)tlv_len != 8 + content_len){
        free(tlv); reject();
    }
    const uint8_t *ticket_content = tlv + 8;

    char blob_name[XS_MAX_LEN+1]; S_LOAD_BLOB(blob_name);
    size_t blob_len;
    uint8_t *blob_bytes = slurp(blob_name, &blob_len);
    if(!blob_bytes){ free(tlv); reject(); }
    uint8_t *arc_bytes; size_t arc_len;
    if(blob_decrypt(blob_bytes, blob_len, &arc_bytes, &arc_len)){
        free(blob_bytes); free(tlv); reject();
    }
    free(blob_bytes);

    char nm_main[XS_MAX_LEN+1], nm_val[XS_MAX_LEN+1], nm_flag[XS_MAX_LEN+1];
    S_ENTRY_MAIN(nm_main); S_ENTRY_VALIDATE(nm_val); S_ENTRY_FLAGSEAL(nm_flag);

    const uint8_t *main_p, *val_p, *flag_ct_p;
    uint32_t main_n, val_n, flag_ct_n;
    if(arc_find_entry(arc_bytes, arc_len, nm_main, &main_p, &main_n) ||
       arc_find_entry(arc_bytes, arc_len, nm_val,  &val_p,  &val_n)  ||
       arc_find_entry(arc_bytes, arc_len, nm_flag, &flag_ct_p, &flag_ct_n))
    {
        free(arc_bytes); free(tlv); reject();
    }

    vm V; vm_init(&V, 64 * 1024);
    uint8_t *main_copy = malloc(main_n); memcpy(main_copy, main_p, main_n);
    uint8_t *val_copy  = malloc(val_n);  memcpy(val_copy,  val_p,  val_n);

    if(vm_load_class(&V, "0", main_copy, main_n) ||
       vm_load_class(&V, "1", val_copy,  val_n))
    {
        vm_destroy(&V);
        free(main_copy); free(val_copy);
        free(arc_bytes); free(tlv); reject();
    }

    V.ctx.inner_msg = ticket_content;
    V.ctx.inner_msg_len = content_len;

    vm_val result;
    int rc = vm_run_main(&V, &result);
    if(rc != 0 || result.tag != VT_BSTR || result.n != 32){
        vm_destroy(&V);
        free(main_copy); free(val_copy);
        free(arc_bytes); free(tlv); reject();
    }
    /* Copy out of VM arena before it's freed. */
    uint8_t fkm[32];
    memcpy(fkm, result.b, 32);
    vm_destroy(&V);
    free(main_copy); free(val_copy);

    uint8_t *flag_pt = malloc(flag_ct_n);
    memcpy(flag_pt, flag_ct_p, flag_ct_n);
    int n = aes128_cbc_decrypt(fkm, fkm + 16, flag_pt, flag_ct_n, 1);
    if(n < 0){
        free(flag_pt); free(arc_bytes); free(tlv);
        reject();
    }

    printf("%s", S_FLAG_HDR(sbuf));
    fwrite(flag_pt, 1, (size_t)n, stdout);
    fputc('\n', stdout);

    free(flag_pt); free(arc_bytes); free(tlv);
    return 0;
}
