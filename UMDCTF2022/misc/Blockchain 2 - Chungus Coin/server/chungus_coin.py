import hashlib
import json
from time import time
from textwrap import dedent
from uuid import uuid4
from flask import Flask, request, jsonify
from urllib.parse import urlparse
from generate_transactions import initial_transactions, generate_transactions, get_balances
import requests

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.nodes = []
        self.recent_nodes = {}
        self.names = ["birch", "gary", "cheshirecatalytic", "dewy", "artemisi19", "triakontakai", "matlac", "wittsend2",
                      "jsfleming", "mykale", "amanthanvi", "ptrip9199", "ishaan514", "shricubed", "mmohades", "angcheng27",
                      "suryaviyyapu", "nickfroehl", "yieb", "cybercyber2", "sm00thcriminal96", "ai-ya-ya"]  
        self.new_block(previous_hash=1, proof=100) # genesis block

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    @property
    def last_block(self):
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        self.pending_transactions.append(transaction)
        return self.last_block['index'] + 1

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        h_hash = hashlib.sha256(block_string).hexdigest()
        return h_hash

    def proof_of_work(self, last_proof):
        # PoW Algorithm: Find a number p' such that hash(pp') contains leading 5 zeroes, 
        # where p is the previous proof and p' is the new proof 
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof 

    @staticmethod
    def valid_proof(last_proof, proof):
        # Checks if the proof is valid or not (first 5 bytes have to be "00000")
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:5] == "00000"
	
    def register_node(self, name, ip):
        self.nodes.append({'name': name, 'ip': ip})
        #print(self.nodes)

    def valid_chain(self, chain):
        # Determine if a given blockchain is valid
        last_block = chain[0]
        if last_block['proof'] != 100 or last_block['previous_hash'] != 1:
            print("Invalid genesis block")
            return False
        
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            
            print(f'{last_block}\n')
            print(f'{block}')
            print("\n-----------\n")
            
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                print("invalid hash")
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                print("invalid proof")
                return False

            # Check that index of block is correct
            if current_index + 1 != block['index']:
                print("invalid index")
                return False

            # Check that timestamps aren't wack
            if last_block['timestamp'] > block['timestamp']:
                print("invalid timestamp")
                return False

            last_block = block
            current_index += 1

        # Check for valid transactions
        if self.pending_transactions != last_block['transactions']:
            print("invalid transactions")
            return False

        return True


app = Flask(__name__)

# Initiate blockchain with genesis block, starting transactions in a new block, and new transactions
blockchain = Blockchain()
initial_transactions(blockchain) # gives everyone 13371337 Chungus Coins
blockchain.new_block(blockchain.proof_of_work(blockchain.last_block['proof']))
generate_transactions(blockchain)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    balances = get_balances(blockchain)
    # TODO - find nice HTML & CSS theme for this
    s = 'cc = ChungusCoin\n<br>\n<br>\n'
    for k,v in balances.items():
        s += f'{k}: {v} cc\n<br>\n'
    return s, 200
    
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    node_name = values['node_name']
    node_ip = request.remote_addr

    #req_ip = urlparse(node_addr).netloc.split(':')[0] 
    #act_ip = request.remote_addr

    if node_name is None:
        return "Error: Please supply a valid node name", 400

    if node_name in blockchain.names:
        return "Error: Node name is already taken", 400

    # check if name or address already in nodes
    for node in blockchain.nodes:
        if node_name == node['name']:
            return "Error: Node name is already taken"
        elif node_ip == node['ip']:
            return "Error: This address is already a registered node"
        
    blockchain.register_node(node_name, node_ip)
    response = {
        'message': 'New node have been added',
	'node_name': node_name,
        'node_ip': node_ip
    }

    return jsonify(response), 201

@app.route('/nodes/update', methods=['POST'])
def consensus():
    values = request.get_json()
    length = values['length']
    challenger_chain = values['chain']
    name = values['name']

    if (length - len(blockchain.chain) == 1) and (blockchain.valid_chain(challenger_chain)) and (len(challenger_chain) == length) and not (name in blockchain.names) and \
                                             (blockchain.pending_transactions == challenger_chain[-1]['transactions']):
        blockchain.chain = challenger_chain
        with open('flag.txt', 'r') as f:
            data = str(f.read().strip())

        #addr = winning_node['addr']
        response = {
            'message': 'We have updated our chain with your new block :)',
            'new_chain': blockchain.chain,
            'reward': f"1337 ChungusCoin will be added to pending_transactions and the real prize: {data}"
        }
        blockchain.names.append(name)
        blockchain.pending_transactions = []
        blockchain.new_transaction("0", name, 1337)
        generate_transactions(blockchain)
    else:
        response = {
            'message': 'The chain shall remain the same',
            'chain': blockchain.chain
        }
	
    return jsonify(response), 200

@app.route('/pending_transactions', methods=['GET'])
def pending_transactions():
    return jsonify(blockchain.pending_transactions), 200

@app.route('/')
def home():
    with open('chunga.txt', 'r') as f:
        chunga = f.read().replace('\n', '<br>')
    return "<html><body><h1>Welcome to Chungus Coin!</h1>\n\n<p>" + chunga + '</p></body></html>\n', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50002)

# CREDS: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

