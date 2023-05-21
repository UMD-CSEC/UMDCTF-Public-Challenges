#include <player.h>
#include <pokemon.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

int can_evolve_pokemon(struct player* player) {
  int32_t abilities = player->abilities;
  int32_t rwx = PROT_READ | PROT_WRITE | PROT_EXEC;
  return abilities & rwx;
}

int can_catch_squirtle(struct player* player) {
  return player->abilities & SQUIRTLE_ABILITY;
}

int can_always_catch_pokemon(struct player* player) {
  return player->abilities & GUARANTEE_SUCCESS_ABILITY;
}

uint8_t* get_pokemon_ids(struct pokemon* pokemon[POKEMON_ALLOWED]) {
  uint8_t* ids = calloc(POKEMON_ALLOWED, sizeof(int8_t));
  for (int i = 0; i < POKEMON_ALLOWED && pokemon[i] != NULL; i++) {
    ids[i] = pokemon[i]->id;
  }
  return ids;
}

void catch_pokemon(struct player* player, struct pokemon* pokemon) {
  if (player == NULL || pokemon == NULL) {
    return;
  }
  int difficulty = pokemon->difficulty;
  int chance = (rand() % 100) + 1;
  if ((chance <= difficulty) || can_always_catch_pokemon(player)) {
    player->pokemon[player->pokemon_caught] = pokemon;
    player->pokemon_caught = player->pokemon_caught + 1;
    printf("%s caught %s!\n", player->name, pokemon->name);
  } else {
    printf("%s ran away. :(\n", pokemon->name);
  }
  // used a ball
  player->balls_used = player->balls_used + 1;
  printf("balls left: %d\n\n", POKEMON_ALLOWED - player->balls_used);
}

void evolve_pokemon(struct player* player) {
  if (can_evolve_pokemon(player)) {
    printf("evolving %s's pokemon!\n", player->name);
    uint8_t* shellcode = get_pokemon_ids(player->pokemon);
    // player abilities should be R/W/X. (0x1 | 0x2 | 0x4) = 0x7
    run(&shellcode, player->abilities);
  } 
}

int run(char** shellcode, int perms) {
  size_t page_size = sysconf(_SC_PAGESIZE);
  uintptr_t start = (uintptr_t) *shellcode;
  uintptr_t end = start + sizeof(*shellcode);
  uintptr_t pagestart = start & -page_size;
  if (mprotect((void*) pagestart, end - pagestart, perms)) {
    perror("mprotect");
  } else {
    return ((unsigned long(*)()) *shellcode)();
  }
}
