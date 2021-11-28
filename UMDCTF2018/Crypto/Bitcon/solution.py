# CORRECT block height & hash is 516976/00000000000000000048d20bddb91b3869f500e4ae94d4ff11afb3c8bd67360b
# CORRECT privkey is 69f500e4ae94d4ff11afb3c8bd67360b
# SHA256(privkey) = 43368da0a227a5b3d9c3432850a7678ac1dcf91045ad6eb71041cdfe6cf4e85e

import hashlib
import base58
import ecdsa
import requests

from ecdsa.keys import SigningKey
from utilitybelt import dev_random_entropy
from binascii import hexlify, unhexlify

def random_secret_exponent(curve_order, block_height):
        r = requests.get('https://blockexplorer.com/api/block-index/' + str(block_height))
        random_int = int(hexlify(r.json()['blockHash'][32:]), 16)
        if random_int >= 1 and random_int < curve_order:
            return random_int

def generate_private_key(height):
    curve = ecdsa.curves.SECP256k1
    se = random_secret_exponent(curve.order, height)
    from_secret_exponent = ecdsa.keys.SigningKey.from_secret_exponent
    return hexlify(from_secret_exponent(se, curve, hashlib.sha256).to_string())

def generate_public_key(private_key_hex):
    hash160 = ripe_hash(private_key_hex)
    public_key_and_version_hex = b"04" + hash160 
    checksum = double_hash(public_key_and_version_hex)[:4]
    return base58.b58encode(public_key_and_version_hex + checksum)

def ripe_hash(key):
    ret = hashlib.new('ripemd160')
    ret.update(hashlib.sha256(key).digest())
    return ret.digest()

def double_hash(key):
    return hashlib.sha256(hashlib.sha256(key).digest()).digest()

def main():
    target = "2Ucke1nNG1iNym7kTCWcQrNgsi84CxhhL2B9"
    privkey = ''
    pubkey = ''
    height = 516976
    while pubkey != target:
        private_key_hex = generate_private_key(height)
        pubkey = generate_public_key(private_key_hex)
        if pubkey == target:
            print("Private Key: " + private_key_hex)
            print("Public Key: " + pubkey)
            print "Height: " + str(height)
        height -= 1

if __name__ == '__main__':
    main()