/* Place our extra sections page-aligned with start/stop markers.
   `chk` holds the integrity-checked anti-debug.
   `.xtext` holds the runtime-decrypted code. */
SECTIONS {
    chk : ALIGN(64) {
        __chk_start = .;
        *(chk)
        __chk_end = .;
    }
    .xtext : ALIGN(4096) {
        __xtext_start = .;
        *(.xtext)
        . = ALIGN(4096);
        __xtext_end = .;
    }
}
INSERT AFTER .text;
