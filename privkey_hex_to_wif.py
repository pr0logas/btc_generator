#!/usr/bin/env python3
##:: Date: 2021-01-09
##:: Author: Tomas Andriekus
##:: Description:

import bitcoin
import sys

def start_generator():
    # Generate a random private key
    valid_private_key = False

    while not valid_private_key:
        #private_key = bitcoin.random_key()
        private_key  = sys.argv[1] # Insert manually as argument
        decoded_private_key = bitcoin.decode_privkey(private_key, 'hex')
        valid_private_key = 0 < decoded_private_key < bitcoin.N

    print("Private Key (hex) is: ", private_key)
    print("Private Key (decimal) is: ", decoded_private_key)

    # Convert private key to WIF format !!!( Uncompressed )!!!
    wif_encoded_private_key = bitcoin.encode_privkey(decoded_private_key, 'wif')
    print("Private Key (WIF-Uncompressed) is: ", wif_encoded_private_key)
    print("Private Key (WIF-Compressed) is: ????")

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
    print("Compressed Bitcoin Address (b58check) is:", compressed_wallet_addr)


start_generator()
