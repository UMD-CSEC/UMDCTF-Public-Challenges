import hashlib
import requests
from time import time
import json
import pickle

def proof_of_work(last_proof):
    # PoW Algorithm: Find a number p' such that hash(pp') contains leading 5 zeroes,
    # where p is the previous proof and p' is the new proof
    proof = 0
    while valid_proof(last_proof, proof) is False:
        proof += 1
    return proof

def valid_proof(last_proof, proof):
    # Checks if the proof is valid or not (first 5 bytes have to be "00000")
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:5] == "00000"

def hash_prev(block):
    block_string = json.dumps(block, sort_keys=True).encode()
    h_hash = hashlib.sha256(block_string).hexdigest()
    return h_hash

dest = 'http://0.cloud.chals.io:24797'
name = "gary2"
#dest = 'http://127.0.0.1:50002'
#myip = "172.58.187.96"
#myip = "172.29.90.96"
#myport = 24797

# make a post request for initializing node
data = {"node_name": name}
r = requests.post(f'{dest}/nodes/register', json=data)
print(r.text)
print(r.json()['message'] + '\n')

# get pending transactions and blockchain
r = requests.get(f'{dest}/chain')
blockchain = r.json()['chain']
print(blockchain)

r = requests.get(f'{dest}/pending_transactions')
pending_transactions = r.json()
#print(pending_transactions)

# complete proof of work for new block and form a new block with transactions and other data
last_proof = blockchain[-1]['proof']
proof = proof_of_work(last_proof)
block = {
    'index': blockchain[-1]['index'] + 1,
    'timestamp': time(),
    'transactions': pending_transactions,
    'proof': proof,
    'previous_hash': hash_prev(blockchain[-1])
}
blockchain.append(block)

new_dict = {'chain': blockchain, 'length': len(blockchain), 'name': name}
r = requests.post(f'{dest}/nodes/update', json=new_dict)
print(r)
print(r.text)

