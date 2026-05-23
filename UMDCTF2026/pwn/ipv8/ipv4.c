#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char* header_format = \
" 0                   1                   2                   3   \n"
" 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 \n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
"|Version|  IHL  |Type of Service|          Total Length         |\n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
"|         Identification        |Flags|      Fragment Offset    |\n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
"|  Time to Live |    Protocol   |         Header Checksum       |\n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
"|                    Source ASN Prefix (r.r.r.r)                |\n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
"|                    Source Host Address (n.n.n.n)              |\n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
"|                 Destination ASN Prefix (r.r.r.r)              |\n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
"|                 Destination Host Address (n.n.n.n)            |\n"
"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n";


void win() {
    system("/bin/sh");
}

int check_valid_address(char* address) {
    int i = 0;
    while (*address) {
        if (*address == '.') {
            i++;
        }
        address++;
    }
    return i != 3;
}

void check_rine(char* dest_asn) {
    if (strcmp(dest_asn, "0.0.0.0") == 0) {
        printf("Sorry, we want devices using ipv8 only...\n");
        exit(1);
    }

    if (strcmp(dest_asn, "100.72.7.67") == 0) {
        printf("Welcome in our beloved ipv8 address\n");
        win();
    } else {
        printf("Wrong RINE address!! Perhaps you were looking for 100.72.7.67\n");
    }
}

int main() {
    char src_asn[0x30];
    char src_addr[0x30];
    char dest_asn[0x30];
    char dest_addr[0x30];
    
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    printf("IPv8 is the future! As someone with an ipv4 address, luckily ipv8 is backwards compatible!\n");

    printf("What is your Source ASN Prefix?\n");
    printf("> ");
    scanf("%*s");
    printf("Sorry, you don't get to set that silly! This is for ipv8 only!\n");
    strcpy(src_asn, "0.0.0.0");
    strcpy(dest_asn, "0.0.0.0");

    printf("What is your Source Host Address?\n");
    printf("> ");
    scanf("%s", src_addr);

    if (check_valid_address(src_addr)) {
        printf("Thats not a valid address!\nHere's an ipv8 packet for your reference :3\n");
        printf(header_format);
        exit(1);
    }

    printf("What is your Destination ASN Prefix?\n");
    printf("> ");
    scanf("%*s");
    printf("Sorry, you don't get to set that silly! This is for ipv8 only!\n");

    printf("What is your Destination Host Address?\n");
    printf("> ");
    scanf("%48s", dest_addr);

    if (check_valid_address(dest_addr)) {
        printf("You're soo silly, u got your source address right, now tell me where u want to go :3\n");
        printf(header_format);
        exit(1);
    }

    check_rine(dest_asn);    
}