#!/usr/bin/env python3
import binascii
import hashlib
import hmac
import os
import sys
from time import sleep, time
from termcolor import colored

import serial

sys.path += [ os.path.join(os.path.split(__file__)[0], '../libs/python') ]

from aes import AESCipher, unpad
from intelhex import IntelHex
from listPorts import getPorts

AES_NONCE_LENGTH = 16
MAC_LENGTH = 20
AES_KEY = bytes([0x39, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57])
MAC_KEY = bytes([0x93, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57, 0xff, 0xff, 0xff, 0xff])

def read_message(ser: serial.Serial) -> dict:
   #                    Message structure
   #+---------+-----------+------------+----------+--------+
   #| Timer   | AES nonce | HMAC nonce |   MAC    |  Data  |
   #+---------+-----------+------------+----------+--------+
   #| 2 bytes | 16 bytes  | 20 bytes   | 20 bytes | 1 byte |
   #+---------+-----------+------------+----------+--------+
   # The HMAC nonce, MAC and data are encrypted with AES in CBC mode
   msg_length = int.from_bytes(ser.read(2), byteorder='big')
   msg_components = dict()
   msg_components['timer'] = int.from_bytes(ser.read(2), byteorder='big')
   aes_nonce = ser.read(16)
   encrypted_part = ser.read(msg_length - 2 - 16)
   decrypted_part = unpad(AESCipher(AES_KEY).decryptCBC(encrypted_part, aes_nonce))
   msg_components['mac_nonce'] = decrypted_part[:20]
   msg_components['mac'] = decrypted_part[20:40]
   msg_components['data'] = int.from_bytes(decrypted_part[-1:], byteorder='big')
   return msg_components


def main():
   # Check if hexfile exists
   hexfile = "microvisor.hex"
   if not os.path.isfile(hexfile):
      print("ERROR: File not found:", hexfile)
      sys.exit(2)
   ih = IntelHex(hexfile)

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
      mac_nonce = msg['mac_nonce']
      remote_mac = msg['mac']
      data = msg['data']

      # Calc digest
      hmac_gen = hmac.new(MAC_KEY, None, hashlib.sha1)
      hmac_gen.update(ih.tobinstr(0,30*1024-1))
      hmac_gen.update(msg['mac_nonce'])
      local_mac = hmac_gen.digest()

      if (remote_mac == local_mac):
         print(colored(f"✓ Received message has valid proof ", 'green', attrs=["bold"]) + f"({remote_mac.hex()})")
      else:
         print(colored(f"✗ Received message with invalid proof!", "red", attrs=["bold"]))
      print(f"Measurement: {data}")
      print(f"Time to create message: {elapsed_time}ms")

if __name__ == "__main__":
   main()
