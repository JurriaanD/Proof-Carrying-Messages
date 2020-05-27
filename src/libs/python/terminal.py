import sys
from termcolor import colored

from cmd2 import Cmd, with_argparser

import argparsers
import comm
import tests
from util import Opcodes, int_to_bytes, string_to_bytes
from comm import Message


class Test(Cmd):
    """ CLI application to communicate with an Arduino """
    intro = 'Welcome to the Proof-Carrying Messaging Terminal for Arduino. \nType help or ? to list commands.\n'
    prompt = '> '

    ##### Setup #####
    def __init__(self):
        super().__init__()
        self.continuation_prompt = "... "
        self.default_error = "{} is not a recognized command"
        self.hidden_commands = ['alias', 'macro', 'run_script', 'shell', 'edit', 'history', 'py', 'run_pyscript', 'set', 'shortcuts', '_relative_run_script', 'eof']
        self.comm = comm.SerialComm(sys.argv[1] if len(sys.argv) > 1 else None)
        self.comm.read_serial() # Arduino is ready... message

    def print_response(self):
        """ Prints a response from the Arduino """
        print(f">>> {self.comm.read_serial()}")

    @with_argparser(argparsers.ECHO_PARSER)
    def do_echo(self, opts):
        """ Echo command """
        msg = Message().set_code(Opcodes.ECHO)
        msg.set_data_from_string(' '.join(opts.text))
        self.comm.write_serial(msg.serialize())
        self.print_response()

    @with_argparser(argparsers.SHA256_PARSER)
    def do_sha256(self, opts):
        """ sha256 command """
        msg = Message().set_code(Opcodes.SHA256)
        msg.set_data_from_string(' '.join(opts.text))
        self.comm.write_serial(msg.serialize())
        self.print_response()

    @with_argparser(argparsers.MD5_PARSER)
    def do_md5(self, opts):
        """ md5 command """
        msg = Message().set_code(Opcodes.MD5)
        msg.set_data_from_string(' '.join(opts.text))
        self.comm.write_serial(msg.serialize())
        self.print_response()

    @with_argparser(argparsers.AES_PARSER)
    def do_aes(self, opts):
        """ AES command, dispatches to the handler for the specified mode """
        func = getattr(opts, 'func', None)
        if func is not None:
            # Call whatever subcommand function was selected
            func(self, opts)
        else:
            # No subcommand was provided, so call help
            self.do_help('aes')

    def aes_ecb(self, opts):
        """ AES ECB command handler"""
        msg = Message().set_code(Opcodes.AES_ECB)
        msg.set_data_from_string(' '.join(opts.text))
        self.comm.write_serial(msg.serialize())
        self.print_response()

    def aes_ctr(self, opts):
        """ AES CTR command handler """
        msg = Message().set_code(Opcodes.AES_CTR)
        msg.set_data(string_to_bytes('0'*15 + '1' + ' '.join(opts.text)))
        print(colored("⚠️   The IV is always set to be 0000000000000001 in interactive mode.", 'yellow', attrs=["bold"]))
        self.comm.write_serial(msg.serialize())
        self.print_response()

    def aes_cbc(self, opts):
        """ AES CBC command handler """
        msg = Message().set_code(Opcodes.AES_CBC)
        msg.set_data(string_to_bytes('0'*15 + '1' + ' '.join(opts.text)))
        print(colored("⚠️   The IV is always set to be 0000000000000001 in interactive mode.", 'yellow', attrs=["bold"]))
        self.comm.write_serial(msg.serialize())
        self.print_response()

    argparsers.AES_ECB_PARSER.set_defaults(func=aes_ecb)
    argparsers.AES_CTR_PARSER.set_defaults(func=aes_ctr)
    argparsers.AES_CBC_PARSER.set_defaults(func=aes_cbc)

    @with_argparser(argparsers.ECDH_PARSER)
    def do_ecdh(self, _opts):
        """ Elliptic Curve Diffie-Hellman command """
        self.comm.negotiate_symm_key()
        self.print_response()

    @with_argparser(argparsers.ECDH_PARSER)
    def do_dh(self, opts):
        """ Alias for Elliptic Curve Diffie-Hellman command """
        self.do_ecdh(opts)

    @with_argparser(argparsers.FLASHHASH_PARSER)
    def do_generate_proof(self, opts):
        """ Command to hash the flash memory """
        msg = Message().set_code(Opcodes.MD5_FLASH)
        if opts.bounds is None:
            msg.set_data(bytes())
        else:
            msg.set_data(int_to_bytes(opts.bounds[0], 2) + int_to_bytes(opts.bounds[1], 2))
        self.comm.write_serial(msg.serialize())
        self.print_response()

    @with_argparser(argparsers.CRYPTO_SWITCH_PARSER)
    def do_secure_channel(self, opts):
        """ Command to toggle secure mode """
        msg = Message().set_code(Opcodes.CRYPTO_SWITCH)
        if opts.state == 'on':
            self.comm.start_decrypting_messages()
            msg.set_data_from_string('1')
        else:
            self.comm.stop_decrypting_messages()
            msg.set_data_from_string('0')
        self.comm.write_serial(msg.serialize())
        self.print_response()

    @with_argparser(argparsers.SENSOR_READING_PARSER)
    def do_sensor_reading(self, _opts):
        """ Command to get a sensor reading from the Arduino """
        msg = Message().set_code(Opcodes.SENSOR_READING)
        msg.set_data(bytes())
        self.comm.write_serial(msg.serialize())
        self.print_response()

    @with_argparser(argparsers.TESTS_PARSER)
    def do_tests(self, _opts):
        """ Command run test suite """
        tests.run_tests(self.comm)

    def do_eof(self, _opts):
        """ Triggered when the user presses Ctrl+D """
        print("Shutting down connection...")
        self.comm.close()
        return True

sys.exit(Test().cmdloop())
