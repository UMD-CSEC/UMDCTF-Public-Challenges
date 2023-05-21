#!/usr/bin/env python3

from pokemon import pokemons

# from binary
ID_MAGIC = 0x6

# shift according to magic
def shift(p_id) -> int: 
	return p_id ^ ID_MAGIC

def pokemon(name) -> int: 
	return shift(int(pokemons[name]))


