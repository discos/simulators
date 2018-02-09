import sys
import time
import socket
import datetime
import unittest

from types import ModuleType
from contextlib import contextmanager

from simulators.server import Server, Simulator
from simulators.common import BaseSystem, ListeningSystem, SendingSystem


class TestListeningServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = ('127.0.0.1', 10000)
        cls.system = ListeningTestSystem()
        cls.server = Server(cls.system, l_address=cls.address)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_proper_request(self):
        response = get_response(self.address, msg='#command:a,b,c!')
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(self.address, msg='#wrong_command:foo!')
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

    def test_custom_command_without_parameters(self):
        response = get_response(self.address, msg='$custom_command!')
        self.assertRegexpMatches(response, 'no_params')


class TestSendingServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = ('127.0.0.1', 10001)
        cls.system = SendingTestSystem()
        cls.server = Server(cls.system, s_address=cls.address)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_get_message(self):
        response = get_response(self.address)
        self.assertEqual(response, 'message')


class TestDuplexServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.l_address = ('127.0.0.1', 10002)
        cls.s_address = ('127.0.0.1', 10003)
        cls.system = DuplexTestSystem()
        cls.server = Server(cls.system, cls.l_address, cls.s_address)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_proper_request(self):
        response = get_response(self.l_address, msg='#command:a,b,c!')
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(self.l_address, msg='#wrong_command:foo!')
        self.assertRegexpMatches(response, 'you sent a wrong command')

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.l_address,
            msg='$custom_command:a,b,c!'
        )
        self.assertRegexpMatches(response, 'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(self.l_address, msg='$custom_command!')
        self.assertRegexpMatches(response, 'no_params')

    def test_get_message(self):
        response = get_response(self.s_address)
        self.assertEqual(response, 'message')

    def test_last_cmd(self):
        message = '#test:1,2,3!'
        l_response = get_response(self.l_address, msg=message)
        self.assertEqual(l_response, '112233')
        s_response = get_response(self.s_address)
        self.assertEqual(s_response, message[1:-1])


class TestSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mymodulename = 'simulators.mymodule'
        cls.mymodule = ModuleType(cls.mymodulename)
        sys.modules[cls.mymodulename] = cls.mymodule
        cls.simulator = Simulator(cls.mymodule)

    def test_create_simulator_from_name(self):
        address = ('127.0.0.1', 10004)
        self.mymodule.servers = [(address, (), ())]
        self.mymodule.System = BaseSystem

        simulator = Simulator('mymodule')
        simulator.start(daemon=True)
        simulator.stop()

        wait_until_connection_closed(address)

    def test_start_and_stop_listening(self):
        address = ('127.0.0.1', 10005)
        self.mymodule.servers = [(address, (), ())]
        self.mymodule.System = ListeningTestSystem

        self.simulator.start(daemon=True)

        response = get_response(address, msg='#command:a,b,c!')
        self.assertEqual(response, 'aabbcc')

        self.simulator.stop()
        wait_until_connection_closed(address)

    def test_start_and_stop_sending(self):
        address = ('127.0.0.1', 10006)
        self.mymodule.servers = [((), address, ())]
        self.mymodule.System = SendingTestSystem

        self.simulator.start(daemon=True)

        response = get_response(address)
        self.assertEqual(response, 'message')

        self.simulator.stop()
        wait_until_connection_closed(address)

    def test_start_and_stop_duplex(self):
        l_address = ('127.0.0.1', 10007)
        s_address = ('127.0.0.1', 10008)
        self.mymodule.servers = [(l_address, s_address, ())]
        self.mymodule.System = DuplexTestSystem

        self.simulator.start(daemon=True)

        l_response = get_response(l_address, msg='#command:a,b,c!')
        self.assertEqual(l_response, 'aabbcc')
        s_response = get_response(s_address)
        self.assertEqual(s_response, 'command:a,b,c')

        self.simulator.stop()
        wait_until_connection_closed(l_address)
        wait_until_connection_closed(s_address)


def wait_until_connection_closed(address, timeout=2):
    t0 = datetime.datetime.now()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while sock.connect_ex(address):  # Connection succeeded
        if (datetime.datetime.now() - t0).seconds < timeout:
            time.sleep(0.01)
        else:
            break


def get_response(server_address, msg=None, timeout=2.0, response=True):
    with socket_context(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect(server_address)
        if msg:
            sock.sendall(msg)
        return sock.recv(1024) if response else b''


class ListeningTestSystem(ListeningSystem):

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
                self.last_cmd = self.msg[1:-1]
                name, params_str = self.last_cmd.split(':')
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


class SendingTestSystem(SendingSystem):

    sampling_time = 1

    def __init__(self):
        self.last_cmd = 'message'

    def get_message(self):
        return self.last_cmd


class DuplexTestSystem(ListeningTestSystem, SendingTestSystem):

    def __init__(self):
        ListeningTestSystem.__init__(self)
        SendingTestSystem.__init__(self)


@contextmanager
def socket_context(*args, **kw):
    sock = socket.socket(*args, **kw)
    try:
        yield sock
    finally:
        sock.close()


if __name__ == '__main__':
    unittest.main()
