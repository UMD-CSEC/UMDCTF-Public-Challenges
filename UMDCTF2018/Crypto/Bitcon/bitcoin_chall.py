import hashlib
import base58
import ecdsa
import requests

from ecdsa.keys import SigningKey
from utilitybelt import dev_random_entropy
from binascii import hexlify, unhexlify

def random_secret_exponent(curve_order):
        r = requests.get('https://blockchain.info/latestblock')
        random_int = int(hexlify(r.json()['hash'][32:]), 16)
        if random_int >= 1 and random_int < curve_order:
            return random_int

def generate_private_key():
    curve = ecdsa.curves.SECP256k1
    se = random_secret_exponent(curve.order)
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

def generate_private_key_wif(private_key_hex):
    private_key_and_version = b"80" + private_key_hex
    checksum = double_hash(private_key_and_version)[:8]
    hashed = private_key_and_version + checksum
    return base58.b58encode(private_key_and_version + checksum)

def main():
    private_key_hex = generate_private_key()
    public_key_hex = generate_public_key(private_key_hex)
    private_key_wif_hex = generate_private_key_wif(private_key_hex)
    print("Private Key: " + private_key_hex)
    print("Public Key: " + public_key_hex)
    print("Private Key (WIF Format): " + private_key_wif_hex)

if __name__ == '__main__':
    main()