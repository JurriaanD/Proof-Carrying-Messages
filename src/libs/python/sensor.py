import sys
import os
from time import sleep

import serial

from listPorts import getPorts
from aes import AESCipher, unpad

NONCE_LENGTH = 16
AES_KEY = bytes([0x39, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57])

ports = getPorts()
if len(ports) == 0:
    print("No serial ports found. Please check your USB connection and try again.")
    sys.exit(1)
port = ports[0]
print(f"No port specified, defaulting to {port}")
baudrate = 9600
ser = serial.Serial(port, baudrate)

# Restart arduino
ser.setDTR(False)
print("Resetting Arduino...")
sleep(1)
ser.setDTR(True)

# Read 'Arduino is ready' message
response_length = int.from_bytes(ser.read(2), byteorder='big')
ser.read(response_length)

while True:
    nonce = os.urandom(NONCE_LENGTH)
    ser.write(nonce)
    ser.flush()
    response_length = int.from_bytes(ser.read(2), byteorder='big')
    response = ser.read(response_length)
    decrypted_response = unpad(AESCipher(AES_KEY).decryptCBC(response, nonce))
    print(int.from_bytes(decrypted_response, byteorder='big'))

    sleep(2)
