#!/usr/bin/env python3
##:: Author: Tomas Andriekus
##:: Date: 2020-01-07
##:: Description: read wallets from file and match mongodb rich wallets (with balance)

from pymongo import MongoClient

RANDOM_GENERATED_WALLETS_PATH='./data/generated_wallets.txt'
FOUND_WALLETS_PATH='./data/found_wallets.txt'

client = MongoClient('mongodb://10.10.10.201:27017/')
with client:
    db = client.btc

def write_to_file(path, wallet):
    with open(path, "a") as f:
        f.write(wallet)
        f.close()

def read_from_file_wallets_with_private_keys(path):
    f=open(path,'r')
    wlts=f.read().splitlines()

    size=len(wlts)
    count=0
    for wlt in wlts:
        count += 1
        query = {"wallet": wlt}
        res = list(db.wallets_with_balance.find(query))
        #print(f"{size}/{count}")
        if res != []:
            answer = "FOUND WALLET!" + str(res)
            print(answer)
            write_to_file(FOUND_WALLETS_PATH, answer)
    print("Matching ended.")


read_from_file_wallets_with_private_keys(RANDOM_GENERATED_WALLETS_PATH)
