#include <stdio.h>
#include <string.h>

int poop_var __attribute__((section("poophaha"))) = 42;
char hahah_str[] __attribute__((section("hahah"))) = "Hahah, this is hilarious!";
float funny_float __attribute__((section("funny"))) = 3.14;

void xor_string(char *string, unsigned char key) {
    int length = strlen(string);
    for (int i = 0; i < length; i++) {
        string[i] ^= key;
    }
}

int main() {
    printf("Poop variable value: %d\n", poop_var);
    printf("Hahah string: %s\n", hahah_str);
    printf("Funny float value: %f\n", funny_float);
    printf("jessie");
    printf("james");
    printf("meowth");

    printf("TEAMROCKET");
    printf("somethingsomethingmalware");
    printf("im so tired");
    printf("sleepy time");

    printf("bruhsinglebytexorin2023?");
    

    return 0;
}