# Usage: python interactive.py [port]
# To install pyserial, run pip install pyserial or conda install pyserial
import signal
import sys
import os
from time import sleep
from comm import SerialComm
from util import parse_string_to_bytes, BenchOpcodes

NB_BENCH = 10

# Serial communication setup
comm = SerialComm(sys.argv[1] if len(sys.argv) > 1 else None)
comm.dh1()

def signal_handler(_sig, _frame):
    """ Nicely exit on Ctrl+C (SIGINT) """
    print("\b\b\rThank you for encrypting with us today :)")
    comm.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def handle_input(inp: str):
    """ Transforms the user input and sends it to the Arduino """
    parts = parse_string_to_bytes(inp)
    opcode = int.from_bytes(parts["opcode"], byteorder="big")

    comm.write_serial(parts["opcode"] + parts["dataLength"] + parts["data"])

    if opcode == BenchOpcodes.DH2:
        for _ in range(NB_BENCH):
            comm.write_serial(os.urandom(32))

while True:
    # Read bursts of messages instead of one
    # Simplifies receiving multiple timings
    while True:
        print(comm.read_serial())
        sleep(0.1)
        if not comm.any_received():
            break

    handle_input(input(">>> "))
