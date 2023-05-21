#include <stdio.h>

int my_variable __attribute__((section("my_section"))) = 42;
char my_string[] __attribute__((section("my_section"))) = "Hello, world!";
float my_float __attribute__((section("my_section"))) = 3.14;

void use_section_data() {
    printf("My variable value: %d\n", my_variable);
    printf("My string: %s\n", my_string);
    printf("My float value: %f\n", my_float);
}

int main() {
    use_section_data();
    return 0;
}

