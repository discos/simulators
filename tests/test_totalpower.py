import unittest
from simulators.totalpower import System


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
        msg = 'Z\n'
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

    def test_X(self):
        pass

    def test_X_too_few_params(self):
        msg = 'X 40 0 0 127.0.0.1\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'nak\n')

    def send_socket_data(self):
        pass

    def test_V(self):
        msg = 'V\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            self.system.parse(msg[-1]), self.system.firmware_string
        )

    def test_pause(self):
        msg = 'pause\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_stop(self):
        msg = 'stop\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')

    def test_resume(self):
        msg = 'resume\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(msg[-1]), 'ack\n')


if __name__ == '__main__':
    unittest.main()
