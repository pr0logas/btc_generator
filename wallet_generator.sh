#!/usr/bin/env bash
##:: Author: Tomas Andriekus
##:: Date: 2020-01-06
##:: Description: Create offline wallet by generating a random addr.

WORK_PATH='./data/'
rm -fr ${WORK_PATH}generated_*
mkdir -p $WORK_PATH

OUTPUT_WALLETS_WITH_PRIV="${WORK_PATH}generated_private_keys.txt"
OUTPUT_WALLETS="${WORK_PATH}generated_wallets.txt"
MAX=10000

function generate {
for ((i=1; i <= MAX ; i++)) ; do
	# creates random wallet
	hex=$(bitcointool -command genkey | head -1 | awk '{print $3}') 

	# converts private key to wallet address 
	out=$(bitcointool -command pubfrompriv -p $hex)

	# grabs only wallets before segwit and after
	echo WIF_${hex} | awk '{print $1}' >> $OUTPUT_WALLETS_WITH_PRIV
	echo ${out} | awk '{print $5}' >> $OUTPUT_WALLETS
	echo ${out} | awk '{print $8}' >> $OUTPUT_WALLETS
	echo ${1}-${i}
done
}

generate "1-Thread" &
generate "2-Thread" &

