def parse_string_to_bytes(string: str) -> dict:
    """ Extracts opcode, data and datalength from terminal inputline """
    inp = string.split(' ')
    opcode = int(inp[0])
    data = ' '.join(inp[1:])
    data_length = len(data)
    res = dict()
    res["opcode"] = int_to_bytes(opcode, 2)
    res["dataLength"] = int_to_bytes(data_length, 2)
    res["data"] = bytearray(data, "utf-8")
    return res

def string_to_bytes(string: str) -> bytes:
    """ Converts a UTF-8 string to bytes """
    return bytearray(string, 'utf8')

def int_to_bytes(num: int, nb_bytes: int) -> bytes:
    """ Converts an integer to it's big endian representation """
    return num.to_bytes(nb_bytes, byteorder='big')

def bytes_to_hex(byt: bytes) -> str:
    """ Converts bytes to a hexadecimal string representation """
    return ''.join('{:02x}'.format(x) for x in byt)

def bytes_to_int(byt: bytes) -> int:
    """ Converts bytes to a big endian integer """
    return int.from_bytes(byt, byteorder='big')

class Opcodes:
    """ Enum for the opcodes in interactive mode """
    ECHO, SHA256, MD5, AES_ECB, AES_CTR, AES_CBC, ECDH_SHAKE, MD5_FLASH, CRYPTO_SWITCH, SENSOR_READING = range(1, 11)

class BenchOpcodes:
    """ Enum for the opcodes in benchmark mode """
    AES_ECB, DH1, DH2, MD5_FLASH, SENSOR_READING, SENSOR_READING_ENC, SENSOR_READING_ENC_PROOF = range(1, 8)
