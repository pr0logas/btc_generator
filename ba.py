#!/usr/bin/env python3
##:: Date: 2021-01-09
##:: Author: Tomas Andriekus
##:: Descriotion: Create a random or manual private key of BTC and match the wallet addr with existing wallets on database.

# db = btc
# col = wallets_with_balance

import bitcoin
import time
import threading
import multiprocessing
import os
from pymongo import MongoClient
from pymongo.errors import AutoReconnect

MONGO_HOST = 'mongodb://127.0.0.1:27017/'
HOW_MANY_CPU_CORES = 2
HOW_MANY_WALLETS_TO_CHECK_PER_CYCLE = 1000
FOUNDED_WALLETS_PATH='found_wallets.txt'

def start_mongo():
    client = MongoClient(MONGO_HOST)
    with client:
        db = client.btc
    return db

def write_to_file(path, wallet):
    with open(path, "a") as f:
        f.write(wallet)
        f.close()


def autoreconnect_retry(fn, retries=20):
    def db_op_wrapper(*args, **kwargs):
        tries = 0

        while tries < retries:
            try:
                return fn(*args, **kwargs)

            except AutoReconnect:
                tries += 1

        raise Exception("MongoDB not responding. No luck even after %d retries" % retries)

    return db_op_wrapper

@autoreconnect_retry
def mongo_send_find_query(connection, query):
    return list(connection.wallets_with_balance.find(query, {"_id": 0, "wallet": 1}))

@autoreconnect_retry
def mongo_write_generated_private_keys_with_wallets(connection, write_query):
    return connection.generated_wallets_with_priv_keys.insert_one(write_query)

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

        write_query = {"wallet": compressed_wallet_addr , "privkey" : private_key}
        mongo_write_generated_private_keys_with_wallets(db, write_query)

        query = {"wallet": compressed_wallet_addr}
        query_result = mongo_send_find_query(db, query)

        # >>> Debug <<<
        #print(f"Trying to find: Worker-{workernum} {query} with privKey: {private_key}")
        #print(f"Database match result: {query_result}")

        if query_result != []:
            print(f"Wallet Found! Worker-{workernum} {query_result} {private_key}")
            write_to_file(FOUNDED_WALLETS_PATH, 'Wallet Found! Private key: ' + private_key + ' ' + str(query_result) + '\n')


    print(f"--- Worker-{workernum} checked {HOW_MANY_WALLETS_TO_CHECK_PER_CYCLE} wallets / "
          f"{(time.time() - start_time)} seconds ---")
    start_generator(workernum)

def check_progress():
    time.sleep(10)
    pot_sleep_time = 900
    while True:
        try:
            stat = os.stat(FOUNDED_WALLETS_PATH)
            pot_sleep_time = 5
            print("")
            print(f"************************** HONEY POT! ************************************")
            print(f"*********** Please check the file: {FOUNDED_WALLETS_PATH} ***************")
            print("")

        except FileNotFoundError:
            pot_sleep_time = 900
            print(f"*** Found nothing so far, patience, please ***")
            print(f"*** There are only: 1,461,501,637,330,902,918,203,684,832,716,283,019,655,932,542,976 possible BTC addresses :) ***")


        except Exception as e:
            print(f"<IOwork> Something went wrong. Cannot get {FOUNDED_WALLETS_PATH} modification time!")
            print(e)
            pass
        time.sleep(pot_sleep_time)


def start_workers(cpucores):
    for i in range(cpucores):
        p = multiprocessing.Process(target=start_generator, args=(i,))
        p.start()

start_workers(HOW_MANY_CPU_CORES)
threading.Thread(target=check_progress).start()
