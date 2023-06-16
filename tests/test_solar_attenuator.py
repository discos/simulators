import unittest
from simulators.solar_attenuator import System


class TestSolarAttenuator(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def tearDown(self):
        del self.system

    def test_set_w_home(self, home=1):
        msg = 'set W_home\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.home, home)

    def test_set_w_solar_attn(self, mode="attenuator"):
        msg = 'set W_solar_attn\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_set_w_cal(self, mode="calibrator"):
        msg = 'set W_cal\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_set_w_passthrough(self, mode="pass-through"):
        msg = 'set W_passthrough\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_get_mode(self, mode="pass-through"):
        msg = 'set W_passthrough\r\nget W_mode\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_wrong_commands(self):
        msg = 'dummy;;\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, '')

    def test_empty_commands(self):
        msg = '\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, '')


if __name__ == '__main__':
    unittest.main()
