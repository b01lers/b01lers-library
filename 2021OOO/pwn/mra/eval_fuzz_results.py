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

files = []

procs = []
testcases = Path("outputs2/crashes")
for portbase, testcase in enumerate(testcases.iterdir()):
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
    with open(tc, "rb") as tcc:
        files.append(tcc)
        content = tcc.read()
        r = process(["qemu-aarch64-static", "-g", str(port), "./mra"])
        procs.append(r)
        print(content)
        try:
            r.sendline(content)
        except:
            continue
        with open("gdbscript.gdb", "w") as srcfile:
            srcfile.write(SRCTEMPLATE.format(port))
        try:
            proc = subprocess.run(["gdb-multiarch", "-q", "-x", "gdbscript.gdb"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            op = proc.stdout
        except:
            try:
                proc.kill()
                r.close()
            except:
                pass
            continue
        print("CRASHES========================")
        found_crashes = re.findall(PC_REG, op.decode("utf-8", errors="ignore"))
        print(found_crashes)
        print("BT=============================")
        backtrace = re.findall(BT_REG, op.decode("utf-8", errors="ignore"))
        print(backtrace)
        print("===============================")
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

