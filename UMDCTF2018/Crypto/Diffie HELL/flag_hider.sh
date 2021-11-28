#!/bin/bash
if [ $# != 1 ]
then
    echo "Please supply '-e' to encrypt or '-d' to decrypt."
elif [ "$1" == "-e" ]
then
    openssl aes-256-cbc -a -in flag.txt -out encrypted.umdctf
elif [ "$1" == "-d" ]
then
    openssl aes-256-cbc -a -d -in encrypted.umdctf -out flag.txt
else
    echo "Please supply '-e' to encrypt or '-d' to decrypt."
fi
