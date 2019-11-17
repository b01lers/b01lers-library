The flag is encrypted and then base64'd. Here it is: E2zVOQfaRwYoMiTapzA03RQJJmtq1KuHTCuWGdVo/+w=

To decrypt it you will need to implement the amazing Key Derivation Function called CictroKDF (not to be confused with the well-known CictroHash). After a key has been derived you can use it with AES ECB mode to decrypt the flag.

The message for the KDF is: Are you silly? I'm still gunna send it!!

Wrap the flag in RITSEC{}

Author: cictrone

Hint: example setup Key: "Totally not a black box, I swear" Plaintext: "not a black box!" Ciphertext (base64'ed): GywB/y8LEXN335lUf6QWzA==

Hint2: pi_func(ord('a'), 0) = 42 pi_func(pi_func(ord('a'), 0), 1) = 70 pi_func(ord('b'), 0) = 46 pi_func(pi_func(ord('b'), 0), 1) = 228