# Notes for Trainfuck

## Creation

1) Build the chall code program to generate the BF

```c
int main() {
    int encflag[31] = {127, 8, 110, 6, 126, 3, 81, 35, 88, 116, 73, 46, 117, 38, 66, 117, 26, 26, 73, 45, 26, 117, 117, 49, 93, 113, 27, 43, 89, 56, 10};
    char guess[31]; 
    char modified[31];
    print("Hello please enter the flag!\n");
    int counter = 0;
    char input = readchar();

    while(input != '\n') {
        guess[counter] = input;
        counter += 1;
        input = readchar();
    }

    int is_wrong = 0;

    for (int i = 0; i < 30; i++) {
        if (i % 2 == 0) {
            if (encflag[i] != (guess[i] ^ 42)) {
                is_wrong = 1;
            }
            modified[i] = guess[i] ^ 42;
        } else {
            if (encflag[i] != (guess[i] ^ 69)) {
                is_wrong = 1;
            }
            modified[i] = guess[i] ^ 69;
        } 
    }
    if(is_wrong != 0) {
        print("Wrong!\n");
        for(int i = 0; i < 30; i++) {
            printchar(modified[i]);
        }
        printchar('\n');
    } else {
        print("You got it!!\n");
        for(int i = 0; i < 30; i++) {    
            printchar(guess[i]);
        }
    }

}
```

2) Generate the brainfuck (output in trainfuck.bf)

3) Do text replacement on the BF file to the emojis

  Using replacement script! 

flag = UMDCTF{fr1ck_ch00_ch00_tw41ns}



