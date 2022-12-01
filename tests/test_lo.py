import unittest
from simulators.lo import System


class TestGenericLocalOscillator(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='generic_LO')

    def test_set_power(self, power=10):
        msg = f'POWER {power} dBm\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.power, power)

    def test_set_wrong_power(self, power=10):
        # dBm suffix missing
        msg = f'POWER {power}\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.power, power)

        # wrong dBm suffix
        msg = f'POWER {power} dbm\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.power, power)

        # String instead of int power
        msg = 'POWER dummy dBm\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.power, power)

    def test_get_power(self):
        power = 20
        self.test_set_power(power=power)
        msg = 'POWER?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{power}\n')

    def test_set_get_power(self, power=10):
        msg = f'POWER {power} dBm;POWER?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{power}\n')

    def test_set_frequency(self, frequency=10):
        msg = f'FREQ {frequency} MHZ\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.frequency, frequency)

    def test_set_wrong_frequency(self, frequency=10):
        # MHZ suffix missing
        msg = f'FREQ {frequency}\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.frequency, frequency)

        # wrong MHZ suffix
        msg = f'FREQ {frequency} MHz\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.frequency, frequency)

        # String instead of int frequency
        msg = 'FREQ dummy MHZ\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.frequency, frequency)

    def test_get_frequency(self):
        frequency = 20
        self.test_set_frequency(frequency=frequency)
        msg = 'FREQ?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{frequency * 1000000}\n')

    def test_set_get_frequency(self, frequency=10):
        msg = f'FREQ {frequency} MHZ;FREQ?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{frequency * 1000000}\n')

    def test_read_status(self):
        msg = 'SYST:ERR?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, '0,\"No error\"\n')

    def test_wrong_empty_commands(self):
        msg = 'dummy;;\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))


class TestWLocalOscillator(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='w_LO')

    def test_set_w_LO_freq_PolH(self, polh=12.23):
        msg = 'set W_LO_freq_PolH=12.23\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_lo_freq_polH, polh)

    def test_set_w_LO_freq_PolV(self, polv=31.82):
        msg = 'set W_LO_freq_PolV=31.82\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_lo_freq_polV, polv)

    def test_get_w_LO_PolH(self, polh=12.23):
        msg = 'set W_LO_freq_PolH=12.23\r\nget W_LO_PolH\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'W_LO_freq_PolH={self.system.w_lo_freq_polH} Mhz',
            f'W_LO_freq_PolH={polh} Mhz')

    def test_get_w_LO_PolV(self, polv=31.82):
        msg = 'set W_LO_freq_PolV=31.82\r\nget W_LO_PolV\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'W_LO_freq_PolH={self.system.w_lo_freq_polV} Mhz',
            f'W_LO_freq_PolH={polv} Mhz')

    def test_get_w_LO(self, polh=12.23, polv=31.82):
        msg = "set W_LO_freq_PolH=12.23\r\n" +\
            "set W_LO_freq_PolV=31.82\r\nget W_LO\r\n"
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'W_LO_freq_PolH={self.system.w_lo_freq_polH} Mhz,'
            f'\n W_LO_freq_PolV={self.system.w_lo_freq_polV} Mhz'),
            (f'W_LO_freq_PolH={polh} Mhz,'
            f'\n W_LO_freq_PolV={polv} Mhz'))

    def test_get_w_LO_status(self, stat_polh="Unlocked", stat_polv="Unlocked"):
        msg = 'get W_LO_status\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'W_LO_PolH={self.system.status_W_LO_PolH} Mhz'
            f'\nW_LO_PolV={self.system.status_W_LO_PolV} Mhz'),
            (f'W_LO_PolH={stat_polh} Mhz'
            f'\nW_LO_PolV={stat_polv} Mhz'))

    def test_set_LO_att_PolH(self, att_polh=9.22):
        msg = 'set LO_att_PolH=9.22\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.lo_att_polH, att_polh)

    def test_set_LO_att_PolV(self, att_polv=12.51):
        msg = 'set LO_att_PolV=12.51\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.lo_att_polV, att_polv)

    def test_get_LO_att_PolH(self, att_polh=9.22):
        msg = 'set LO_att_PolH=9.22\r\nget LO_att_PolH\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'LO_att_PolH={self.system.lo_att_polH}',
            f'LO_att_PolH={att_polh}')

    def test_get_LO_att_PolV(self, att_polv=12.51):
        msg = 'set LO_att_PolV=12.51\r\nget LO_att_PolV\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'LO_att_PolH={self.system.lo_att_polV}',
            f'LO_att_PolH={att_polv}')

    def test_get_LO_att(self, att_polh=9.22, att_polv=12.51):
        msg = 'set LO_att_PolH=9.22\r\nset LO_att_PolV=12.51\r\nget LO_att\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'LO_att_PolH={self.system.lo_att_polH},'
            f'\nLO_att_PolV={self.system.lo_att_polV}'),
            (f'LO_att_PolH={att_polh},'
            f'\nLO_att_PolV={att_polv}'))


class TestLocalOscillatorUnknownType(unittest.TestCase):

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            self.system = System(system_type='unknown')


if __name__ == '__main__':
    unittest.main()
