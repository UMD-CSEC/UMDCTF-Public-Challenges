import random

def initial_transactions(blockchain):
    names = blockchain.names
    for name in names:
        blockchain.new_transaction("0", name, 13371337)

def generate_transactions(blockchain):
    names = blockchain.names
    num_trans = 10
    for _ in range(num_trans):
        # generate transactions based on people's past
        while 1:
            recipient = names[random.randrange(0,len(names))]
            sender = names[random.randrange(0,len(names))]
            if sender == recipient:
                continue

            # check if transaction is possible
            amount = random.randrange(1,10000)
            start = 13371337
            for block in blockchain.chain:
                for trans in block['transactions']:
                    if trans['sender'] == sender:
                        start -= trans['amount']
                    elif trans['recipient'] == sender:
                        start += trans['amount']

            if start - amount >= 0:
                blockchain.new_transaction(sender, recipient, amount)
                break

def get_balances(blockchain):
    names = blockchain.names 
    balances = {}
    for name in names:
        balances[name] = 0
        for block in blockchain.chain:
            for trans in block['transactions']:
                if trans['sender'] == name:
                    balances[name] -= trans['amount']
                elif trans['recipient'] == name:
                    balances[name] += trans['amount']
    
    return balances

