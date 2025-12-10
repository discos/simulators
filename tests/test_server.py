import sys
import os
import time
import socket
import unittest

from types import ModuleType
from threading import Thread, Event
from queue import Empty
from io import StringIO
from socketserver import ThreadingTCPServer, ThreadingUDPServer

from simulators.server import Server, Simulator
from simulators.common import ListeningSystem, SendingSystem


STARTING_PORT = 10000


def address_generator_function():
    port = STARTING_PORT
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ('127.0.0.1', port)
        try:
            s.bind(address)
            s.close()
            time.sleep(0.01)
            yield address
        except OSError:
            pass
        port += 1


address_generator = address_generator_function()


class TestListeningServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = next(address_generator)
        cls.server = Server(
            ListeningTestSystem,
            ThreadingTCPServer,
            kwargs={},
            l_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_wrong_greet_msg(self):
        with self.assertRaises(ValueError):
            get_response(
                self.address,
                greet_msg=b'Wrong greet message!',
            )

    def test_proper_request(self):
        response = get_response(
            self.address,
            greet_msg=b'This is a greeting message!',
            msg=b'#command:a,b,c%%%%%'
        )
        self.assertEqual(response, b'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(
            self.address,
            greet_msg=b'This is a greeting message!',
            msg=b'#wrong_command:foo%%%%%'
        )
        self.assertRegex(response, b'you sent a wrong command')

    def test_value_error(self):
        """The message of ValueError in the logfile"""
        get_response(
            self.address,
            greet_msg=b'This is a greeting message!',
            msg=b'#valueerror:%%%%%',
            response=False
        )
        self.assertIn('unexpected value', get_logs())

    def test_unexpected_error(self):
        get_response(
            self.address,
            greet_msg=b'This is a greeting message!',
            msg=b'#unexpected:%%%%%',
            response=False
        )
        self.assertIn('unexpected exception', get_logs())

    def test_unexpected_response(self):
        get_response(
            self.address,
            greet_msg=b'This is a greeting message!',
            msg=b'#unexpected_response:%%%%%',
            response=False
        )
        self.assertIn('unexpected response: 0.0', get_logs())

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.address,
            greet_msg=b'This is a greeting message!',
            msg=b'$custom_command:a,b,c%%%%%'
        )
        self.assertRegex(response, b'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(
            self.address,
            greet_msg=b'This is a greeting message!',
            msg=b'$custom_command%%%%%'
        )
        self.assertRegex(response, b'no_params')


class TestListeningUDPServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = next(address_generator)
        cls.server = Server(
            ListeningTestSystem,
            ThreadingUDPServer,
            kwargs={},
            l_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_proper_request(self):
        response = get_response(
            self.address,
            msg=b'#command:a,b,c%%%%%',
            udp=True
        )
        self.assertEqual(response, b'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(
            self.address, msg=b'#wrong_command:foo%%%%%', udp=True
        )
        self.assertRegex(response, b'you sent a wrong command')

    def test_value_error(self):
        """The message of ValueError in the logfile"""
        get_response(
            self.address, msg=b'#valueerror:%%%%%', response=False, udp=True
        )
        self.assertIn('unexpected value', get_logs())

    def test_unexpected_error(self):
        get_response(
            self.address, msg=b'#unexpected:%%%%%', response=False, udp=True
        )
        self.assertIn('unexpected exception', get_logs())

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.address, msg=b'$custom_command:a,b,c%%%%%', udp=True
        )
        self.assertRegex(response, b'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(
            self.address,
            msg=b'$custom_command%%%%%',
            udp=True
        )
        self.assertRegex(response, b'no_params')


class TestSendingServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = next(address_generator)
        cls.server = Server(
            SendingTestSystem,
            ThreadingTCPServer,
            kwargs={},
            s_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_get_message(self):
        response = get_response(self.address)
        self.assertEqual(response, b'message')

    def test_unknown_command(self):
        get_response(self.address, msg=b'$unknown%%%%%', response=False)
        self.assertIn('command unknown not supported', get_logs())

    def test_raise_exception(self):
        get_response(
            self.address,
            msg=b'$raise_exception%%%%%',
            response=False
        )
        self.assertIn(
            'unexpected exception raised by sendingtestsystem', get_logs()
        )


class TestSendingUDPServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.address = next(address_generator)
        cls.server = Server(
            SendingTestSystem,
            ThreadingUDPServer,
            kwargs={},
            s_address=cls.address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_get_message(self):
        response = get_response(self.address, udp=True)
        self.assertEqual(response, b'message')

    def test_unknown_command(self):
        get_response(
            self.address,
            msg=b'$unknown%%%%%',
            response=False,
            udp=True
        )
        self.assertIn('command unknown not supported', get_logs())

    def test_raise_exception(self):
        get_response(
            self.address,
            msg=b'$raise_exception%%%%%',
            response=False,
            udp=True
        )
        self.assertIn(
            'unexpected exception raised by sendingtestsystem', get_logs()
        )


class TestDuplexServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.l_address = next(address_generator)
        cls.s_address = next(address_generator)
        cls.server = Server(
            DuplexTestSystem,
            ThreadingTCPServer,
            kwargs={},
            l_address=cls.l_address,
            s_address=cls.s_address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_proper_request(self):
        response = get_response(
            self.l_address,
            greet_msg=b'This is a greeting message!',
            msg=b'#command:a,b,c%%%%%'
        )
        self.assertEqual(response, b'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(
            self.l_address,
            greet_msg=b'This is a greeting message!',
            msg=b'#wrong_command:foo%%%%%'
        )
        self.assertRegex(response, b'you sent a wrong command')

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.l_address,
            greet_msg=b'This is a greeting message!',
            msg=b'$custom_command:a,b,c%%%%%'
        )
        self.assertRegex(response, b'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(
            self.l_address,
            greet_msg=b'This is a greeting message!',
            msg=b'$custom_command%%%%%'
        )
        self.assertRegex(response, b'no_params')

    def test_get_message(self):
        response = get_response(self.s_address)
        self.assertEqual(response, b'message')

    def test_last_cmd(self):
        message = b'#test:1,2,3%%%%%'
        l_response = get_response(
            self.l_address,
            greet_msg=b'This is a greeting message!',
            msg=message
        )
        self.assertEqual(l_response, b'112233')
        s_response = get_response(self.s_address)
        self.assertEqual(s_response, message[1:].strip(b'%'))


class TestDuplexUDPServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.l_address = next(address_generator)
        cls.s_address = next(address_generator)
        cls.server = Server(
            DuplexTestSystem,
            ThreadingUDPServer,
            kwargs={},
            l_address=cls.l_address,
            s_address=cls.s_address
        )
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_proper_request(self):
        response = get_response(
            self.l_address, msg=b'#command:a,b,c%%%%%', udp=True
        )
        self.assertEqual(response, b'aabbcc')

    def test_wrong_request(self):
        """Wrong request but expected by the protocol"""
        response = get_response(
            self.l_address, msg=b'#wrong_command:foo%%%%%', udp=True
        )
        self.assertRegex(response, b'you sent a wrong command')

    def test_custom_command_with_parameters(self):
        response = get_response(
            self.l_address,
            msg=b'$custom_command:a,b,c%%%%%',
            udp=True
        )
        self.assertRegex(response, b'ok_abc')

    def test_custom_command_without_parameters(self):
        response = get_response(
            self.l_address, msg=b'$custom_command%%%%%', udp=True
        )
        self.assertRegex(response, b'no_params')

    def test_get_message(self):
        response = get_response(self.s_address, udp=True)
        self.assertEqual(response, b'message')

    def test_last_cmd(self):
        message = b'#test:1,2,3%%%%%'
        l_response = get_response(self.l_address, msg=message, udp=True)
        self.assertEqual(l_response, b'112233')
        s_response = get_response(self.s_address, udp=True)
        self.assertEqual(s_response, message[1:].strip(b'%'))


class TestServerVarious(unittest.TestCase):

    def test_server_shutdown(self):
        address = next(address_generator)
        server = Server(
            ListeningTestSystem,
            ThreadingTCPServer,
            kwargs={},
            l_address=address,
        )
        server.start()
        time.sleep(0.1)
        response = get_response(
            address,
            greet_msg=b'This is a greeting message!',
            msg=b'$system_stop%%%%%'
        )
        self.assertEqual(response, b'$server_shutdown%%%%%')

    def test_server_no_addresses(self):
        with self.assertRaises(ValueError):
            Server(
                ListeningTestSystem,
                ThreadingTCPServer,
                kwargs={}
            )

    def test_server_wrong_socket_type(self):
        address = next(address_generator)
        with self.assertRaises(ValueError):
            Server(
                ListeningTestSystem,
                object,
                kwargs={},
                l_address=address
            )

    def test_server_start_twice(self):
        address = next(address_generator)
        with self.assertRaises(OSError):
            s1 = Server(
                ListeningTestSystem,
                ThreadingTCPServer,
                kwargs={},
                l_address=address
            )
            s1.start()
            s2 = Server(
                ListeningTestSystem,
                ThreadingTCPServer,
                kwargs={},
                l_address=address
            )
            s2.start()


class TestSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mymodulename = 'simulators.mymodule'
        cls.mymodule = ModuleType(cls.mymodulename)
        sys.modules[cls.mymodulename] = cls.mymodule

    def test_create_simulator_from_module(self):
        address = next(address_generator)
        self.mymodule.servers = [(address, (), ThreadingTCPServer, {})]
        self.mymodule.System = ListeningTestSystem

        simulator = Simulator(self.mymodule)
        simulator.start(daemon=True)
        simulator.stop()

    def test_system_type(self):
        self.mymodule.servers = [
            (
                next(address_generator),
                (),
                ThreadingTCPServer,
                {'system_type': 'foo'}
            ),
            (
                next(address_generator),
                (),
                ThreadingTCPServer,
                {'system_type': 'moo'}
            ),
        ]
        self.mymodule.System = ListeningTestSystem
        try:
            stdout = StringIO()
            sys.stdout = stdout
            simulator = Simulator(self.mymodule, system_type='moo')
            context = "fork"
            if sys.version_info[1] >= 14:
                context = "forkserver"
            simulator.start(daemon=True, context=context)
            simulator.stop()
            output = stdout.getvalue()
        finally:
            sys.stdout = sys.__stdout__
            stdout.close()

        self.assertIn("moo' up and running", output)

    def test_create_simulator_from_name(self):
        address = next(address_generator)
        self.mymodule.servers = [(address, (), ThreadingTCPServer, {})]
        self.mymodule.System = ListeningTestSystem

        simulator = Simulator('mymodule')
        simulator.start(daemon=True)
        simulator.stop()

    def test_start_and_stop_listening(self):
        address = next(address_generator)
        self.mymodule.servers = [(address, (), ThreadingTCPServer, {})]
        self.mymodule.System = ListeningTestSystem

        simulator = Simulator(self.mymodule)
        simulator.start(daemon=True)

        response = get_response(
            address,
            greet_msg=b'This is a greeting message!',
            msg=b'#command:a,b,c%%%%%'
        )
        self.assertEqual(response, b'aabbcc')

        simulator.stop()

    def test_start_and_stop_sending(self):
        address = next(address_generator)
        self.mymodule.servers = [((), address, ThreadingTCPServer, {})]
        self.mymodule.System = SendingTestSystem

        simulator = Simulator(self.mymodule)
        simulator.start(daemon=True)

        response = get_response(address)
        self.assertEqual(response, b'message')

        simulator.stop()

    def test_start_and_stop_duplex(self):
        l_addr = next(address_generator)
        s_addr = next(address_generator)
        self.mymodule.servers = [(l_addr, s_addr, ThreadingTCPServer, {})]
        self.mymodule.System = DuplexTestSystem

        simulator = Simulator(self.mymodule)
        simulator.start(daemon=True)

        l_response = get_response(
            l_addr,
            greet_msg=b'This is a greeting message!',
            msg=b'#command:a,b,c%%%%%'
        )
        self.assertEqual(l_response, b'aabbcc')
        s_response = get_response(s_addr)
        self.assertEqual(s_response, b'command:a,b,c')

        simulator.stop()

    def test_stop_without_start(self):
        address = next(address_generator)
        self.mymodule.servers = [((), address, ThreadingUDPServer, {})]
        self.mymodule.System = SendingTestSystem
        simulator = Simulator(self.mymodule)
        simulator.stop()

    def test_non_daemon_simulator(self):
        l_addr = next(address_generator)
        s_addr = next(address_generator)
        self.mymodule.servers = [(l_addr, s_addr, ThreadingTCPServer, {})]
        self.mymodule.System = DuplexTestSystem

        simulator = Simulator(self.mymodule)
        e = Event()

        def shutdown(self, event):
            while not event.is_set():
                continue
            response = get_response(
                l_addr,
                greet_msg=b'This is a greeting message!',
                msg=b'$system_stop%%%%%'
            )
            self.assertEqual(response, b'$server_shutdown%%%%%')
            response = get_response(s_addr, msg=b'$system_stop%%%%%')
            self.assertEqual(response, b'$server_shutdown%%%%%')

        t = Thread(target=shutdown, args=(self, e))
        t.start()
        simulator.start(has_started=e)
        t.join()

    def test_start_simulator_twice(self):
        try:
            address = next(address_generator)
            self.mymodule.servers = [(address, (), ThreadingTCPServer, {})]
            self.mymodule.System = ListeningTestSystem

            s1 = Simulator(self.mymodule)
            s1.start(daemon=True)

            stdout = StringIO()
            sys.stdout = stdout
            s2 = Simulator(self.mymodule)
            s2.start(daemon=True)

            s1.stop()
            output = stdout.getvalue()
        finally:
            sys.stdout = sys.__stdout__
            stdout.close()

        self.assertIn("already running", output)


def get_response(
        server_address,
        greet_msg=None,
        msg=None,
        timeout=2.0,
        response=True,
        udp=False):
    retval = b''
    if udp:
        socket_type = socket.SOCK_DGRAM
        if not msg:
            msg = b''
    else:
        socket_type = socket.SOCK_STREAM
    with socket.socket(socket.AF_INET, socket_type) as sock:
        sock.settimeout(timeout)
        sock.connect(server_address)
        if greet_msg:
            greeting = sock.recv(len(greet_msg))
            if greeting != greet_msg:
                raise ValueError
        if isinstance(msg, bytes):
            sock.sendall(msg)
        if response:
            try:
                retval = sock.recv(1024)
            except socket.timeout:
                pass
    return retval


def get_logs():
    time.sleep(0.01)
    filename = os.path.join(os.getenv('ACSDATA', ''), 'sim-server.log')
    logs = []
    with open(filename, mode='rb') as f:
        buffer_string = ''
        f.seek(0, os.SEEK_END)
        while len(logs) < 3:
            try:
                f.seek(-2, os.SEEK_CUR)
                buffer_string += f.read(1).decode('utf-8')
            except OSError:
                break
            if buffer_string.endswith('\n'):
                log = buffer_string[:-1][::-1]
                pid = str(os.getpid())
                index = log.find(pid)
                if index != -1:
                    logs.append(log[index + len(pid) + 1:])
                    buffer_string = ''
    return logs


class ListeningTestSystem(ListeningSystem):

    header = '#'
    tail = '%%%%%'

    def __init__(self, **kwargs):  # pylint: disable=unused-argument
        self.msg = ''
        try:
            getattr(self, 'last_cmd')
        except AttributeError:
            self.last_cmd = b''

    def parse(self, byte):
        # Example of msg: #command_name:par1,par2,par3!
        if byte == self.header:
            self.msg = byte
            return True
        elif self.msg.startswith(self.header):
            self.msg += byte
            if self.msg.endswith(self.tail):
                self.msg = self.msg.lstrip(self.header)
                self.msg = self.msg.rstrip(self.tail)
                self.last_cmd = self.msg.encode('utf-8')
                name, params_str = self.msg.split(':')
                self.msg = ''
                if name == 'wrong_command':
                    return 'you sent a wrong command'
                elif name == 'valueerror':
                    raise ValueError('unexpected value')
                elif name == 'unexpected':
                    raise AttributeError('unexpected exception')
                elif name == 'unexpected_response':
                    return 0.0  # Nor boolean or str
                params = params_str.split(',')
                response = ''
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
        return f'{msg} (id: {id(self)})'

    @staticmethod
    def system_greet():
        return 'This is a greeting message!'


class SendingTestSystem(SendingSystem):

    def __init__(self, **kwargs):  # pylint: disable=unused-argument
        try:
            getattr(self, 'last_cmd')
        except AttributeError:
            self.last_cmd = b''
        self.last_cmd = b'message'
        self.t = None

    def subscribe(self, q):
        self.stop = Event()
        t = Thread(
            target=self.put,
            args=(q, self.stop, 0.25, self.last_cmd)
        )
        t.daemon = True
        t.start()

    @staticmethod
    def put(q, stop, sampling_time, last_cmd):
        while True:
            if stop.is_set():
                break
            while True:
                try:
                    q.get_nowait()
                except Empty:
                    break
            q.put(last_cmd)
            time.sleep(sampling_time)

    def unsubscribe(self, _):
        self.stop.set()

    @staticmethod
    def raise_exception():
        raise Exception('raised by sendingtestsystem')


class DuplexTestSystem(ListeningTestSystem, SendingTestSystem):

    def __init__(self, **kwargs):
        ListeningTestSystem.__init__(self, **kwargs)
        SendingTestSystem.__init__(self, **kwargs)


if __name__ == '__main__':
    unittest.main()
