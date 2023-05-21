#ifndef pokemon_game_pokemon_h
#define pokemon_game_pokemon_h

#include <stdlib.h>
#include <stdint.h>

#define POKEMON_REGISTERED 0xff
#define SQUIRTLE_ID 7

struct pokemon {
  char* name;
  uint8_t id;
  int32_t difficulty;
};

// should only be 0xff
static struct pokemon** pokemons;

struct pokemon* create_pokemon(char* name, unsigned char index);

int is_pokemon_squirtle(struct pokemon* pokemon);

void init_pokemon(void);
void deinit_pokemon(void);

struct pokemon* find_pokemon(void);

#endif
