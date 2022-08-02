import unittest
import socket
import time
from threading import Thread
from simulators.totalpower import System, Board

LISTENING_ADDRESS = '127.0.0.1'
LISTENING_PORT = 6001


class TestTotalPower(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def tearDown(self):
        del self.system

    def test_unknown_command(self):
        msg = '%\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertFalse(self.system.parse(msg[-1]))

    def test_T(self):
        msg = 'T 0 0\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(msg[-1])
        answer = answer.split(',')
        self.assertEqual(int(answer[0]), 0)
        self.assertEqual(int(answer[1]), 0)
        try:
            for arg in answer[2:]:
                arg = int(arg)
        except ValueError:
            self.fail('Wrong answer received!')

    def test_T_wrong_params_type(self):
        msg = 'T 0.5 0.5\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_T_wrong_params_number(self):
        msg = 'T 0 0 0\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_E(self):
        msg = 'E 0 0\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(msg[-1])
        answer = answer.split(',')
        self.assertEqual(int(answer[0]), 0)
        self.assertEqual(int(answer[1]), 0)
        try:
            for arg in answer[2:]:
                arg = int(arg)
        except ValueError:
            self.fail('Wrong answer received!')

    def test_E_wrong_params_number(self):
        msg = 'E 0 0 0\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_I(self):
        msg = 'I B 0 1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_I_wrong_input(self):
        msg = 'I I 0 1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_I_wrong_attenuation(self):
        msg = 'I B 20 1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_I_wrong_filter(self):
        msg = 'I B 0 5\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_I_too_many_params(self):
        msg = 'I B 0 4 5\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_A(self):
        msg = 'A 1 B 0 4\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_A_wrong_channel(self):
        msg = 'A 20 B 0 4\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak 20\n')

    def test_A_wrong_input(self):
        msg = 'A 1 I 0 4\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak 1\n')

    def test_A_wrong_attenuation(self):
        msg = 'A 1 B 20 4\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak 1\n')

    def test_A_wrong_filter(self):
        msg = 'A 1 B 0 5\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak 1\n')

    def test_A_too_few_params(self):
        msg = 'A 1 B 0\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_status(self):
        msg = '?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            len(self.system.parse(msg[-1]).split()),
            7 + (self.system.channels * 3)
        )

    def test_N(self):
        msg = 'N 1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_N_too_few_params(self):
        msg = 'N\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_N_wrong_params(self):
        msg = 'N 2\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_M(self):
        msg = 'M 1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_M_too_few_params(self):
        msg = 'M\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_M_wrong_params(self):
        msg = 'M 2\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_Z(self):
        msg = 'Z 1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')
        msg = 'Z 0\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_Z_too_few_params(self):
        msg = 'Z\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_Z_wrong_params(self):
        msg = 'Z 2\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_S(self):
        msg = 'S 100\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_S_too_few_params(self):
        msg = 'S\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_R(self):
        msg = 'R\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            len(self.system.parse(msg[-1]).split()), 3 + self.system.channels
        )

    def _send_x_command(self, msg):
        time.sleep(0.05)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_X(self):
        # A sample period of 501 allows to receive only
        # one packet in a second, therefore speeding up the test
        sample_period = 501
        msg = 'X %d 1 0 %s %d\n' % (
            sample_period,
            LISTENING_ADDRESS,
            LISTENING_PORT
        )

        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((LISTENING_ADDRESS, LISTENING_PORT))
        sock.listen(1)

        t = Thread(target=self._send_x_command, args=(msg,))
        t.start()
        s, _ = sock.accept()
        t.join()

        # We also check if the sample counter reverts to 0
        self.system.sample_counter = 65535

        msg = 'resume\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')
        time.sleep(float(sample_period / 2) / 1000)

        msg = 'pause\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

        data = s.recv(1024)
        self.assertEqual(len(data), 64 * int(1000 / sample_period))

        msg = 'resume\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')
        time.sleep(float(sample_period / 2) / 1000)

        msg = 'stop\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

        data = s.recv(1024)
        self.assertEqual(len(data), 64 * int(1000 / sample_period))

        s.close()
        sock.close()

    def test_X_wrong_port(self):
        msg = 'X 40 0 0 127.0.0.1 5001\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaises(socket.error):
            self.system.parse(msg[-1])

    def test_X_too_few_params(self):
        msg = 'X 40 0 0 127.0.0.1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_X_disconnect_without_stop(self):
        # A sample period of 501 allows to receive only
        # one packet in a second, therefore speeding up the test
        sample_period = 501
        msg = 'X %d 1 0 %s %d\n' % (
            sample_period,
            LISTENING_ADDRESS,
            LISTENING_PORT
        )

        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((LISTENING_ADDRESS, LISTENING_PORT))
        sock.listen(1)

        t = Thread(target=self._send_x_command, args=(msg,))
        t.start()
        s, _ = sock.accept()
        sock.close()
        t.join()

        msg = 'resume\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')
        time.sleep(float(sample_period + 10) / 1000)

        data = s.recv(1024)

        # Disconnect socket
        s.close()

        self.assertEqual(len(data), 64 * int(1000 / sample_period))

        t0 = time.time()
        # Wait up to 2 seconds for the timer to join and be set to None
        while time.time() - t0 < 2:
            if self.system.data_timer is None:
                break
            time.sleep(0.01)
        if self.system.data_timer:
            self.fail('timer is taking too long to join!')

    def test_resume_without_X(self):
        msg = 'resume\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def test_V(self):
        msg = 'V\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            self.system.parse(msg[-1]), self.system.firmware_string
        )


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_I(self):
        self.assertEqual(self.board.I, 'PRIM')
        self.board.I = 'B'
        self.assertEqual(self.board.I, 'BWG')
        self.board.I = 'DUMMY'
        self.assertEqual(self.board.I, 'BWG')
        self.board.I = 'GREG'
        self.assertEqual(self.board.I, 'GREG')
        self.board.I = 'Z'
        self.assertEqual(self.board.I, '50_OHM')
        self.board.I = None
        self.assertEqual(self.board.I, 'GREG')

    def test_A(self):
        self.assertEqual(self.board.A, 7)
        self.board.A = 14
        self.assertEqual(self.board.A, 14)
        self.board.A = 1000
        self.assertEqual(self.board.A, 14)

    def test_F(self):
        self.assertEqual(self.board.F, 1)
        self.board.F = 4
        self.assertEqual(self.board.F, 4)
        self.board.F = 10
        self.assertEqual(self.board.F, 4)

    def test_B(self):
        self.assertEqual(self.board.B, 2000)
        self.board.F = 4
        self.assertEqual(self.board.F, 4)
        self.assertEqual(self.board.B, 300)
        self.board.F = 10
        self.assertEqual(self.board.F, 4)
        self.assertEqual(self.board.B, 300)


if __name__ == '__main__':
    unittest.main()
