CC ?= cc
STRIP ?= strip

QJS_DIR := third_party_quickjs
TARGET := build/bookmaker
DIST := dist/bookmaker

QJS_SRC := \
	$(QJS_DIR)/quickjs.c \
	$(QJS_DIR)/libregexp.c \
	$(QJS_DIR)/libunicode.c \
	$(QJS_DIR)/cutils.c \
	$(QJS_DIR)/libbf.c

CFLAGS ?= -O2
CFLAGS += -std=c11 -D_GNU_SOURCE -DCONFIG_VERSION=\"2024-01-13\"
CFLAGS += -fwrapv -fno-stack-protector -fPIE
CFLAGS += -Wall -Wextra -Wno-sign-compare -Wno-unused-parameter
CFLAGS += -Wno-array-bounds -Wno-format-truncation
LDFLAGS += -pie -Wl,-z,relro,-z,now
LDLIBS += -lm -ldl -lpthread

.PHONY: all clean run

all: $(DIST)

$(TARGET): challenge.c $(QJS_SRC)
	mkdir -p $(dir $(TARGET))
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^ $(LDLIBS)

$(DIST): $(TARGET)
	mkdir -p $(dir $(DIST))
	cp $(TARGET) $(DIST)
	$(STRIP) $(DIST)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -rf build dist
