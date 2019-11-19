import angr
import sys
import logging

logging.getLogger('angr').setLevel(logging.CRITICAL)

result = ""

def should_abort(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return "Nope" in stdout_output

def is_successful(state):
    stdout_output = state.posix.dumps(sys.stdout.fileno())
    return "OK" in stdout_output

for i in range(999):
    idx = i + 1
    progname=str(idx).zfill(3) + ".c.out"
    project = angr.Project(progname)
    state = project.factory.entry_state()
    simgr = project.factory.simgr(state)
    simgr.explore(find=is_successful, avoid=should_abort)
    if simgr.found:
        solution_state=simgr.found[0]
        result += str(solution_state.posix.dumps(sys.stdin.fileno()))
        print(result)
    else:
        raise Exception("no solution found for {}".format(progname))