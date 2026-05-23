CC=gcc
CFLAGS=-fno-stack-protector -w -static
BIN=chal/ipv4
SRC=ipv4.c

all: $(BIN)

$(BIN): $(SRC)
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)

clean:
	rm -f $(BIN)
