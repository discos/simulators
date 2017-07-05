import sys
import socket
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

    def test_response(self):
        response = self.get_response(msg='#command:a,b,c!')
        self.assertEqual(response, '#aabbcc!')

    def test_wrong_response(self):
        response = self.get_response(msg='#pippo:a,b,c!')
        self.assertRegexpMatches(response, '#command pippo not supported!')

    def get_response(self, msg):
        with socket_context(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            sock.connect(self.server.server_address)
            sock.sendall(msg)
            return sock.recv(1024)


class System(BaseSystem):

    msg_header = b'#'
    msg_tail = b'!'

    def parse(self, msg):
        # Example of msg: #command_name:par1,par2,par3!
        plain_msg = msg.lstrip('#').rstrip('!')
        name, params_str = plain_msg.split(':')
        params = params_str.split(',')
        return name, params

    def command(self, *args):
        # For instance: args == ('a', 'b') -> 'aabb'
        response = b''
        for arg in args:
            response += arg*2
        return self.msg_header + response + self.msg_tail


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


if __name__ == '__main__':
    unittest.main()
