import unittest
from simulators.solar_attenuator import System


class TestSolarAttenuator(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def tearDown(self):
        del self.system

    def test_set_w_solar_attn(self, mode="attenuator"):
        msg = f'set W_solar_attn\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_set_w_cal(self, mode="calibrator"):
        msg = f'set W_cal\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_set_w_passthrough(self, mode="pass-through"):
        msg = f'set W_passthrough\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_get_w_cal_temp(self, cal_temp=21.0):
        msg = f'get W_cal_temp\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.cal_temp, cal_temp)

    def test_get_mode(self, mode="pass-through"):
        msg = f'set W_passthrough\r\nget W_mode\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, mode)

    def test_wrong_commands(self):
        msg = 'dummy;;\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.mode, '')


if __name__ == '__main__':
    unittest.main()
