ctext = '0f05080e1220360106190c3610061c360207061e361e01081d4e1a2e0600070e362607210c1b0c4814'

# After running the ciphertext through the common classical ciphers and getting nothing, let's try an xor decryption

known = 'flag{' # we know the flag format is flag{FLAG_TEXT}
key = ''
ptext = ''

i = 0
for x in known:
    key += chr(int(ctext[i:i+2],16) ^ ord(x)) # XOR the known flag characters against the ciphertext to determine key characters
    i += 2

print('Key:\t' + key) # turns out the key is just a single character key (i)

i = 0
n = 0
while i < len(ctext): # xor the key against the ciphertext
    cchar = ctext[i:i+2]
    ptext += chr(int(cchar, 16) ^ ord(key[n % len(key)]))
    i += 2
    n += 1

print(ptext) # flag{I_hope_you_know_what'sGoing_OnHere!}
