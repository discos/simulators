import sys
import time
import socket
import datetime
import unittest

from types import ModuleType
from contextlib import contextmanager

from simulators.server import Server, Simulator
from simulators.common import BaseSystem


class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a dummy module to use as a system
        cls.mymodule = ModuleType('simulators.mymodule')
        cls.mymodule.System = System
        sys.modules['simulators.mymodule'] = cls.mymodule
        cls.address = ('', 10000)
        cls.server = Server(cls.address, 'mymodule')
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_proper_request(self):
        response = get_response(self.address, msg='#command:a,b,c!')
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(self.address, '#wrong_command:foo!')
        self.assertRegexpMatches(response, 'you sent a wrong command')

    def _test_value_error(self):
        """The message of ValueError in the logfile"""
        # TODO

    def _test_unexpected_error(self):
        """The unexpected error in the logfile"""
        # TODO

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.address,
            msg='$custom_command:a,b,c!'
        )
        self.assertRegexpMatches(response, 'ok_abc')

    def test_custom_command_withoud_parameters(self):
        response = get_response(self.address, msg='$custom_command!')
        self.assertRegexpMatches(response, 'no_params')

    def test_create_server_from_module(self):
        """Server should be also take a module not just a name."""
        server = Server(('', 10001), self.mymodule)
        server.start()
        server.stop()


class TestSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a dummy module to use as a system
        cls.mymodule = ModuleType('simulators.mymodule')
        cls.mymodule.System = System
        sys.modules['simulators.mymodule'] = cls.mymodule
        cls.simulator = Simulator(cls.mymodule)

    def test_start_and_stop(self):
        address = ('127.0.0.1', 10002)
        self.mymodule.servers = [(address, ())]
        self.simulator.start(daemon=True)
        response = get_response(address, msg='#command:a,b,c!')
        self.assertEqual(response, 'aabbcc')
        self.simulator.stop()
        wait_until_connection_closed(address)


def wait_until_connection_closed(address, timeout=2):
    t0 = datetime.datetime.now()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while sock.connect_ex(address):  # Connection succeeded
        if (datetime.datetime.now() - t0).seconds < timeout:
            time.sleep(0.01)
        else:
            break


def get_response(server_address, msg, timeout=2.0, response=True):
    with socket_context(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect(server_address)
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
                self.msg = b''
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


if __name__ == '__main__':
    unittest.main()
