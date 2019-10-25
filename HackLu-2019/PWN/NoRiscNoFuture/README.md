# No Risc No Future
Running a program in a foreign architecture can feel like an arcane, hard to debug endeavor.

To help you get started, we list some handy commands to bootstrap a more familiar setup.

## Docker Setup
Several participants seem to have experienced inconsistencies of exploit behavior when running locally versus remotely.

In order to help with this issue, we supply a docker file which should exactly replicate our challenge setup.

In order to use the docker:
1. build the docker container: `./build.sh`
2. start the docker container: `./run_docker.sh`
3. connect to the challenge: `nc localhost 1338`

We verified our reference exploit to work against this setup.

## Local Debugging Setup
qemu-user allows exposing a gdb stub before running the binary. This can be connected to from gdb.

In a first shell, expose the stub:
```
./qemu-mipsel-static -g 1234 no_risc_no_future
```

In a second shell, connect to the waiting process:
```
gdb-multiarch -ex "break main" -ex "target remote localhost:1234" -ex "continue" ./no_risc_no_future
```

Now the process should break at main and you can debug the process.

Enjoy!