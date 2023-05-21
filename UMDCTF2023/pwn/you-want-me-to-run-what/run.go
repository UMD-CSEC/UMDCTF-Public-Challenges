//go:build linux || freebsd || darwin
// +build linux freebsd darwin

package main

/*
#include <signal.h>
#include <setjmp.h>
#include <stdio.h>
#include <sys/mman.h>
#include <string.h>
#include <unistd.h>

sigjmp_buf jmpbuf;

void signal_handler(int sig) {
    siglongjmp(jmpbuf, sig);
}

int call(const char* shellcode, size_t length) {
    struct sigaction act;
    memset(&act, 0, sizeof(act));
    act.sa_handler = signal_handler;
    sigaction(SIGSEGV, &act, NULL);
    sigaction(SIGILL, &act, NULL);
    sigaction(SIGFPE, &act, NULL);
    sigaction(SIGBUS, &act, NULL);
    sigaction(SIGABRT, &act, NULL);

    if (sigsetjmp(jmpbuf, 1) == 0) {
        // cast the shellcode to a function pointer
        //int (*fn)(void) = (int (*)(void))sc;
		unsigned char *ptr;
		ptr = (unsigned char *) mmap(0, length, \
			PROT_READ|PROT_WRITE|PROT_EXEC, MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
		if(ptr == MAP_FAILED) {
			perror("mmap");
			return;
		}
		memcpy(ptr, shellcode, length);
		return ( *(int(*) ()) ptr)();

        // call the shellcode and return its result
        //return fn();
    } else {
        // return -1 to indicate a crash
        return -1;
    }
}
*/
import "C"
import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"net"
	"unicode/utf8"
	"unsafe"
)

var flag = "UMDCTF{cpus_love_collisions}"

func Run(sc []byte) bool {
	ret := C.call((*C.char)(unsafe.Pointer(&sc[0])), (C.size_t)(len(sc)))
	return ret != -1
}

func clen(n []byte) ([]byte, int) {
	for i := 0; i < len(n); i++ {
		if n[i] == 0 || n[i] == 10 {
			return n[:i], i
		}
	}
	return n, len(n)
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	// print the client's address
	fmt.Println("New client connected: ", conn.RemoteAddr())
	// send a response back to the client
	response := []byte("MMMM you want me to run WHAT?\n")
	_, err := conn.Write(response)
	if err != nil {
		fmt.Println("Error writing:", err)
		return
	}
	// read data from the client
	buffer := make([]byte, 1024)
	_, err = conn.Read(buffer)
	if err != nil {
		fmt.Println("Error reading:", err)
		return
	}
	buff, length := clen(buffer)
	fmt.Println("Got message: ", buff)
	if length < 10 {
		conn.Write([]byte("That is not nearly a long enough to be worth my while!\n"))
		return
	}
	if length > 16 {
		conn.Write([]byte("In this economy?! That is wayyyyy too long!\n"))
		return
	}

	if !utf8.ValidString(string(buffer)) {
		conn.Write([]byte("That is not a family friendly thing to run!\n"))
		return
	}

	conn.Write([]byte("Time to show your message to the CPU and see what it thinks!\n"))
	success := Run(buffer)
	if success {
		fmt.Println("CPU is happy")
		conn.Write([]byte("Well... I suppose the CPU says its happy, let's see if we can accept it...\n"))
	} else {
		fmt.Println("CPU is sad")
		conn.Write([]byte("Your message made the CPU sad :(\n"))
		return
	}

	if !checkStr(buff) {
		conn.Write([]byte("Woah woah woah - we only accept things here whose MD5 hashes start and end with three 0s!"))
		return
	}

	conn.Write([]byte(fmt.Sprintf("I guess I did run that!\n%s", flag)))
	return
}

func checkStr(buffer []byte) bool {
	fmt.Println(buffer)
	hashBytes := md5.Sum(buffer)
	hashString := hex.EncodeToString(hashBytes[:])
	return checkMD5(hashString)
}

func checkMD5(hash string) bool {
	fmt.Println(hash)
	firstDigit := hash[0]
	lastDigit := hash[len(hash)-1]
	if firstDigit == '0' && lastDigit == '0' && hash[1] == '0' && hash[2] == '0' && hash[len(hash)-2] == '0' && hash[len(hash)-3] == '0' {
		return true
	}
	return false
}

func main() {
	// listen on all available IP addresses on port 8080
	ln, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Println("Error:", err)
		return
	}
	defer ln.Close()

	fmt.Println("Listening on port 8080...")

	for {
		// wait for a client to connect
		conn, err := ln.Accept()
		if err != nil {
			fmt.Println("Error:", err)
			continue
		}

		// handle the client connection in a new goroutine
		go handleConnection(conn)
	}
}
