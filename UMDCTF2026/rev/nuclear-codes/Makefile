all: main

main_unpatched: main.c
	gcc main.c -O3 -s -flto -l:libmpc.a -l:libmpfr.a -l:libgmp.a -o $@

main: main_unpatched patch_strings.py
	python3 patch_strings.py

clean:
	rm -f main
