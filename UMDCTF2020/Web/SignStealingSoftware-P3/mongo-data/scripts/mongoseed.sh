#! /bin/bash

if [ -e /scripts/.seeddata ]
then
  printf "\nWARNING"
  printf "\n==========\n"
  printf "Data already seeded!\n"
  printf "If you want to remove and reseed, run 'rm /scripts/.seeddata'\n\n"
else
	printf "\nREMOVING Sample Database\n==========================\n"
	mongo sample --eval "db.dropDatabase()"
	printf "\nImporting Documents in a new Database called Sample\n"
	printf "===================================================\n"
    mongoimport --db houston_astros --collection player_database --type json --file /data/Batting.json --jsonArray
  touch /scripts/.seeddata
  printf "\nDONE!\n"
fi