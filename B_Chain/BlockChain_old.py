#module 1
import datetime
import hashlib
import json
from flask import Flask, jsonify

# part one -- bulding a blockchain
# bulding with class
class Blockchain:
    # genysys block -- first block of BChain
    # solid BChain--not to be hack

    def __init__(self):
        self.chain = [] #list of block
        self.create_block(proof = 1, prev_hash = '0')
    
    def create_block(self, proof, prev_hash):
        #index block , timestamp, proof, prev_hash
        block = {'index' : len(self.chain)+1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'prev_hash' : prev_hash
                }
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while (check_proof is False):
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if (hash_operation[:4] == '0000'):
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
         # convet dict into a string
         encoded_block = json.dumps(block, sort_keys=True).encode()
         return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_vald(self, chain):
        prev_block = chain[0]
        block_index = 1

        while (block_index < len(chain)):
            block = chain[block_index]
            # hash check
            if (block['prev_hash'] != self.hash(prev_block)):
                return False
            # proof check
            prev_proof = prev_block['proof'] # proof of prev
            proof = block['proof'] # proof of current block
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if (hash_operation[:4] != '0000'):
                return False

            # update block index & prevblock
            prev_block = block 
            block_index +=1   
        return True

# part 2 Mining block
#creating a flask Web App

app = Flask(__name__) # flask app creat

# def hello_world():
#     return 'Hello, World!'

# creating a BlockChain

blockchain_instance = Blockchain() 

# mining a new block
# Running on http://127.0.0.1:5000/
@app.route('/mine_block', methods=['GET'])
def mine_block():
    # proof of work problem
    prev_block = blockchain_instance.get_prev_block()
    prev_proof = prev_block['proof']

    #proof of work making
    proof = blockchain_instance.proof_of_work(prev_proof)

    # add block to Bloack chain
    prev_hash = blockchain_instance.hash(prev_proof)

    #create block
    block = blockchain_instance.create_block(proof,prev_hash)

    # showing respone in postman
    response = {'message' : 'Mine block is done, block is added!',
                'index' :block ['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'prev_hash' : block['prev_hash']
                }
    return jsonify(response), 200

# get block chain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain' : blockchain_instance.chain,
                'length' : len(blockchain_instance.chain) }
    return jsonify(response), 200


# block valid


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain_instance.is_chain_vald(blockchain_instance.chain)
    if is_valid:
        response = {'message' : 'Block is all good'}
    else:
        response = {'message' : 'Block having problem'}
    return jsonify(response), 200

# running a flask web app

app.run(host = '0.0.0.0', port = 5000) 

#use postman to access