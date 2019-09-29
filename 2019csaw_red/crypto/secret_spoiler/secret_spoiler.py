#!/usr/bin/env python2.7
import random

# all my secrets! no looking!
from secret import *

def gen(n, secret, num):
    s = Splitter(n, secret).split()
    random.shuffle(s)
    return [{k: v.encode("hex")} for (k,v) in s[0:num]]

def main():
    print("Alright, so here's my secret: {}\n".format(CT))
    print(gen(100, bytes(SECRET_KEY), 3))

if __name__ == "__main__":
    exit(main())