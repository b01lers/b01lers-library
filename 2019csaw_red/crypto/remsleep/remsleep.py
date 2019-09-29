import functools
from Crypto.Cipher import ChaCha20

def xor(a, b):
    return ''.join(chr(ord(x) ^ ord(y)) for x,y in zip(a, b))

def encode(flag, pieces):
    key = functools.reduce(xor,pieces)
    cipher = ChaCha20.new(key=key, nonce=pieces[0][:8])
    enc = cipher.encrypt(flag)
    return enc.encode('hex')

if __name__ == '__main__':
    f = open('/root/flag.txt','r')
    flag = f.read()
    f.close()
    try:
        print 'How many pieces did you split your key into?'
        count = int(raw_input(''))
        pieces = []
        req_len = 32
        for i in range(count):
            print 'Hex-encoded piece please'
            piece = raw_input('')
            if len(piece) < req_len:
                piece = '0'*(req_len-len(piece)) + piece
            elif len(piece) > req_len:
                piece = piece[:req_len]
            pieces.append(piece)
        print "Here's the flag! {}".format(encode(flag, pieces))
    except:
        print "Bye bye"