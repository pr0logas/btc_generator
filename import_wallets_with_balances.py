#!/usr/bin/python3
##:: Author: Tomas Andriekus
##:: Date: 2020-01-07
##:: Description: import rich wallets to mongodb database. Source:
# https://gz.blockchair.com/bitcoin/addresses/

from pymongo import MongoClient

WALLETS_WITH_HONEY_PATH='blockchair_bitcoin_addresses_latest.tsv'

client = MongoClient('mongodb://localhost:27017/')
with client:
    db = client.btc

def read_from_file(path):
    with open(path, 'r') as f:
        read_data = f.readlines()
        for i in read_data:
            res = i.split()
            wlt = { "wallet" : res[0] }
            db.wallets_with_balance.insert_one(wlt)

read_from_file(WALLETS_WITH_HONEY_PATH)
