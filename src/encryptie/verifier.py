#!/usr/bin/env python3
import os
import sys
from time import sleep, time
from termcolor import colored

import serial

sys.path += [ os.path.join(os.path.split(__file__)[0], '../libs/python') ]

from aes import AESCipher, unpad
from listPorts import getPorts

AES_NONCE_LENGTH = 16
AES_KEY = bytes([0x39, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57])

def read_message(ser: serial.Serial) -> dict:
   #                    Message structure
   #+---------+-----------+--------+
   #| Timer   | AES nonce |  Data  |
   #+---------+-----------+--------+
   #| 2 bytes | 16 bytes  | 1 byte |
   #+---------+-----------+--------+
   # The data is encrypted with AES in CBC mode
   msg_length = int.from_bytes(ser.read(2), byteorder='big')
   msg_components = dict()
   msg_components['timer'] = int.from_bytes(ser.read(2), byteorder='big')
   aes_nonce = ser.read(16)
   encrypted_data = ser.read(msg_length - 2 - 16)
   decrypted_data = unpad(AESCipher(AES_KEY).decryptCBC(encrypted_data, aes_nonce))
   msg_components['data'] = int.from_bytes(decrypted_data, byteorder='big')
   return msg_components


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
      # Wait for message
      msg = read_message(ser)
      elapsed_time = msg['timer']
      data = msg['data']

      print(f"Measurement: {data}")
      print(f"Time elapsed: {elapsed_time}ms")

if __name__ == "__main__":
   main()
