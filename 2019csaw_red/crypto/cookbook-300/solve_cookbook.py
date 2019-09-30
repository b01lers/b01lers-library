from pwn import *
import textwrap

age = 10 + 10

known = "flag{" # first name

padding = "query:" + "0"*10 + "0"*10 # last name

known_block = 1
flag_block = 3

context.log_level = "error"

for i in range(25):
    for c in range(0x21, 0x7e):
        c = chr(c)
        test = known
        conn = remote("crypto.chal.csaw.io", 1000)
        conn.recvline_contains("First Name:")
        conn.sendline(test + c)
        conn.recvline()
        conn.sendline(padding)
        conn.recvline()
        conn.sendline(str(age))
        ciphertext = conn.recvline_contains("Encrypted Information:")
        ciphertext = ciphertext.split()[2]
        ciphertext = str(ciphertext, "ascii")
        ciphertext = textwrap.wrap(ciphertext, 32)
        if ciphertext[known_block] == ciphertext[flag_block]:
            known += c
            print("\r{}".format(known))
            break
        conn.close()

    age -= 1
    padding = padding[:-1]

print(known)
