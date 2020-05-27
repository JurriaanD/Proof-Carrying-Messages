#!/usr/bin/env python3
import binascii
import os
import sys
from time import sleep, time
from termcolor import colored

import serial

sys.path += [ os.path.join(os.path.split(__file__)[0], '../libs/python') ]

from listPorts import getPorts

def read_message(ser: serial.Serial) -> dict:
   #Message structure
   #+---------+-----------+
   #| Timer   | XOR value |
   #+---------+-----------+
   #| 2 bytes | 1 byte    |
   #+---------+-----------+
   msg_length = int.from_bytes(ser.read(2), byteorder='big')
   assert msg_length == 3
   message_data = dict()
   message_data['elapsed_time'] = int.from_bytes(ser.read(2), byteorder='big')
   message_data['xor'] = int.from_bytes(ser.read(1), byteorder='big');
   return message_data


def main():
   # Setup serial connection
   ports = getPorts()
   if len(ports) == 0:
      print("No serial ports found. Please check your USB connection and try again.")
      sys.exit(1)
   port = ports[0]
   print(f"No port specified, defaulting to {port}")
   ser = serial.Serial(port, 9600)

   # Restart arduino
   ser.setDTR(False)
   print("Resetting Arduino...")
   sleep(1)
   ser.setDTR(True)

   # Read 'Arduino is ready' message
   response_length = int.from_bytes(ser.read(2), byteorder='big')
   print(ser.read(response_length).decode("utf8"))
   # Acknowledge welcome message
   ser.write(b's')
   ser.flush()

   while True:
      message_data = read_message(ser)
      print(f"XORed memory in: {message_data['elapsed_time']}ms")
      print(f"Calculated value is {message_data['xor']}\n")

if __name__ == "__main__":
   main()
