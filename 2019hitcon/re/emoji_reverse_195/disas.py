#!/usr/bin/env python3

from pwn import *

def disassembler():
    emoji1 = {
        "1": [chr(0x1f233), 'nop'],
        "2": [chr(0x2795), 'add'],
        "3": [chr(0x2796), 'sub'],
        "4": [chr(0x274c), 'mul'],
        "5": [chr(0x275c), 'mod'],
        "6": [chr(0x274e), 'xor'],
        "7": [chr(0x1f46b), 'and'],
        "8": [chr(0x1f480), 'lt'], # a = pop, b = pop, if a < b: 1, else 0
        "9": [chr(0x1f4af), 'eq'],
        "10": [chr(0x1f680), 'jmp'], # a
        "11": [chr(0x1f236), 'jnz'], # b
        "12": [chr(0x1f21a), 'jz'],  # c # a = pop, b = pop if b != 0, jump a
        "13": [chr(0x23ec), 'push'], # d
        "14": [chr(0x1f51d), 'pop'], # e # Gets emoji from table 2 and pushes the value to the stack
        "15": [chr(0x1f4e4), 'dereferenceandpush'], # f
        "16": [chr(0x1f4e5), 'dereferenceandwrite'], # 10 # a = pop, b = pop a = controlable_memory_index b = which byte to read. pops 2, pushes value from controled locations
        "17": [chr(0x1f195), 'new'], # 11 # a = pop, b = pop a = controlable_memory_index b = which byte to write to. c = value to write
        "18": [chr(0x1f193), 'free'], # 12 # Creates new something, puts in first slot
        "19": [chr(0x1f4c4), 'readfromlocation'], # 13 # Frees and sets to null
        "20": [chr(0x1f4dd), 'writetolocation'], # 14
        "21": [chr(0x1f521), 'writebyte'], # 15 # check < 10 ,writes some area
        "22": [chr(0x1f522), 'write'], # 16
        "23": [chr(0x1f6d1), 'exit'] # 17
    }

    emoji2 = {
        "0": chr(0x1f600),
        "1": chr(0x1f601),
        "2": chr(0x1f602),
        "3": chr(0x1f923),
        "4": chr(0x1f61c),
        "5": chr(0x1f604),
        "6": chr(0x1f605),
        "7": chr(0x1f606),
        "8": chr(0x1f609),
        "9": chr(0x1f60a),
        "10": chr(0x1f60d),
    }
    with open('./chal.evm') as f:
        while True:
            c = f.read(1)
            if not c:
                break
            try:
                mem = [v[1] for k, v in emoji1.items() if v[0] == c][0]
                print(mem)
            except Exception as e:
                try:
                    mem = [k for k, v in emoji2.items() if v== c][0]
                    print(mem)
                except Exception as e:
                    print(e)

disassembler()


