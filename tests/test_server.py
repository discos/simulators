import sys
import time
import socket
import datetime
import unittest

from types import ModuleType
from contextlib import contextmanager
from threading import Thread

from simulators.server import Server, Simulator
from simulators.common import BaseSystem, ListeningSystem, SendingSystem


class TestListeningServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = ('127.0.0.1', 10000)
        cls.server = Server(
            ListeningTestSystem,
            args=(),
            l_address=cls.address
        )
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

    def test_value_error(self):
        """The message of ValueError in the logfile"""
        get_response(self.address, msg='#valueerror:!', response=False)
        self.assertTrue('unexpected value' in get_logs())

    def test_unexpected_error(self):
        get_response(self.address, msg='#unexpected:!', response=False)
        self.assertTrue('unexpected exception' in get_logs())

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
        cls.server = Server(
            SendingTestSystem,
            args=(),
            s_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_get_message(self):
        response = get_response(self.address)
        self.assertEqual(response, 'message')

    def test_unknown_command(self):
        get_response(self.address, msg='$unknown!', response=False)
        self.assertTrue('command unknown not supported' in get_logs())

    def test_raise_exception(self):
        get_response(self.address, msg='$raise_exception!', response=False)
        self.assertTrue(
            'unexpected exception raised by sendingtestsystem' in get_logs()
        )


class TestDuplexServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.l_address = ('127.0.0.1', 10002)
        cls.s_address = ('127.0.0.1', 10003)
        cls.server = Server(
            DuplexTestSystem,
            args=(),
            l_address=cls.l_address,
            s_address=cls.s_address
        )
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

    def test_create_simulator_from_module(self):
        address = ('127.0.0.1', 10004)
        self.mymodule.servers = [(address, (), ())]
        self.mymodule.System = ListeningTestSystem

        simulator = Simulator(self.mymodule)
        simulator.start(daemon=True)
        simulator.stop()

    def test_create_simulator_from_name(self):
        address = ('127.0.0.1', 10005)
        self.mymodule.servers = [(address, (), ())]
        self.mymodule.System = BaseSystem

        simulator = Simulator('mymodule')
        simulator.start(daemon=True)
        simulator.stop()

    def test_start_and_stop_listening(self):
        address = ('127.0.0.1', 10006)
        self.mymodule.servers = [(address, (), ())]
        self.mymodule.System = ListeningTestSystem

        self.simulator.start(daemon=True)

        response = get_response(address, msg='#command:a,b,c!')
        self.assertEqual(response, 'aabbcc')

        self.simulator.stop()

    def test_start_and_stop_sending(self):
        address = ('127.0.0.1', 10007)
        self.mymodule.servers = [((), address, ())]
        self.mymodule.System = SendingTestSystem

        self.simulator.start(daemon=True)

        response = get_response(address)
        self.assertEqual(response, 'message')

        self.simulator.stop()

    def test_start_and_stop_duplex(self):
        l_address = ('127.0.0.1', 10008)
        s_address = ('127.0.0.1', 10009)
        self.mymodule.servers = [(l_address, s_address, ())]
        self.mymodule.System = DuplexTestSystem

        self.simulator.start(daemon=True)

        l_response = get_response(l_address, msg='#command:a,b,c!')
        self.assertEqual(l_response, 'aabbcc')
        s_response = get_response(s_address)
        self.assertEqual(s_response, 'command:a,b,c')

        self.simulator.stop()

    def test_stop_without_start(self):
        address = ('127.0.0.1', 10007)
        self.mymodule.servers = [((), address, ())]
        self.mymodule.System = SendingTestSystem
        self.simulator.stop()

    def test_non_daemon_simulator(self):
        l_address = ('127.0.0.1', 10010)
        s_address = ('127.0.0.1', 10011)
        self.mymodule.servers = [(l_address, s_address, ())]
        self.mymodule.System = DuplexTestSystem

        simulator = Simulator(self.mymodule)

        t = Thread(target=simulator.start)
        t.start()
        time.sleep(0.1)
        response = get_response(l_address, msg='$system_stop!')
        self.assertEqual(response, '$server_shutdown!')
        response = get_response(s_address, msg='$system_stop!')
        self.assertEqual(response, '$server_shutdown!')
        t.join()


class TestServerVarious(unittest.TestCase):

    def test_server_shutdown(self):
        address = ('127.0.0.1', 10012)
        server = Server(
            ListeningTestSystem,
            args=(),
            l_address=address,
        )
        server.start()

        def shutdown(self):
            time.sleep(0.01)
            response = get_response(address, msg='$system_stop!')
            self.assertEqual(response, '$server_shutdown!')

        t = Thread(target=shutdown, args=(self,))
        t.start()
        t.join()
        while server.is_alive:
            time.sleep(0.01)

    def test_server_no_addresses(self):
        with self.assertRaises(ValueError):
            Server(
                ListeningTestSystem,
                args=()
            )


def get_response(server_address, msg=None, timeout=2.0, response=True):
    with socket_context(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect(server_address)
        if msg:
            sock.sendall(msg)
        return sock.recv(1024) if response else b''


def get_logs():
    time.sleep(0.03)
    now = datetime.datetime.now()
    logs = []
    for line in open('sim-server.log', 'r').readlines():
        line = line.strip()
        log_date = datetime.datetime.strptime(
            ' '.join(line.split(' ')[0:2]) + '000',
            '%Y-%m-%d %H:%M:%S,%f'
        )
        log_date += datetime.timedelta(microseconds=25000)
        if (now - log_date).total_seconds() < 0.01:
            logs.append(' '.join(line.split(' ')[2:]))
    return logs


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
                elif name == 'valueerror':
                    raise ValueError('unexpected value')
                elif name == 'unexpected':
                    raise AttributeError('unexpected exception')
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

    sampling_time = 0.01

    def __init__(self):
        self.last_cmd = 'message'

    def get_message(self):
        return self.last_cmd

    @staticmethod
    def raise_exception():
        raise Exception('raised by sendingtestsystem')


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
