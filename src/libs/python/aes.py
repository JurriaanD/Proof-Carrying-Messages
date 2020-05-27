import os

from Crypto.Cipher import AES
from Crypto.Util import Counter

# Padding for the input string -- not related to encryption itself.
BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

class AESCipher:
    """ Wrapper class for Crypto.Cipher.AES """
    def __init__(self, key: bytes, initCounterValue=1):
        self.key = key
        self.CTR = AES.new(self.key, AES.MODE_CTR, counter=Counter.new(128, initial_value=initCounterValue))

    def encryptECB(self, plaintext: str) -> bytes:
        """ Encrypt the given string with AES in ECB mode """
        return AES.new(self.key, AES.MODE_ECB).encrypt(pad(plaintext))

    # This should probably also unpad, but we're using this in the ECDH in a way that
    # we *don't* want padding.
    def decryptECB(self, ciphertext: bytes) -> bytes:
        """ Decrypt the given ciphertext with AES in ECB mode """
        return AES.new(self.key, AES.MODE_ECB).decrypt(ciphertext)

    def encryptCBC(self, plaintext: str, iv: bytes):
        """ Encrypt the given string with AES in CBC mode """
        return AES.new(self.key, AES.MODE_CBC, IV=iv).encrypt(pad(plaintext))

    def decryptCBC(self, ciphertext: bytes, iv: bytes):
        """ Decrypt the given ciphertext with AES in CBC mode """
        return AES.new(self.key, AES.MODE_CBC, IV=iv).decrypt(ciphertext)

    def encryptCTR(self, plaintext: str) -> bytes:
        """ Encrypt the given string with AES in CTR mode """
        return self.CTR.encrypt(plaintext)

    def setCounterValue(self, val: int) -> bytes:
        """ Sets the counter value (only for using CTR mode) """
        self.CTR = AES.new(self.key, AES.MODE_CTR, counter=Counter.new(128, initial_value=val))

if __name__ == "__main__":
    cipher = AESCipher(bytes([0x39, 0x79, 0x24, 0x42, 0x26, 0x45, 0x29, 0x48, 0x40, 0x4D, 0x63, 0x51, 0x66, 0x54, 0x6A, 0x57]))
    iv = os.urandom(16)
    encrypted = cipher.encryptCBC("hello world", iv)
    decrypted = cipher.decryptCBC(encrypted, iv)
    print(encrypted)
    print(decrypted)
    print(unpad(decrypted))
