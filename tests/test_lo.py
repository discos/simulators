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


class TestLocalOscillatorUnknownType(unittest.TestCase):

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            self.system = System(system_type='unknown')

if __name__ == '__main__':
    unittest.main()
