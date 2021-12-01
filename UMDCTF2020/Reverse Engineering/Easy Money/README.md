# Easy Money

Word on the street is this challenge is quite straightforward.

Compilation string: gcc -fpie -fstack-protector -s main.c -o main
$ ldd main
	linux-vdso.so.1 (0x00007ffde75d7000)
	libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f5fd188d000)
	/lib64/ld-linux-x86-64.so.2 (0x00007f5fd1e30000)

* `Author` -- moogboi
* `Flag Hash` -- 01aab61477feee473e9c132f966c5d832f2a886a0185f754fe7fbe3e7649c484
* `Difficulty` -- 1/10