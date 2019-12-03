s = 'UTBUGzb1s2^etlq>^O2w2s^i25se^1g^x1t|'
o=''
for i in range(len(s)):
    o += chr(ord(s[i]) ^ 1)
print(o)
