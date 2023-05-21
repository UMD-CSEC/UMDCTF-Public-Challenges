# pwn/pokemon_game

"gotta catch them all... right?"

## Challenge Notes
The `code/` folder is the only one that matters. You can build the Dockerfile (and tag) with the `./build-docker.sh` script. There is a helper script to run the docker image, `./run-docker.sh` but it is just a shortcut for running with `-p 6969:8080`. 

This can be edited in the file to expose the desired port, but the port for socat inside of the container is 8080. The default solution is for port 6969.

### TO GET THE BINARY FROM THE CONTAINER
You can build locally on linux, however for consistency purposes I would suggest copying the built binary from a container to supply for the challenge. There is a script to accomplish this! While the container is active (`./run-docker.sh`), you can run `./get-binary.sh` to retrieve the binary to the current directory.

## Solution
**Given**: Linux i386 binary, stripped. Titled -- "catch_them_all"

### Vulnerability (1)
Buffer overflow when retrieving the player's name. Not reported by VulnFanatic (BinaryNinja), but is trivial to identify in disassembly.

It should be identifiable that the player's name has a max length (16). However, the program will read up to 20.
```c
struct player* player = (struct player*) malloc(sizeof(struct player));
char* name = (char*) malloc(sizeof(char));
get_string(name, "enter your name: ", NAME_LEN + 4);
memcpy(player->name, name, strlen(name));
```

This allows the player to overwrite specific fields. The goal is to overwrite the [`player->abilities`] field with the number 0x7.

```c
/* This function is called before the evolution stage */
int can_evolve_pokemon(struct player* player) {
  int32_t abilities = player->abilities;
  int32_t rwx = PROT_READ | PROT_WRITE | PROT_EXEC;
  return abilities & rwx;
}
```

```c
/* The `evolve_pokemon` function runs the pokemon identifiers (char) as shellcode. */
void evolve_pokemon(struct player* player) {
  if (can_evolve_pokemon(player)) {
    printf("evolving %s's pokemon!\n", player->name);
    uint8_t* shellcode = get_pokemon_ids(player->pokemon);
    // player abilities should be R/W/X. (0x1 | 0x2 | 0x4) = 0x7
    run(shellcode, player->abilities);
  }
}
```

The size of the shellcode is capped at ***100***. This should be sufficient for cat-ing the file (pwntools) but leaves room for other approaches.

## Flag
`UMDCTF{l00k1n6_f0r_5qu1r7l35_5h3ll}`
