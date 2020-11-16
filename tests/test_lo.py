import unittest
from simulators.lo import System


class TestLocalOscillator(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def tearDown(self):
        del self.system

    def test_set_power(self, power=10):
        msg = 'POWER %d dBm\n' % power
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.power, power)

    def test_set_wrong_power(self, power=10):
        # dBm suffix missing
        msg = 'POWER %d\n' % power
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.power, power)

        # wrong dBm suffix
        msg = 'POWER %d dbm\n' % power
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
        self.assertEqual(response, '%s\n' % power)

    def test_set_get_power(self, power=10):
        msg = 'POWER %d dBm;POWER?\n' % power
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, '%s\n' % power)

    def test_set_frequency(self, frequency=10):
        msg = 'FREQ %d MHZ\n' % frequency
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.frequency, frequency)

    def test_set_wrong_frequency(self, frequency=10):
        # MHZ suffix missing
        msg = 'FREQ %d\n' % frequency
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.frequency, frequency)

        # wrong MHZ suffix
        msg = 'FREQ %d MHz\n' % frequency
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
        self.assertEqual(response, '%s\n' % (frequency * 1000000))

    def test_set_get_frequency(self, frequency=10):
        msg = 'FREQ %d MHZ;FREQ?\n' % frequency
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, '%d\n' % (frequency * 1000000))

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


if __name__ == '__main__':
    unittest.main()
