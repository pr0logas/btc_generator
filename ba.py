#!/usr/bin/env python3
##:: Date: 2021-01-09
##:: Author: Tomas Andriekus
##:: Descriotion: Create a random or manual private key of BTC and match the wallet addr with existing wallets on network..

import bitcoin
import time
import threading
import multiprocessing
from pymongo import MongoClient

HOW_MANY_CPU_CORES = 2
HOW_MANY_WALLETS_TO_CHECK_PER_CYCLE = 1000
FOUNDED_WALLETS_PATH='found_wallets.txt'
DB = 'btc'
COLLECTION = 'wallets_with_balance'

def start_mongo():
    client = MongoClient('mongodb://10.10.10.201:27017/')
    with client:
        db = client.DB
    return db

def write_to_file(path, wallet):
    with open(path, "a") as f:
        f.write(wallet)
        f.close()

def start_generator(workernum):
    start_time = time.time()

    db = start_mongo()

    for i in range(1, HOW_MANY_WALLETS_TO_CHECK_PER_CYCLE):
        # Generate a random private key
        valid_private_key = False
        while not valid_private_key:
            private_key = bitcoin.random_key()
            #private_key  = '000000000000000000000000000000000000000000000000000000000000c936' # Insert manually
            decoded_private_key = bitcoin.decode_privkey(private_key, 'hex')
            valid_private_key = 0 < decoded_private_key < bitcoin.N

        #print("Private Key (hex) is: ", private_key)
        #print("Private Key (decimal) is: ", decoded_private_key)

        # Convert private key to WIF format !!!( Uncompressed )!!!
        #wif_encoded_private_key = bitcoin.encode_privkey(decoded_private_key, 'wif')
        #print("Private Key (WIF) is: ", wif_encoded_private_key)

        # Add suffix "01" to indicate a compressed private key
        #compressed_private_key = f"{private_key}01"
        #print("Private Key Compressed (hex) is: ", compressed_private_key)

        # Generate a WIF format from the compressed private key (WIF-compressed)
        #wif_compressed_private_key = bitcoin.encode_privkey(
        #    bitcoin.decode_privkey(compressed_private_key, 'hex'), 'wif_compressed')
        #print("Private Key (WIF-Compressed) is: ", wif_compressed_private_key)

        # Multiply the EC generator point G with the private key to get a public key point
        public_key = bitcoin.fast_multiply(bitcoin.G, decoded_private_key) # Tuple
        #print("Public Key (x,y) coordinates is:", public_key)

        # Encode as hex, prefix 04
        hex_encoded_public_key = bitcoin.encode_pubkey(public_key, 'hex')
        #print("Public Key (hex) is:", hex_encoded_public_key)

        # Compress public key, adjust prefix depending on whether y is even or odd
        (public_key_x, public_key_y) = public_key
        compressed_prefix = '02' if (public_key_y % 2) == 0 else '03'
        hex_compressed_public_key = compressed_prefix + (bitcoin.encode(public_key_x, 16).zfill(64))
        #print("Compressed Public Key (hex) is:", hex_compressed_public_key)

        # Generate bitcoin address from public key !!!( Uncompressed )!!!
        #print("Uncompressed Bitcoin Address (b58check) is:", bitcoin.pubkey_to_address(public_key))

        # Generate compressed bitcoin address from compressed public key
        compressed_wallet_addr = bitcoin.pubkey_to_address(hex_compressed_public_key)
        #print("Compressed Bitcoin Address (b58check) is:", compressed_wallet_addr)

        query = {"wallet": compressed_wallet_addr}
        res = list(db.COLLECTION.find(query ,{ "_id": 0, "wallet": 1}))
        #print(f"Trying to find: Worker-{workernum} {query} with privKey: {private_key}")

        if res != []:
            print(f"Wallet Found! Worker-{workernum} {res}")
            write_to_file(FOUNDED_WALLETS_PATH, 'Wallet Found! Private key: ' + private_key + ' ' + str(res) + '\n')


    print(f"--- Worker-{workernum} checked {HOW_MANY_WALLETS_TO_CHECK_PER_CYCLE} wallets / "
          f"{(time.time() - start_time)} seconds ---")
    start_generator(workernum)


def start_workers(cpucores):
    for i in range(cpucores):
        p = multiprocessing.Process(target=start_generator, args=(i,))
        p.start()

start_workers(HOW_MANY_CPU_CORES)