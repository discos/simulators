import unittest
from simulators import if_distributor



class TestIFDistributorParse(unittest.TestCase):

    def setUp(self):
        self.system = if_distributor.System()

    def test_get_header(self):
        """Return True when the first byte is the header."""
        header = self.system.header
        self.assertTrue(self.system.parse(header))

    def test_wrong_header(self):
        """Return False when the first byte is not an allowed header."""
        self.assertFalse(self.system.parse(b'w'))

    def test_max_msg_length_reached(self):
        """Raise ValueError in case the max_msg_length is reached."""
        msg = b'#aaa 99 9999'  # The last byte is not the expected tail
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaises(ValueError):
            self.system.parse(msg[-1])

    def test_wong_number_of_setup_items(self):
        """Raise ValueError in case the setup has wrong number of items."""
        msg = b'#aaa 99999\n'  # Three items required, two given
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'must have three items'):
            self.system.parse(msg[-1])

    def test_wong_setup_device(self):
        """Raise ValueError in case the setup device is unknown."""
        # The device type has to be ATT or SWT
        msg = b'#aaa 99 999\n'  # aaa is not a valid device type
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'device aaa not in'):
            self.system.parse(msg[-1])

    def test_setup_id_not_integer(self):
        """Raise ValueError in case the device ID is not an integer."""
        msg = b'#ATT XX 999\n'  # The ID XX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'the device ID must be an integer'):
            self.system.parse(msg[-1])

    def test_setup_id_not_allowed(self):
        """Raise ValueError in case of wrong device ID."""
        msg = b'#ATT 99 999\n'  # The ID 99 does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'device 99 does not exist'):
            self.system.parse(msg[-1])

    def test_setup_value_not_integer(self):
        """Raise ValueError in case the setup value is not an integer."""
        msg = b'#ATT 00 XXX\n'  # The value XXX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'the device value must be an integer'):
            self.system.parse(msg[-1])

    def test_setup_value_not_allowed(self):
        """Raise ValueError in case of wrong setup value."""
        msg = b'#ATT 00 999\n'  # The value 999, for the ATT 00, does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'value 999 not allowed'):
            self.system.parse(msg[-1])

    def test_setup_sets_the_value(self):
        """The setup has to set the device value."""
        value = self.system.devices['ATT'][0][1]
        for byte in b'#ATT 00 001\n':
            self.system.parse(byte)
        self.assertEqual(self.system.ATT_0, value)

    def _test_set_and_get_value(self):
        value = self.system.devices['ATT'][0][1]
        # Set the value
        for byte in b'#ATT 00 001\n':
            self.system.parse(byte)
        print value
        # Get the value


    def test_wrong_command(self):
        # #aaa99999\n
        pass


if __name__ == '__main__':
    unittest.main()
