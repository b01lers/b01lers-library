def printFlag(s):
   o = ''
   for i in range(len(s)):
       o += chr(((((ord(s[i]) ^ 0xf) - 0x1d) * 8) % 0x5f) + ord(' '))
   return o
   
if __name__ == '__main__':
    s = "\\PJ\\fC|)L0LTw@Yt@;Twmq0Lw|qw@w2$a@0;w|)@awmLL|Tw|)LwZL2lhhL0k"
    print(printFlag(s))



