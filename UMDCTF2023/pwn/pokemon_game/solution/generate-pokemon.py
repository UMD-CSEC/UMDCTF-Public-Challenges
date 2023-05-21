#!/usr/bin/env python3
import csv

pokemon_file = open('pokemon.csv', 'r')
reader = csv.reader(pokemon_file)

ctr = 0
content = {}

array_name = "pokemons"
array_size = 0xff

for line in reader:
	if ctr == 0: 
		ctr = ctr + 1 
		continue

	if ctr >= array_size:
		break

	pokemon_id, name, _, _, _, _, _, _ = line 
	content[name] = pokemon_id 
	ctr = ctr + 1


pokemon_file = open('pokemon.py', 'w')
pokemon_file.write(f'{array_name} = {content}')
