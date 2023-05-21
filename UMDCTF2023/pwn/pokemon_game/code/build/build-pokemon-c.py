#!/usr/bin/env python3
import csv

pokemon_file = open('build/pokemon.csv', 'r') 
reader = csv.reader(pokemon_file)

ctr = 0
def write_def(po_id, p_id, name)->str: 
	return f'   pokemons[{po_id}]=create_pokemon("{name}", {p_id});\n'

content=[]
array_name = "pokemons" 
array_size = 0xff
MAGIC = 0x6

for line in reader:
	if ctr == 0: 
		ctr = ctr + 1 
		continue
	if ctr >= array_size:
		break 
	pokemon_id, name, _, _, _, _, _, _ = line 
	content +=[write_def(pokemon_id, int(pokemon_id) ^ MAGIC, name)] 
	ctr = ctr + 1

pokemon_file = open('templates/pokemon.c.templ', 'r') 
pokemon_h_file = open('pokemon.c', 'w')
for line in pokemon_file: 
	if "INSERT POKEMON" not in line: 
		pokemon_h_file.write(line) 
	else: 
		for c in content: 
			pokemon_h_file.write(c)
