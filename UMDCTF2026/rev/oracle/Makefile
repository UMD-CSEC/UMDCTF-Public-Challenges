CC      ?= gcc
# -fvisibility=hidden: don't export our symbols into the dynamic symtab.
# -ffunction-sections/-fdata-sections: keep per-symbol sections so any dead
# code is gc'd, making the stripped binary smaller and more opaque.
CFLAGS  ?= -O2 -Wall -Wno-unused-but-set-variable -I src \
           -fvisibility=hidden -ffunction-sections -fdata-sections \
           -fno-asynchronous-unwind-tables
LDFLAGS ?= -Wl,-T,xtext.ld -Wl,--gc-sections -Wl,-s

SRCS = src/main.c src/chk.c src/kitext.c src/xorstr.c src/strings_pool.c \
       src/aes.c src/sha256.c src/tea.c \
       src/blob.c src/blob_key_table.c src/vm.c src/base64.c
OBJS = $(SRCS:.c=.o)

all: dist/oracle

gen: src/strings.inc.h src/strings_pool.c src/blob_key_table.c dist/feed.bin

src/strings.inc.h src/strings_pool.c: build/gen_strings.py
	python3 build/gen_strings.py

vm_src/validate.vmasm build/validate_ticket.bin: build/gen_validate.py build/hashx.py
	python3 build/gen_validate.py

build/vm_out/main.vmc build/vm_out/validate.vmc: \
    build/vm_assemble.py vm_src/main.vmasm vm_src/validate.vmasm
	python3 build/vm_assemble.py vm_src/main.vmasm vm_src/validate.vmasm \
	    --out-dir build/vm_out --classes-idx "main=0,validate=1"

src/blob_key_table.c dist/feed.bin: \
    build/build_blob.py build/vm_out/main.vmc build/vm_out/validate.vmc \
    build/validate_ticket.bin build/hashx.py
	python3 build/build_blob.py

src/%.o: src/%.c | gen
	$(CC) $(CFLAGS) -c $< -o $@

build/oracle.elf: $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $@ $(LDFLAGS)

dist/oracle: build/oracle.elf build/encrypt_kitext.py
	cp build/oracle.elf dist/oracle
	python3 build/encrypt_kitext.py dist/oracle
	strip --strip-all --remove-section=.comment --remove-section=.note.gnu.build-id dist/oracle
	chmod +x dist/oracle

clean:
	rm -f src/*.o build/oracle.elf dist/oracle dist/feed.bin dist/ticket.txt \
	      src/strings.inc.h src/strings_pool.c src/blob_key_table.c \
	      vm_src/validate.vmasm build/validate_ticket.bin \
	      build/shipped_keypair.hex
	rm -rf build/vm_out build/__pycache__

.PHONY: all gen clean
