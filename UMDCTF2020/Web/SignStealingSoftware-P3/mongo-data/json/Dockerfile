FROM mongo

COPY . .

CMD mongoimport --host mongodb --db houston_astros --mode upsert --collection player_database --type json --file ./Batting.json --jsonArray