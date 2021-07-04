# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 20:27:23 2021
@author: shristy
requests==2.18.4:pip install

"""

# Module 2 --> Cryptocurrency
import datetime  # Each block will have exact date when its mined
import hashlib  # We will work with hash functions
import json  # Encode the block
from flask import Flask, jsonify,request  # The messages are returned from the blockchain
import requests
from uuid import uuid4
from urllib.parse import urlparse
#from flask_cors import CORS



# Part 1 Building blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        # transactions and
        self.transactions =[]
        self.wallet = 0
        self.create_block(proof=1, previous_hash='0')
        self.nodes=set()
        self.port=5001


    def create_block(self, proof, previous_hash):
        # Each block in the blockchain will have the following property
        # Here Index is block Number
        # Proof is same as nonce
        # After adding the current transactions, empty it
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions,
                 'wallet': self.wallet
                 }
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # This problem/equation is completely chosen as per the choice.
            # The problem can be modified/hardened
            POW = hashlib.sha256(str(previous_proof ** 2 - new_proof ** 2).encode()).hexdigest()
            # Here the target is only 4 zeros
            if POW[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            current_block = chain[block_index]
            if current_block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            current_proof = current_block['proof']
            POW = hashlib.sha256(str(previous_proof ** 2 - current_proof ** 2).encode()).hexdigest()
            if POW[:4] != '0000':
                return False
            previous_block = current_block
            block_index += 1
        return True

    def verify_transaction_signature(self, sender_address, receiver_address, transaction):
        parsed_url = urlparse(sender_address)
        if (parsed_url.port != self.port):
            return False
        elif self.wallet-transaction<0:
            return False
        transactions = {"amount": transaction}
        response = requests.post(f'http://{urlparse(receiver_address).netloc}/add_wallet', data=transactions, json=transaction)
        if response.status_code != 201:
            return False
        return True




    def add_transaction(self,sender, receiver, amount, ismined):
        if ismined:
            self.transactions.append({'sender': sender, 'receiver': receiver, 'amount': amount})
            self.wallet=self.wallet+amount
        else:
            if self.verify_transaction_signature(sender,receiver,amount):
                self.transactions.append({'sender': sender, 'receiver': receiver, 'amount': amount})
                self.wallet = self.wallet - amount
                previous_block = self.get_previous_block()
                # Index of the new block that will have these transactions
                return previous_block['index'] + 1
            else:
                return -1


    def add_node(self,address):
        parsed_url=urlparse(address)
        if(parsed_url.port!=self.port):
            self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False



# part 2 --> Mining the blockchain
# Creating the web App
# FLask based web application
app = Flask(__name__)
#CORS(app)
# creating an address for the node on Port 5000 with the help of uuid
node_address = str(uuid4()).replace('-','')

app.config['JSONIFY_PREETYPRINT_REGULAR'] = False

# Creating the Block chain
blockchain = Blockchain()



# Decorator
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    new_proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address,receiver='Shristy', amount=10,ismined=True)
    new_created_block = blockchain.create_block(new_proof, previous_hash)
    response = {'message': 'Congratulate miner you just mined a block!',
                'index': new_created_block['index'],
                'timestamp': new_created_block['timestamp'],
                'proof': new_created_block['proof'],
                'previous_Hash': new_created_block['previous_hash'],
                'transactions': new_created_block['transactions'],
                'wallet': new_created_block['wallet']}
    return jsonify(response), 200


# Decorator
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json=request.get_json()
    transaction_keys={'sender','receiver','amount'}
    if not all(key in json for key in transaction_keys):
        response={'message': 'Houston, we have a problem'}
        return jsonify(response),400
    index=blockchain.add_transaction(json['sender'],json['receiver'],json['amount'],False)
    if index!=-1:
        response = {'message': f'The transaction will be added in the block Number {index}'}
        return jsonify(response), 201
    else:
        response = {'message': 'Houston, we have a problem! Either wallet is not sufficient or signature is incorrect!'}
        return jsonify(response),400



#Connecting the new node to all the chains of the decentralized network
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes=json.get('nodes')
    if nodes is None:
        response = {'message': 'Houston, we have a problem, No Nodes Present!'}
        return jsonify(response), 400
    for node in nodes:
        blockchain.add_node(node)
    response={'message': f'All the nodes are added {list(blockchain.nodes)}'}
    return jsonify(response),201

#REPLACING THE CHAIN WITH THE LONGEST CHAIN IF NEEDED
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chainreplaced = blockchain.replace_chain()
    if is_chainreplaced:
        response = {'message': f'The node had different chain therefore its replaced by largest one {blockchain.chain}.'}
    else:
        response = {'message': 'All good the chain was the largest one.'}
    return jsonify(response), 200

# Authentication needs to be established through private data
@app.route('/add_wallet', methods=['POST'])
def add_wallet():
    if request is None:
        response={'message': 'No payload!'}
        return jsonify(response), 400
    amount = request.form.get('amount')
    if (int(amount) >= 0):
        blockchain.wallet = blockchain.wallet + int(amount)
    response={'message':f'{amount} Added, total amount is {blockchain.wallet}.'}
    return jsonify(response), 201


@app.route('/get_wallet_amount', methods=['GET'])
def get_wallet_amount():
    response={'amount': blockchain.wallet}
    return jsonify(response),200


# Part 3 Decentralizing the blockchain
# 0.0.0.0 makes the host available to anyone
app.run(host='0.0.0.0', port=blockchain.port)

