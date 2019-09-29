#!/usr/bin/env python2.7
"""
cookbook.py

    A simple database application for querying for popular chefs and their
    famous secret recipes.
"""
from __future__ import print_function
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

flag = open("/root/flag.txt").read().strip("\n")
key = os.urandom(16)


def pad(query):
    query = query + 'A'
    while len(query) % 16 != 0:
        query = query + 'A'
    return query


def encrypt(query):
    """
    encrypts a query with flag secret appended using AES-ECB
    """
    query = query + flag

    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
    aes_encrypt = cipher.encryptor()
    ct = aes_encrypt.update(pad(query)) + aes_encrypt.finalize()
    return ct.encode("hex")


def construct_query(age, first, last):
    """
    uses user information and constructs a valid query for encryption
    """
    query = "query:"
    query += "0" * int(age)
    query += first + last
    return encrypt(query)

def fix_send(message):
    print(message)
    return raw_input("")

def main():

    print("=========\nElectronic Cookbook Database\n==========\n")
    print("\t> Search for your favorite chef, and see their favorite (secret) ingredient!")

    try:
        first = fix_send("\nFirst Name: ")
        last = fix_send("Last Name: ")
        age = fix_send("Age: ")

        print("\nEncrypted Information: {}".format(construct_query(age, first, last)))

    except KeyboardInterrupt, EOFError:
        print("\nExiting. Beep Boop.")
        return 1

    except ValueError:
        print("\nInvalid Age! Exiting. Beep Boop.")
        return 1


if __name__ == "__main__":
    main()