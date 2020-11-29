# Module 1 - Create a CryptoCurr

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# requests api need pip install requests

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests #used to get response

from uuid import uuid4 #
from urllib.parse import urlparse #
# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set() # adding node to set

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions' : self.transactions }
        self.transactions = [] # adding tran to block
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transactions(self, sender, receiver ,amount):
        self.transactions.append({'sender': sender,
                                  'receiver' : receiver,
                                  'amount' : amount})
        #get index of last block chian
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        # parse add of node using urlparse
        parsed_url = urlparse(address)
        # add  node to n/w
        self.nodes.add(parsed_url.netloc)
        #ParseResult(scheme='http', netloc='127.0.0.1:5000', path='/', params='', query='', fragment='')

    def replace_chain(self):
        network = self.nodes
        longest_chain = None         # as we dont know nodes having long chain in n/w
        max_length = len(self.chain) # used to find the ogest chain
        for node in network:
            # acces the request with "/get_chain"
            # get dynamic node in request
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if (length > max_length) and (self.is_chain_valid(chain)):
                    max_length = length
                    longest_chain = chain
        
        # if longest chain not none
        if longest_chain:
            self.chain = longest_chain
            return True
        # longest chain is none
        return False




# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port

# uuid4 generate some address with -, we dont need - in our case
# so replace it with blank
node_address = str(uuid4()).replace('-','')


# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)

    # adding the tran
    blockchain.add_transactions(sender = node_address, receiver= 'Loki', amount=1)

    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions'],
                
                }
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new tran to blockchain
@app.route('/add_tran', methods = ['POST'])
def add_transactions():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all( key in json for key in transaction_keys):
        return 'Some elements(keys) of tran are missing', 400
    # index of next block
    index = blockchain.add_transactions(json['sender'], json['receiver'], json['amount'])
    response = {"message" : f'This tran will be add to block {index}'}
    return jsonify(response), 201 # 201 for stating everything is good


# Part 3: dec our blockchain

# connecting new nodes

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Nodes", 400
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message' : 'All nodes are connected',
                'total_nodes' : list(blockchain.nodes)}
    return jsonify(response), 201 # 201 for stating everything is good

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5003)