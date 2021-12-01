
#include <stdio.h>
#include <string.h>

int PhaseOne(unsigned char * input){
  
  int count = 0;

  if(input[1] == '_') { count++; }
  if(input[6] == '_') { count++; }
  if(input[11] == '_') { count++; }
  if(input[16] == '_') { count++; }

  if(count != 4){
    printf("Phase one\tFAILED\n");
    return -1;
  }
  
  printf("Phase one\tSUCCESS\n");
  return 0;
}

int PhaseTwo(unsigned char * input){
  
  int count = 0;

  if(input[3] == '0') { count++; }
  if(input[5] == '3') { count++; }
  if(input[13] == '0') { count++; }

  if(count != 3){
    printf("Phase two\tFAILED\n");
    return -1;
  }
  
  printf("Phase two\tSUCCESS\n");
  return 0;
}

int FinalPhase(unsigned char * input){

  unsigned char boardOne[9] = {0};
  unsigned char boardTwo[9] = {0};
  memcpy(boardOne, input, 9);
  memcpy(boardTwo, input + 9, 9); 
  
  unsigned char a0 = boardOne[0];
  unsigned char a1 = boardOne[1];
  unsigned char a2 = boardOne[2];
  unsigned char a3 = boardOne[3];
  unsigned char a4 = boardOne[4];
  unsigned char a5 = boardOne[5];
  unsigned char a6 = boardOne[6];
  unsigned char a7 = boardOne[7];
  unsigned char a8 = boardOne[8];

  unsigned char b0 = boardTwo[0];
  unsigned char b1 = boardTwo[1];
  unsigned char b2 = boardTwo[2];
  unsigned char b3 = boardTwo[3];
  unsigned char b4 = boardTwo[4];
  unsigned char b5 = boardTwo[5];
  unsigned char b6 = boardTwo[6];
  unsigned char b7 = boardTwo[7];
  unsigned char b8 = boardTwo[8];

  int total = 0;
  int count = 0;
  
  printf("Final phase\n");

  total = a0 + a1 + a2;
  if(total == 0xf4){ count++; }
  else { printf("\t[0] failed\n"); }

  total = a3 + a4 + a5;
  if(total == 0xd9) { count++; }
  else { printf("\t[1] failed\n"); }
  
  total = a6 + a7 + a8;
  if(total == 0x10d) { count++; }
  else { printf("\t[2] failed\n"); }

  total = a0 + a3 + a6;
  if(total == 0xd8) { count++; }
  else { printf("\t[3] failed\n"); }

  total = a1 + a4 + a7;
  if(total == 0x122) { count++; }
  else { printf("\t[4] failed\n"); }

  total = a2 + a5 + a8;
  if(total == 0xe0) { count++; }
  else { printf("\t[5] failed\n"); }

  total = b0 + b1 + b2;
  if(total == 0x11b) { count++; }
  else { printf("\t[6] failed\n"); }

  total = b3 + b4 + b5;
  if(total == 0x102) { count++; }
  else { printf("\t[7] failed\n"); }

  total = b6 + b7 + b8;
  if(total == 0x128) { count++; }
  else { printf("\t[8] failed\n"); }

  total = b0 + b3 + b6;
  if(total == 0x14c) { count++; }
  else { printf("\t[9] failed\n"); }

  total = b1 + b4 + b7;
  if(total == 0xd7) { count++; }
  else { printf("\t[10] failed\n"); }

  total = b2 + b5 + b8;
  if(total == 0x122) { count++; }
  else { printf("\t[11] failed\n"); }

  total = b0 + b6;
  if(total == 0xe8) { count++; }
  else { printf("\t[12] failed\n"); }


  if(count == 13){ printf("\t\tSUCCESS\n"); }
  else { return -1; }

  return 0;
}

int main(){
  
  printf("Enter the flag without UMDCTF-{}: ");

  unsigned char input[20] = {0};
  int ret = 0;

  fgets(input, 21, stdin);
  printf("\n");
  
  ret = PhaseOne(input);
  if(ret){
    return -1;
  }

  ret = PhaseTwo(input);
  if(ret){
    return -1;
  }

  ret = FinalPhase(input);
  if(ret){
    return -1;
  }

  return 0;
}
