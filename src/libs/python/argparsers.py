import argparse

ECHO_PARSER = argparse.ArgumentParser(description="Echo the same text back")
ECHO_PARSER.add_argument('text', help='Text to echo', nargs="*")

SHA256_PARSER = argparse.ArgumentParser(description="Echo the SHA256 hash of the given text")
SHA256_PARSER.add_argument('text', help='Text to hash', nargs="*")

MD5_PARSER = argparse.ArgumentParser(description="Echo the MD5 hash of the given text")
MD5_PARSER.add_argument('text', help='Text to hash', nargs="*")

AES_PARSER = argparse.ArgumentParser(description='Echo the given text encrypted with AES')
AES_SUBPARSERS = AES_PARSER.add_subparsers(title='modes')

AES_ECB_PARSER = AES_SUBPARSERS.add_parser('ecb', help='Electronic Code Book Mode')
AES_ECB_PARSER.add_argument('text', help='Text to encrypt', nargs="*")

AES_CTR_PARSER = AES_SUBPARSERS.add_parser('ctr', help='CounTeR Mode')
AES_CTR_PARSER.add_argument('text', help='Text to encrypt', nargs="*")

AES_CBC_PARSER = AES_SUBPARSERS.add_parser('cbc', help='Cipher Block Chaining Mode')
AES_CBC_PARSER.add_argument('text', help='Text to encrypt', nargs="*")

ECDH_PARSER = argparse.ArgumentParser(description="Negotiates a shared key with the Arduino")

FLASHHASH_PARSER = argparse.ArgumentParser(description="Echo the MD5 hash of the Arduino's flash memory")
FLASHHASH_PARSER.add_argument('--bounds', help='Lower and upper bound of the memory that should get hashed', nargs=2, type=int, metavar=('lower', 'upper'))

CRYPTO_SWITCH_PARSER = argparse.ArgumentParser(description="Encrypt all future communication with a symmetric key")
CRYPTO_SWITCH_PARSER.add_argument('state', choices=['on', 'off'])

SENSOR_READING_PARSER = argparse.ArgumentParser(description="Echo a sensor reading from the Arduino")

TESTS_PARSER = argparse.ArgumentParser(description="Runs the test suite")
