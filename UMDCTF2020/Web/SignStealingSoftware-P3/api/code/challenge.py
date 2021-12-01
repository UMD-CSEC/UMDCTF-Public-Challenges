from flask import Flask, jsonify, request
import pymongo
from bson.json_util import dumps
from flask_cors import CORS, cross_origin
import hashlib
import random
import re
import json
app = Flask(__name__)
app.secret_key = "UMDCTF-2020"
app.config['SESSION_COOKIE_HTTPONLY'] = False
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/v1/resources/playerdata', methods=['POST'])
@cross_origin(origin='*')
def getData():
    result = None
    args = json.loads(request.data)
    client = pymongo.MongoClient('mongodb://mongodb:27017')
    db = client['houston_astros']
    collection = db['player_database']
    team = args['team']
    player = args['player']
    badInput = False

    query = {}
    if team != None and player != None and team != "" and player != "" and badInput != True: 
        if player == 'all':
            query = {'teamID': team}
        else:
            query = {'teamID': team, 'playerID': player}
        result = dumps(collection.find(query))
        
    else: 
        if badInput == True:
            result = "2"
        else:
            result = "-1"
    
    return result
    
app.run(host="0.0.0.0")
