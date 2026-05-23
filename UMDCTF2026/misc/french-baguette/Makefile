CC=gcc
CFLAGS=-I.
DEPS=lenet.h
OBJ=lenet.o main.o

LIBS=-lm

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

french-baguette: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f *.o
