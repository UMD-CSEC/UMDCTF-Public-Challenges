#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sysexits.h>
#include <limits.h>

#define MAX_RESPONSE_LENGTH 1024 + 1

void printflag(){
	char buf[256];
	FILE* f = fopen("./flag.txt", "r");
	fgets(buf, sizeof(buf), f);
	printf("%s\n", buf);
}

int main() {
	char response[MAX_RESPONSE_LENGTH] = {'\0'};
	int magikarp_health = 1;
	int arceus_health = 514;
	int splash_pp = INT_MAX-1;
	setvbuf(stdout, NULL, _IONBF, 0);
	printf("You are challenged by ESIDDALI!\n");
	printf("ESIDDALI sent out MAGIKARP!\n");
	printf("Go! ARCEUS!\n");
	printf("What will you do? (Enter a number)\n");
	printf("0. CHECK BATTLE STATUS\n");
	printf("1. FIGHT\n");
	printf("2. BAG\n");
	printf("3. RUN\n");
	printf("4. POKEMON\n");
	printf("\n");
	while (fgets(response, MAX_RESPONSE_LENGTH, stdin)) {
		if (!strcmp(response, "0\n")){
			printf("MAGIKARP has %d health. Reduce this to zero to win.\n", magikarp_health);
			printf("ARCEUS has %d health. If this is reduced to zero, you lose.\n", arceus_health);
			printf("ARCEUS only knows SPLASH. ARCEUS's SPLASH has %d PP. If SPLASH has zero PP, ARCEUS will STRUGGLE.\n", splash_pp);
			printf("Your bag is full of PP UP. Use them to increase the PP associated with ARCEUS's SPLASH.\n");
			printf("You cannot run from a trainer battle.\n");
			printf("You only have ARCEUS in your party of POKEMON\n");
		}
		else if (!strcmp(response, "1\n")){
			if (splash_pp > 0) {
				printf("ARCEUS used SPLASH!\nBut nothing happened!");
				printf("The foe's MAGIKARP used JUDGEMENT!\n");
				arceus_health -= 128;
				if (arceus_health <= 0) {
					printf("ARCEUS fainted!\n");
					printf("You have ran out of usable POKEMON!\n");
					printf("Unlucky!1!\n");
					break;
				}
				splash_pp -= 1;
				printf("(ARCEUS has %d health now)\n", arceus_health);
				printf("(MAGIKARP's health is unchanged)\n");
				printf("(ARCEUS's SPLASH has %d PP now)\n", splash_pp);

			} else {
				printf("ARCEUS has no moves left!\n");
				printf("ARCEUS used STRUGGLE!\nARCEUS is hit with recoil!\n");
				if (arceus_health <= 514/4) {
					printf("ARCEUS fainted!\n");
					printf("You have ran out of usable POKEMON!\n");
					printf("Unlucky!1!\n");
					break;
				}
				printf("Foe MAGIKARP fainted!\n");
				printf("You defeated ESIDDALI!\n");
				printf("Uh.... I wasted all my money on boba and Taco Bell, please accept this flag instead.\n");
				printflag();
				break;
			}
		}

		else if (!strcmp(response, "2\n")){
			printf("You dumped PP UP on ARCEUS!\n");
			splash_pp+=1;
			printf("(ARCEUS's SPLASH has %d PP now)\n", splash_pp);
			printf("The foe's MAGIKARP used JUDGEMENT!\n");
			arceus_health -= 128;
			if (arceus_health <= 0) {
				printf("ARCEUS fainted!\n");
				printf("You have ran out of usable POKEMON!\n");
				printf("Unlucky!1!\n");
				break;
			}
			printf("(ARCEUS has %d health now)\n", arceus_health);
			printf("(MAGIKARP's health is unchanged)\n");
		}

		else if (!strcmp(response, "3\n")) {
			printf("You can't run from a trainer battle, coward!\n");
			printf("The foe's MAGIKARP used JUDGEMENT!\n");
			arceus_health -= 128;
			if (arceus_health <= 0) {
				printf("ARCEUS fainted!\n");
				printf("You have ran out of usable POKEMON!\n");
				printf("Unlucky!1!\n");
				break;
			}
			printf("(ARCEUS has %d health now)\n", arceus_health);
			printf("(MAGIKARP's health is unchanged)\n");
		}

		else if (!strcmp(response, "4\n")) {
			printf("You only have ARCEUS in your party. There's no one to switch out with!\n");
		}
		else {
			printf("Invalid.\n");
		}
		printf("\nWhat will you do? (Enter a number)\n");
		printf("0. CHECK BATTLE STATUS\n");
		printf("1. FIGHT\n");
		printf("2. BAG\n");
		printf("3. RUN\n");
		printf("4. POKEMON\n");

		printf("\n");
	}

}
