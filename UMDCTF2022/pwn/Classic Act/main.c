// gcc main.c -o classicact -fno-pic -no-pie -std=c99 - Tested on Ubuntu 20.04

#include <stdio.h>
#include <string.h>
int vuln()
{
    char buff1[16];
    char buff2[64];
    int retval = 0;  
    printf("Please enter your name!\n"); 
    gets(buff1);
    printf("Hello:\n");
    printf(buff1); 
    printf("\n"); 
    printf("What would you like to do today?\n"); 
    gets(buff2); 
    int cmp = strncmp(buff2, "Play in UMDCTF!", 15);
    if (cmp == 0)
    {
        printf("You have come to the right place!\n");
        retval = 0;
    }
    else
    {
        printf("Good luck doing that!\n"); 
        retval = 1;
    }
    return retval;
}

void setup()
{
    setbuf(stdin, NULL); 
    setbuf(stderr, NULL);
    setbuf(stdout, NULL);
}

int main()
{
    setup();
    int retval = vuln();
    return retval;
}
