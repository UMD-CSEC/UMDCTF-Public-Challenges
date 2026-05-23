CC       := gcc
CFLAGS   := -O2 -Wall -Wextra -static -s

CHALL    := dist/roulette
SRC      := roulette2.c

all: $(CHALL)

$(CHALL): $(SRC) challenge_data.h
	mkdir -p $(dir $(CHALL))
	$(CC) $(CFLAGS) -o $(CHALL) $(SRC)

run: $(CHALL)
	./$(CHALL)

clean:
	rm -f $(CHALL)

.PHONY: all run clean
