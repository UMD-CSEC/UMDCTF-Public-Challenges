#include <player.h>
#include <pokemon.h>

#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

#define TRUE 1

char pokemon_catch_opts[3] = {'y', 'n', 'f'};

// https://cboard.cprogramming.com/c-programming/70320-how-remove-newline-string.html
void chomp(char* s) {
  while (*s && *s != '\n' && *s != '\r') {
    s++;
  }
  *s = 0;
}

char get_opt(char restraints[3], char* prompt) {
  char opt = '\0';
  printf("%s\n", prompt);
  while (opt != restraints[0] && opt != restraints[1] && opt != restraints[2]) {
    opt = fgetc(stdin);
  }
  return opt;
}

void get_string(char* buf, char* prompt, int length) {
  printf("%s", prompt);
  fgets(buf, length, stdin);
  chomp(buf);
}

int main() {
  // srand(time(NULL));
  struct player* player = (struct player*) malloc(sizeof(struct player));
  char* name = (char*) malloc(sizeof(char));
  get_string(name, "enter your name: ", NAME_LEN + 4);
  memcpy(player->name, name, strlen(name));
  printf(
      "hello adventurer %s\n{\n abilities = %d\n balls_used = %d\n "
      "pokemon_allowed = %d\n}\n",
      player->name, player->abilities, player->balls_used, POKEMON_ALLOWED);
  init_pokemon();
  while (player->balls_used < POKEMON_ALLOWED) {
    // Search for pokemon
    printf("searching for pokemon...");
    struct pokemon* pokemon = find_pokemon();
    // Bug???
    if (pokemon == NULL || pokemon == 0x11) {
       continue;
    } 
    // Found pokemon. Should we catch it?
    printf(" found %s!\n\n", pokemon->name);
    char opt = get_opt(pokemon_catch_opts, "would you like to catch? y/n:");
    if (opt == 'y') {
      catch_pokemon(player, pokemon);
    } else if (opt == 'f') {
      goto end;
    }
    printf("\n\n");
  }
end:
  if (player == NULL) {
    goto clean_poke;
  }
clean_player:
  evolve_pokemon(player);
  free(player);
clean_poke:
  deinit_pokemon();
  return 0;
}
