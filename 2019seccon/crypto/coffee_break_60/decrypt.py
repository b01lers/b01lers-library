import sys
from Crypto.Cipher import AES
import base64
import binascii

#ciphertext = "MUgyesN6cJKrLGSIZfy2lw=="
ciphertext = "FyRyZNBO2MG6ncd3hEkC/yeYKUseI/CxYoZiIeV2fe/Jmtwx+WbWmU1gtMX9m905"

def decrypt(key, text):
    s = ''
    for i in range(len(text)):
        c = ord(text[i]) - 0x20
        k = ord(key[i % len(key)]) - 0x20
        print("after add: {}".format(hex(c)))
        c = c - k
        print("subtraction: {}".format(hex(c)))
        while c < 0:
            c += (0x7e - 0x20 + 1)
        print("splain: {} skey: {}".format(hex(c), hex(k)))
        print("plain: {} key: {}".format(hex(c + 0x20), hex(k + 0x20)))
        s += chr(c + 0x20)
    return s

key1 = "SECCON"
key2 = "seccon2019"

ciphertext=base64.b64decode(ciphertext)
print("c:"+str(binascii.hexlify(bytearray(ciphertext))))
cipher = AES.new(key2 + chr(0x00) * (16 - (len(key2) % 16)), AES.MODE_ECB)
#dec1 = cipher.decrypt(ciphertext)[:-5]
dec1 = "\x27\x6a\x66\x66\x7e\x7c\x4f\x78\x39\x27\x33\x34\x47\x39\x23\x67\x35\x32\x46\x3f\x34\x38\x39\x3e\x42\x25\x7c\x29\x31\x37\x33\x7e\x29\x25\x38\x2e\x27\x6a\x66\x66\x7e\x7c\x51"
print("1:"+str(binascii.hexlify(bytearray(str(dec1)[:-3], 'utf-8'))))
#print("1:"+str(binascii.hexlify(bytearray(dec1))))
dec2 = decrypt(key1, str(dec1))
print("2:"+str(binascii.hexlify(bytearray(dec2, 'utf-8'))))
print("2:"+str(dec2))
