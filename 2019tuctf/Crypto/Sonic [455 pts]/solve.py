#!/usr/bin/python3
from pwn import *
import enchant

d = enchant.Dict("en_US")

r = remote('chal.tuctf.com', 30100)
s = r.recv()
#print(s)
#s = 'pmttw'

def rot_alpha(n):
    from string import ascii_lowercase as lc, ascii_uppercase as uc
    lookup = str.maketrans(lc + uc, lc[n:] + lc[:n] + uc[n:] + uc[:n])
    return lambda s: s.translate(lookup)
for i in range(1,25):
    if(d.check(rot_alpha(i)(s))):
        #r.sendline(rot_alpha(i)(s))
        print(rot_alpha(i)(s))

