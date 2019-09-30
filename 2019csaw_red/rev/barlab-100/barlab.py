import angr
import sys

# a super simple angr find/avoid solver. There's not much path blowup with this one.
rebase = 0x400000
find = 0xb8b
avoids = [rebase + 0xb27, rebase + 0xb78]

p = angr.Project('./barlab')
initial_state = p.factory.entry_state()
simgr = p.factory.simgr(initial_state)
simgr.explore(find=(find + rebase), avoid = avoids)

if simgr.found:
    sol_state = simgr.found[0]
    solbytes = sol_state.posix.dumps(sys.stdin.fileno())
    sys.stdout.write(str(solbytes.decode("utf-8")))
else:
    print("Nope :(")

