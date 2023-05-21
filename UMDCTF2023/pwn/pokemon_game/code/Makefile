CC := gcc
INCLUDE_DIR := $(shell pwd)/include
CFLAGS := -s -Wall -Wextra -std=c11 -z execstack -fno-stack-protector -I$(INCLUDE_DIR) -m32

SOURCES := $(wildcard *.c)
OBJECT_DIR := objs
OBJECTS := $(patsubst %.c, $(OBJECT_DIR)/%.o, $(SOURCES))
OUT_DIR := out
TARGET_NAME := catch_them_all

all:
	@bash -c 'echo "run: make deps && make target"'

.PHONY: target
target: $(TARGET_NAME)
	strip --strip-all $(OUT_DIR)/$(TARGET_NAME)

$(TARGET_NAME): $(OBJECTS)
	mkdir -p $(OUT_DIR)
	$(CC) $(CFLAGS) -o $(OUT_DIR)/$(TARGET_NAME) $(OBJECTS)

$(OBJECT_DIR)/%.o: %.c
	mkdir -p $(OBJECT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

.PHONY: deps
deps: make-pokemon-c

.PHONY: make-pokemon-c
make-pokemon-c:
	bash -c "build/build-pokemon-c.py"

lint:
	@find . -iname '*.c' -and -iname '*.h' -exec clang-format -i --style=Chromium "{}" \;

.PHONY: clean
clean:
	rm -rf $(OBJECT_DIR)/*.o $(OUT_DIR)/$(TARGET_NAME)
	rm pokemon.c

