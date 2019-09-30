ctext = '3103163f142b381a283f0006081b1f311c3d390a282c001d7b28023d1c012e000213011d2002162c07003e081f2c500f'

# Warmup was XOR, so let's start by trying xor with this challenge as well

known = 'flag{' # Same drill, we know the first 5 bytes of the ciphertext
key = ''
ptext = ''

i = 0
for x in known:
    key += chr(int(ctext[i:i+2],16) ^ ord(x))
    i += 2

# If we xor those first 5 bytes against the ciphertext, we get a flag of 'WowXo'. xoring this as our key against the 
# ciphertext gives us gibberish, so it must not be the complete flag. 
print('Key:\t' + key) 
key += chr(int(ctext[-2:],16) ^ ord('}')) # We know the last byte of the flag has to be a closing brace, so let's try that
# If the key is 6 bytes, this makes the last byte of the ctext the 6th byte of the flag
print('Key:\t' + key) # Key: "WowXor" - seems promising

i = 0
n = 0
while i < len(ctext): # xor the key against the ciphertext
    cchar = ctext[i:i+2]
    ptext += chr(int(cchar, 16) ^ ord(key[n % len(key)]))
    i += 2
    n += 1

print(ptext) # flag{You_got_thisOne_too,GuessyouKnowmathright?}
