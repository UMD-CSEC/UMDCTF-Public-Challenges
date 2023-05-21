LDFLAGS=-lSystem -syslibroot `xcrun -sdk macosx --show-sdk-path` -arch arm64
CC = clang 

%.o: %.s
	as $< -o $@

all: shellcode 

cleffa: cleffa.c
	$(CC) $(CFLAGS) -o cleffa cleffa.c

shellcode: shellcode.o
	ld $(LDFLAGS) -o shellcode.macho shellcode.o

clean:
	rm -f *.o *.macho
