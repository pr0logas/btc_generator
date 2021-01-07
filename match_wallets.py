#!/usr/bin/env python3
##:: Author: Tomas Andriekus
##:: Date: 2020-01-07
##:: Description: read wallets from file and match mongodb rich wallets (with balance)

from pymongo import MongoClient

RANDOM_GENERATED_WALLETS_PATH='/home/tomand/btc_generator/data/generated_wallets.txt'

client = MongoClient('mongodb://localhost:27017/')
with client:
    db = client.btc

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
            print("FOUND WALLET!", res)
            break


read_from_file_wallets_with_private_keys(RANDOM_GENERATED_WALLETS_PATH)