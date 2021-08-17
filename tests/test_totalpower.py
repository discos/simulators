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
        pass

    def test_G(self):
        pass

    def test_N(self):
        pass

    def test_M(self):
        pass

    def test_Z(self):
        pass

    def test_S(self):
        pass

    def test_R(self):
        pass

    def test_X(self):
        pass

    def test_K(self):
        pass

    def test_C(self):
        pass

    def test_J(self):
        pass

    def test_O(self):
        pass

    def test_global(self):
        pass

    def test_W(self):
        pass

    def test_L(self):
        pass

    def test_V(self):
        pass


if __name__ == '__main__':
    unittest.main()
