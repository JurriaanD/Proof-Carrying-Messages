from __future__ import annotations
import os
import sys
import time

import axolotl_curve25519 as curve
import serial

from aes import AESCipher, unpad
from listPorts import getPorts
from util import Opcodes, int_to_bytes, parse_string_to_bytes

class SerialComm:
    """ A class for everything related to serial communication with the Arduino """
    def __init__(self, port=None):
        self.do_decrypt_messages = False
        self.keys = dict()
        self.symm_key = None
        if port is None:
            ports = getPorts()
            if len(ports) == 0:
                print("No serial ports found. Please check your USB connection and try again.")
                sys.exit(1)
            port = ports[0]
            print(f"No port specified, defaulting to {port}")
        baudrate = 9600
        self.ser = serial.Serial(port, baudrate)

        # Restart arduino
        self.ser.setDTR(False)
        # print("Resetting Arduino...")
        time.sleep(1)
        self.ser.flushInput()
        self.ser.setDTR(True)

    def any_received(self) -> bool:
        """ Returns whether there is any data in the input buffer """
        return self.ser.inWaiting() > 0

    def read_serial(self) -> str:
        """ Reads UTF8 text message from the input buffer """
        return self.read_serial_raw().decode(encoding="utf8")

    def read_serial_raw(self) -> bytes:
        """ Reads message from the input buffer in bytes form """
        response_length = int.from_bytes(self.ser.read(2), byteorder='big')
        response = self.ser.read(response_length)
        if self.do_decrypt_messages is False:
            return response
        if self.symm_key is None:
            print("Need to do handshake before encrypting!")
            return bytes([])
        decrypted_response = unpad(AESCipher(self.symm_key).decryptECB(response))
        # flashhash = decryptedResponse[:16]
        return decrypted_response[16:]

    def write_serial(self, message: bytes):
        """ Writes the given bytes to the output buffer """
        # print("Sending " + (''.join('0x{:02x} '.format(x) for x in message))) # hex dump of outgoing message
        self.ser.write(message)
        self.ser.flush() # Wait until data is send

    def write_serial_string(self, string: str):
        """ Writes the given string to the output buffer """
        parts = parse_string_to_bytes(string)
        self.write_serial(parts["opcode"] + parts["dataLength"] + parts["data"])

    def close(self):
        """ Closes the connection with the Arduino """
        self.ser.close()

    def dh1(self):
        """ Executes the first part of the Diffie-Hellman key exchange """
        self.keys["private"] = curve.generatePrivateKey(os.urandom(32))
        self.keys["public"] = curve.generatePublicKey(self.keys["private"])

    def dh2(self):
        """ Executes the second half of the Diffie-Hellman key exchange """
        self.write_serial_string(str(Opcodes.ECDH_SHAKE))
        pub_arduino = int(self.read_serial_raw(), base=16).to_bytes(32, byteorder="big")
        self.write_serial(self.keys["public"])
        self.symm_key = curve.calculateAgreement(self.keys["private"], pub_arduino)[:16]

    def negotiate_symm_key(self):
        """ Executes Diffie-Hellman key exchange to establish a shared key """
        self.dh1()
        self.dh2()
        original_message = os.urandom(32)
        self.write_serial(original_message)
        received_message = AESCipher(self.symm_key).decryptECB(self.read_serial_raw())
        if original_message != received_message:
            print("Something went wrong while establishing a shared key")
            sys.exit(1)

    def has_symm_key(self) -> bool:
        """ Returns whether a symmetric key has already been established """
        return self.symm_key is not None

    def start_decrypting_messages(self):
        """ From now on, all incoming messages are encrypted. If the shared key hasn't been established yet, get one. """
        if not self.has_symm_key():
            print("Tried to establish a secure channel without a shared key.")
            print("Starting key exchange protocol...")
            self.negotiate_symm_key()
            print("Succesfully exchanged a secret key!")
            self.read_serial() # Arduino sends back symm key, very secure
        self.do_decrypt_messages = True

    def stop_decrypting_messages(self):
        """ From now on, all incoming messages are in plain text """
        self.do_decrypt_messages = False

class Message:
    """ A utility class to construct and modify messages """
    def __init__(self):
        self.code: int = None
        self.data: bytes = None

    def set_code(self, code: int) -> Message:
        """ Sets the opcode """
        self.code = code
        return self

    def set_data(self, data: bytes) -> Message:
        """ Sets the payload data to the given bytes """
        self.data = data
        return self

    def set_data_from_string(self, string: str) -> Message:
        """ Sets the payload data to the given string """
        self.data = bytearray(string, "utf8")

    def serialize(self) -> bytes:
        """ Returns the complete message as bytes, ready to be send to the Arduino """
        return int_to_bytes(self.code, 2) + int_to_bytes(len(self.data), 2) + self.data
