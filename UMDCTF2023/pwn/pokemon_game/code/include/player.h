#ifndef pokemon_game_player_h
#define pokemon_game_player_h

#include <stdint.h>

#define NAME_LEN 16        /* who has a name larger than 16? */
#define POKEMON_ALLOWED 100 /* shellcode expected length = 43 */

// Abilities
#define SQUIRTLE_ABILITY 0x1
#define GUARANTEE_SUCCESS_ABILITY 0x6

// Player structure
struct player {
  char name[NAME_LEN]; /* vulnerability for cheating */
  int8_t abilities;
  int32_t balls_used;
  int8_t pokemon_caught;
  struct pokemon* pokemon[POKEMON_ALLOWED];
};

void catch_pokemon(struct player* player, struct pokemon* pokemon);
void evolve_pokemon(struct player* player);

int can_evolve_pokemon(struct player* player);
int can_catch_squirtle(struct player* player);
int can_always_catch_pokemon(struct player* player);

#endif
