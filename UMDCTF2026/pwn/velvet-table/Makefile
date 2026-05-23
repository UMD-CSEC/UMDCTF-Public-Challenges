CC := gcc
CFLAGS := -O2 -fno-stack-protector -fPIE -Wl,-z,relro,-z,now -pie -Wall -Wextra
STRIP := strip

BIN := dist/velvet-table
SRC := challenge.c

all: $(BIN)

$(BIN): $(SRC)
	mkdir -p $(dir $(BIN))
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
	$(STRIP) $(BIN)

run: $(BIN)
	./$(BIN)

clean:
	rm -f $(BIN)

.PHONY: all run clean
