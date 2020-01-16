import sys
import os
import time
import socket
import datetime
import unittest

from types import ModuleType
from contextlib import contextmanager
from threading import Thread
from multiprocessing import Value, Array
from ctypes import c_bool, c_char
from Queue import Empty
from SocketServer import ThreadingTCPServer, ThreadingUDPServer

from simulators.server import Server, Simulator
from simulators.common import ListeningSystem, SendingSystem


class TestListeningServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = ('127.0.0.1', 10000)
        cls.server = Server(
            ListeningTestSystem,
            ThreadingTCPServer,
            args=(),
            l_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def tearDown(self):
        time.sleep(0.1)

    def test_proper_request(self):
        response = get_response(self.address, msg='#command:a,b,c%')
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(self.address, msg='#wrong_command:foo%')
        self.assertRegexpMatches(response, 'you sent a wrong command')

    def test_value_error(self):
        """The message of ValueError in the logfile"""
        get_response(self.address, msg='#valueerror:%', response=False)
        self.assertTrue('unexpected value' in get_logs())

    def test_unexpected_error(self):
        get_response(self.address, msg='#unexpected:%', response=False)
        self.assertTrue('unexpected exception' in get_logs())

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.address,
            msg='$custom_command:a,b,c%'
        )
        self.assertRegexpMatches(response, 'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(self.address, msg='$custom_command%')
        self.assertRegexpMatches(response, 'no_params')


class TestListeningUDPServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = ('127.0.0.1', 10000)
        cls.server = Server(
            ListeningTestSystem,
            ThreadingUDPServer,
            args=(),
            l_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def tearDown(self):
        time.sleep(0.1)

    def test_proper_request(self):
        response = get_response(self.address, msg='#command:a,b,c%', udp=True)
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(
            self.address, msg='#wrong_command:foo%', udp=True
        )
        self.assertRegexpMatches(response, 'you sent a wrong command')

    def test_value_error(self):
        """The message of ValueError in the logfile"""
        get_response(
            self.address, msg='#valueerror:%', response=False, udp=True
        )
        self.assertTrue('unexpected value' in get_logs())

    def test_unexpected_error(self):
        get_response(
            self.address, msg='#unexpected:%', response=False, udp=True
        )
        self.assertTrue('unexpected exception' in get_logs())

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.address, msg='$custom_command:a,b,c%', udp=True
        )
        self.assertRegexpMatches(response, 'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(self.address, msg='$custom_command%', udp=True)
        self.assertRegexpMatches(response, 'no_params')


class TestSendingServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = ('127.0.0.1', 10001)
        cls.server = Server(
            SendingTestSystem,
            ThreadingTCPServer,
            args=(),
            s_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def tearDown(self):
        time.sleep(0.1)

    def test_get_message(self):
        response = get_response(self.address)
        self.assertEqual(response, 'message')

    def test_unknown_command(self):
        get_response(self.address, msg='$unknown%', response=False)
        self.assertTrue('command unknown not supported' in get_logs())

    def test_raise_exception(self):
        get_response(self.address, msg='$raise_exception%', response=False)
        self.assertTrue(
            'unexpected exception raised by sendingtestsystem' in get_logs()
        )


class TestSendingUDPServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = ('127.0.0.1', 10001)
        cls.server = Server(
            SendingTestSystem,
            ThreadingUDPServer,
            args=(),
            s_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def tearDown(self):
        time.sleep(0.1)

    def test_get_message(self):
        response = get_response(self.address, udp=True)
        self.assertEqual(response, 'message')

    def test_unknown_command(self):
        get_response(self.address, msg='$unknown%', response=False, udp=True)
        self.assertTrue('command unknown not supported' in get_logs())

    def test_raise_exception(self):
        get_response(
            self.address, msg='$raise_exception%', response=False, udp=True
        )
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
            ThreadingTCPServer,
            args=(),
            l_address=cls.l_address,
            s_address=cls.s_address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def tearDown(self):
        time.sleep(0.1)

    def test_proper_request(self):
        response = get_response(self.l_address, msg='#command:a,b,c%')
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(self.l_address, msg='#wrong_command:foo%')
        self.assertRegexpMatches(response, 'you sent a wrong command')

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.l_address,
            msg='$custom_command:a,b,c%'
        )
        self.assertRegexpMatches(response, 'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(self.l_address, msg='$custom_command%')
        self.assertRegexpMatches(response, 'no_params')

    def test_get_message(self):
        response = get_response(self.s_address)
        self.assertEqual(response, 'message')

    def test_last_cmd(self):
        message = '#test:1,2,3%'
        l_response = get_response(self.l_address, msg=message)
        self.assertEqual(l_response, '112233')
        s_response = get_response(self.s_address)
        self.assertEqual(s_response, message[1:-1])


class TestDuplexUDPServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.l_address = ('127.0.0.1', 10002)
        cls.s_address = ('127.0.0.1', 10003)
        cls.server = Server(
            DuplexTestSystem,
            ThreadingUDPServer,
            args=(),
            l_address=cls.l_address,
            s_address=cls.s_address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def tearDown(self):
        time.sleep(0.1)

    def test_proper_request(self):
        response = get_response(
            self.l_address, msg='#command:a,b,c%', udp=True
        )
        self.assertEqual(response, 'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(
            self.l_address, msg='#wrong_command:foo%', udp=True
        )
        self.assertRegexpMatches(response, 'you sent a wrong command')

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.l_address,
            msg='$custom_command:a,b,c%',
            udp=True
        )
        self.assertRegexpMatches(response, 'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(
            self.l_address, msg='$custom_command%', udp=True
        )
        self.assertRegexpMatches(response, 'no_params')

    def test_get_message(self):
        response = get_response(self.s_address, udp=True)
        self.assertEqual(response, 'message')

    def test_last_cmd(self):
        message = '#test:1,2,3%'
        l_response = get_response(self.l_address, msg=message, udp=True)
        self.assertEqual(l_response, '112233')
        s_response = get_response(self.s_address, udp=True)
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
        self.mymodule.servers = [(address, (), ThreadingTCPServer, ())]
        self.mymodule.System = ListeningTestSystem

        simulator = Simulator(self.mymodule)
        simulator.start(daemon=True)
        simulator.stop()

    def test_create_simulator_from_name(self):
        address = ('127.0.0.1', 10005)
        self.mymodule.servers = [(address, (), ThreadingTCPServer, ())]
        self.mymodule.System = ListeningTestSystem

        simulator = Simulator('mymodule')
        simulator.start(daemon=True)
        simulator.stop()

    def test_start_and_stop_listening(self):
        address = ('127.0.0.1', 10006)
        self.mymodule.servers = [(address, (), ThreadingTCPServer, ())]
        self.mymodule.System = ListeningTestSystem

        self.simulator.start(daemon=True)

        response = get_response(address, msg='#command:a,b,c%')
        self.assertEqual(response, 'aabbcc')

        self.simulator.stop()

    def test_start_and_stop_sending(self):
        address = ('127.0.0.1', 10007)
        self.mymodule.servers = [((), address, ThreadingTCPServer, ())]
        self.mymodule.System = SendingTestSystem

        self.simulator.start(daemon=True)

        response = get_response(address)
        self.assertEqual(response, 'message')

        self.simulator.stop()

    def test_start_and_stop_duplex(self):
        l_addr = ('127.0.0.1', 10008)
        s_addr = ('127.0.0.1', 10009)
        self.mymodule.servers = [(l_addr, s_addr, ThreadingTCPServer, ())]
        self.mymodule.System = DuplexTestSystem

        self.simulator.start(daemon=True)

        l_response = get_response(l_addr, msg='#command:a,b,c%')
        self.assertEqual(l_response, 'aabbcc')
        s_response = get_response(s_addr)
        self.assertEqual(s_response, 'command:a,b,c')

        self.simulator.stop()

    def test_stop_without_start(self):
        address = ('127.0.0.1', 10007)
        self.mymodule.servers = [((), address, ())]
        self.mymodule.System = SendingTestSystem
        self.simulator.stop()

    def test_non_daemon_simulator(self):
        l_addr = ('127.0.0.1', 10010)
        s_addr = ('127.0.0.1', 10011)
        self.mymodule.servers = [(l_addr, s_addr, ThreadingTCPServer, ())]
        self.mymodule.System = DuplexTestSystem

        simulator = Simulator(self.mymodule)

        t = Thread(target=simulator.start)
        t.start()
        time.sleep(0.1)
        response = get_response(l_addr, msg='$system_stop%')
        self.assertEqual(response, '$server_shutdown%')
        response = get_response(s_addr, msg='$system_stop%')
        self.assertEqual(response, '$server_shutdown%')
        t.join()


class TestServerVarious(unittest.TestCase):

    def test_server_shutdown(self):
        address = ('127.0.0.1', 10012)
        server = Server(
            ListeningTestSystem,
            ThreadingTCPServer,
            args=(),
            l_address=address,
        )
        server.start()

        def shutdown(self):
            time.sleep(0.01)
            response = get_response(address, msg='$system_stop%')
            self.assertEqual(response, '$server_shutdown%')

        t = Thread(target=shutdown, args=(self,))
        t.start()
        t.join()

    def test_server_no_addresses(self):
        with self.assertRaises(ValueError):
            Server(
                ListeningTestSystem,
                ThreadingTCPServer,
                args=()
            )

    def test_server_wrong_socket_type(self):
        address = ('127.0.0.1', 10012)
        with self.assertRaises(ValueError):
            Server(
                ListeningTestSystem,
                object,
                args=(),
                l_address=address
            )


def get_response(
        server_address, msg=None, timeout=2.0, response=True, udp=False):
    retval = b''
    if udp:
        socket_type = socket.SOCK_DGRAM
        if not msg:
            msg = ''
    else:
        socket_type = socket.SOCK_STREAM
    with socket_context(socket.AF_INET, socket_type) as sock:
        sock.settimeout(timeout)
        sock.connect(server_address)
        if isinstance(msg, str):
            sock.sendto(msg, server_address)
        if response:
            retval = sock.recv(1024)
    return retval


def get_logs():
    time.sleep(0.03)
    now = datetime.datetime.now()
    logs = []
    filename = os.path.join(os.getenv('ACSDATA', ''), 'sim-server.log')
    for line in open(filename, 'r').readlines():
        try:
            line = line.strip()
            log_date = datetime.datetime.strptime(
                ' '.join(line.split(' ')[0:2]) + '000',
                '%Y-%m-%d %H:%M:%S,%f'
            )
            log_date += datetime.timedelta(microseconds=25000)
            if (now - log_date).total_seconds() < 0.01:
                logs.append(' '.join(line.split(' ')[2:]))
        except ValueError:  # pragma: no cover
            continue
    return logs


class ListeningTestSystem(ListeningSystem):

    header = b'#'
    tail = b'%'

    def __init__(self):
        self.msg = b''
        try:
            getattr(self, 'last_cmd')
        except AttributeError:
            self.last_cmd = Array(c_char, b'\x00' * 50)

    def parse(self, byte):
        # Example of msg: #command_name:par1,par2,par3!
        if byte == self.header:
            self.msg = byte
            return True
        elif self.msg.startswith(self.header):
            self.msg += byte
            if byte == self.tail:
                self.last_cmd.value = self.msg[1:-1]
                name, params_str = str(self.last_cmd.value).split(':')
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

    def __init__(self):
        try:
            getattr(self, 'last_cmd')
        except AttributeError:
            self.last_cmd = Array(c_char, b'\x00' * 50)
        self.last_cmd.value = 'message'
        self.t = None

    def subscribe(self, q):
        self.stop = Value(c_bool, False)
        t = Thread(
            target=self.put,
            args=(q, self.stop, self.sampling_time, self.last_cmd)
        )
        t.daemon = True
        t.start()

    @staticmethod
    def put(q, stop, sampling_time, last_cmd):
        while True:
            if stop.value:
                break
            while True:
                try:
                    q.get_nowait()
                except Empty:
                    break
            q.put(str(last_cmd.value))
            time.sleep(sampling_time)

    def unsubscribe(self, _):
        self.stop.value = True

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
