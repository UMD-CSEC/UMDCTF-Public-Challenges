#include <stdio.h>
#include <sys/ptrace.h>
#include <string.h>
#include <stdlib.h>

volatile unsigned char flag[23] = {0x18, 0x1, 0xbb, 0xd4, 0x5d, 0x1, 0x52, 0xb1, 0x8e, 0xc2, 0xe8, 0x2, 0x18, 0x8e, 0x8b, 0x20, 0x15, 0xdf, 0x19, 0xb0, 0x58, 0xc, 0x27};

volatile unsigned char xor[23] = {0x2c, 0x6d, 0xd7, 0x8b, 0x28, 0x5e, 0x35, 0x81, 0xfa, 0xb6, 0xdc, 0x5d, 0x7c, 0xbe, 0xd4, 0x11, 0x66, 0x80, 0x69, 0x84, 0x2c, 0x6f, 0x4f};

unsigned char input[5] = {0};

int main(){
  
	int output_flag = 1;
	int version_num = 0xf00d;

	if (ptrace(PTRACE_TRACEME, 0, NULL, NULL) != 0) {
		printf("No cheating in love!\n");
		return 0;
	}


	printf("Enter the pin to open your love letter: \n");
	fgets(input, 4, stdin);
	output_flag = atoi(input);
	
	printf("Output_flag: %i\n", output_flag);	

	if (output_flag > 2147483647 || version_num != 0x1337) {
		printf("Sometimes, love needs more work.\n");
		return 0;
	}


	for(int i = 0; i < 23; i++){
		flag[i] = flag[i] ^ xor[i];
	}

	printf("UMDCTF-{%s}\n", flag);

	return 0;

}
