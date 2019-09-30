#Here's the encryptor code:

def encrypt(string, key):
    out = ""
    for s in range(len(string)):
        c = ord(string[s]) # Get numeric value of m_i
        c += ord(key[s%len(key)]) - ord('A') # (key[s % len(key)] - ord('A')
        c = chr(c - ord('A'))
        out += c
    return out

# My Solution :)
def find_key(plaintext, ciphertext):
    out = ""
    # Break the ciphertext into 2 character blocks (cuz its a hex encoding)
    cipher_arr = [ciphertext[s:s+2] for s in range(0, len(ciphertext), 2)]

    for s in range(len(plaintext)):
        # Undo the Encrypt by undoing all the operations done on the plaintext
        # Plaintext[i] = Ciphertext[i] - plaintext[i] + (2 * 'A')
        out += chr(int(cipher_arr[s], 16) - ord(plaintext[s])  + (2 * ord('A')))

    print(out)

if __name__ == "__main__":
    find_key("Hellothere everybody how are you doing today_long-plaintexts-are fun", "2c4f4b5168535a574f57064853485e5b3f5c4856124e525402406942076b60521156565358440057615644693c5e554d530a605d4064525e445d6d521f534f5706495251")

#Here's the plaintext:
# Hellothere everybody how are you doing today_long-plaintexts-are fun
#Here's the ciphertext:
# 2c4f4b5168535a574f57064853485e5b3f5c4856124e525402406942076b60521156565358440057615644693c5e554d530a605d4064525e445d6d521f534f5706495251
