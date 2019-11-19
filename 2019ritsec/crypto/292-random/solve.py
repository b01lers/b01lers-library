from pwn import *

p = remote("ctfchallenges.ritsec.club", 8001)
c = process("./gimme_numbers")

p.sendline(c.recvlines(6)[-1])
print(p.recvall())
