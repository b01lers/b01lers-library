'''
Explanation
The given information shows two ciphertext, two public keys, and a single common modulus. With this information we can apply bezout's identity using the extended euclidean algorithm. Which states that there are two coefficients, which we can call a and b, such that a * e1 + b * e2 = gcd(e1,e2). We also know that the gcd of our public keys, 13 and 15, is 1 since they are coprime.
'''


from fractions import gcd
n = 5196832088920565976847626600109930685983685377698793940303688567224093844213838345196177721067370218315332090523532228920532139397652718602647376176214689

e1 = 15

e2 = 13

c1 = 2042084937526293083328581576825435106672034183860987592520636048680382212041801675344422421233222921527377650749831658168085014081281116990629250092000069

c2 = 199621218068987060560259773620211396108271911964032609729865342591708524675430090445150449567825472793342358513366241310112450278540477486174011171344408

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise ValueError('Modular inverse does not exist.')
    else:
        return x % m

def attack(c1, c2, e1, e2, N):
    if gcd(e1, e2) != 1:
        raise ValueError("Exponents e1 and e2 must be coprime")
    s1 = modinv(e1,e2)
    s2 = (gcd(e1,e2) - e1 * s1) / e2
    temp = modinv(c2, N)
    m1 = pow(c1,s1,N)
    m2 = pow(temp,-s2,N)
    return (m1 * m2) % N


def main():
    try:
        message = attack(c1, c2, e1, e2, n)
        print '\nPlaintext message:\n%s' % format(message, 'x').decode('hex')
    except Exception as e:
        print e.message

main()
