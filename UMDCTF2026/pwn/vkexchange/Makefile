CC ?= cc
GLSLANG_VALIDATOR ?= glslangValidator
CFLAGS ?= -O2
CFLAGS += -std=c11 -Wall -Wextra -Wpedantic -D_FORTIFY_SOURCE=2
LDFLAGS += -Wl,-z,relro,-z,now
LDLIBS += -lvulkan

TARGET := vkexchange
SHADER_HEADER := shader_spv.h
SHADER_SOURCE := settlement.comp

.PHONY: all clean strip

all: $(TARGET)

$(TARGET): vkexchange.c $(SHADER_HEADER)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ vkexchange.c $(LDLIBS)

$(SHADER_HEADER): $(SHADER_SOURCE)
	$(GLSLANG_VALIDATOR) -V -g0 --vn shader_spv -o $@ $<

strip: $(TARGET)
	strip $(TARGET)

clean:
	rm -f $(TARGET) $(SHADER_HEADER)
