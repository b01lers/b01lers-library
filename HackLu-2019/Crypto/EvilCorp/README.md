You were called by the Incident Response Team of Evil Corp, the urgently need your help. Somebody broke into the main server of the company, bricked the device and stole all the files! Nothing is left! This should have been impossible. The Hacker used some secret backdoor to bypass authentication. Without the knowledge of the secret backdoor other servers are at risk as well! The Incident Response Team has a full packet capture of the incident and performed an emergency cold boot attack on the server to retrieve the contents of the memory (its a really important server, Evil Corp is always ready for such kinds of incidents. However they were unable to retrieve much information from the RAM, what's left is only some parts of the "key_block" of the TLS server. Can you help Evil Corp to analyze the exploit the attacker used?

(Flag is inside of the attackers' secret message).


TT = Could not recover

Keyblock:
6B 4F 93 6A TT TT TT TT TT TT 00 D9 F2 9B 4C B0
2D 88 36 CF B0 CB F1 A6 7B 53 B2 00 B6 D9 DC EF
66 E6 2C 33 5D 89 6A 92 ED D9 7C 07 49 57 AD E1
TT TT TT TT TT TT TT TT 56 C6 D8 3A TT TT TT TT
TT TT TT TT TT TT TT TT 94 TT 0C EB 50 8D 81 C4
E4 40 B6 26 DF E3 40 9A 6C F3 95 84 E6 C5 86 40
49 FD 4E F2 A0 A3 01 06

Download challenge files
