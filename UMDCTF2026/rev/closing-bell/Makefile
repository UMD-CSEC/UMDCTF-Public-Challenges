CC ?= gcc
CFLAGS ?= -O2 -fPIE -pie -fno-stack-protector -Wall -Wextra
LDFLAGS ?= -Wl,-z,relro,-z,now

DIST := dist/closing-bell-template.bin

.PHONY: all clean

all: $(DIST)

$(DIST): artifact.c
	mkdir -p dist
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ artifact.c
	strip $@

clean:
	rm -rf dist
