import sys
import socket
import logging
import unittest

from types import ModuleType
from contextlib import contextmanager

from simulators.server import Server
from simulators.common import BaseSystem


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = Server(('', 10000), 'mymodule')
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_proper_request(self):
        response = self.get_response(msg='#command:a,b,c!')
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = self.get_response('#wrong_command:foo!')
        self.assertRegexpMatches(response, 'you sent a wrong command')

    def _test_value_error(self):
        """The message of ValueError in the logfile"""
        # TODO

    def _test_unexpected_error(self):
        """The unexpected error in the logfile"""
        # TODO

    def test_custom_command_with_parameters(self):
        response = self.get_response(msg='$custom_command:a,b,c!')
        self.assertRegexpMatches(response, 'ok_abc')

    def test_custom_command_withoud_parameters(self):
        response = self.get_response(msg='$custom_command!')
        self.assertRegexpMatches(response, 'no_params')

    def get_response(self, msg, timeout=2.0, response=True):
        with socket_context(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect(self.server.server_address)
            sock.sendall(msg)
            return sock.recv(1024) if response else b''


class System(BaseSystem):

    header = b'#'
    tail = b'!'

    def __init__(self):
        self.msg = b''

    def parse(self, byte):
        # Example of msg: #command_name:par1,par2,par3!
        if byte == self.header:
            self.msg = byte
            return True
        elif self.msg.startswith(self.header):
            self.msg += byte
            if byte == self.tail:
                name, params_str = self.msg[1:-1].split(':')
                if name == 'wrong_command':
                    return b'you sent a wrong command'
                elif name == 'unexpected':
                    raise ValueError('unexpected value')
                params = params_str.split(',')
                response = b''
                for param in params:
                    response += param * 2
                return response
            else:
                return True
        else:
            return False

    def custom_command(self, *params):
        params_str = ''.join(list(params))
        msg = 'ok_' + params_str if params else 'no_params'
        return '%s (id: %d)' % (msg, id(self))


@contextmanager
def socket_context(*args, **kw):
    sock = socket.socket(*args, **kw)
    try:
        yield sock
    finally:
        sock.close()


# Create a dummy module to use as a system
mymodule = ModuleType('simulators.mymodule')
mymodule.System = System
sys.modules['simulators.mymodule'] = mymodule


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': [],
        }


if __name__ == '__main__':
    unittest.main()
