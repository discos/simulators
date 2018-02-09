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

    def test_wrong_number_of_setup_items(self):
        """Raise ValueError in case the setup has wrong number of items."""
        msg = b'#aaa 99999\n'  # Three items required, two given
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'must have three items'):
            self.system.parse(msg[-1])

    def test_wrong_setup_command(self):
        """Raise ValueError in case the setup command is unknown."""
        # The command type has to be ATT or SWT
        msg = b'#aaa 99 999\n'  # aaa is not a valid command type
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'command aaa not in'):
            self.system.parse(msg[-1])

    def test_setup_channel_not_integer(self):
        """Raise ValueError in case the channel ID is not an integer."""
        msg = b'#ATT XX 999\n'  # The ID XX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'the channel ID must be an integer'):
            self.system.parse(msg[-1])

    def test_setup_channel_not_allowed(self):
        """Raise ValueError in case of wrong channel ID."""
        msg = b'#ATT 99 999\n'  # The ID 99 does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'channel 99 does not exist'):
            self.system.parse(msg[-1])

    def test_setup_value_not_integer(self):
        """Raise ValueError in case the setup value is not an integer."""
        msg = b'#ATT 00 XXX\n'  # The value XXX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'the command value must be an integer'):
            self.system.parse(msg[-1])

    def test_setup_value_not_allowed(self):
        """Raise ValueError in case of wrong setup value."""
        msg = b'#ATT 00 999\n'  # The value 999, for the ATT 00, does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'value 999 not allowed'):
            self.system.parse(msg[-1])

    def test_setup_sets_the_value(self):
        """The setup has to set the channel value."""
        value = 100
        for byte in b'#ATT 00 %03d\n' % value:
            self.system.parse(byte)
        self.assertEqual(self.system.channels[0], value)

    def test_default_setup(self):
        """The channel must have a default value."""
        default_value = self.system.max_att_multiplier
        self.assertEqual(self.system.channels[0], default_value)

    def test_wrong_number_of_get_items(self):
        """Raise ValueError in case the GET has wrong number of items."""
        msg = b'#aaa 99 99?\n'  # Two items required, three given
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'must have two items'):
            self.system.parse(msg[-1])

    def test_wrong_get_channel(self):
        """Raise ValueError in case the GET command is unknown."""
        # The command type has to be ATT or SWT
        msg = b'#aaa 00?\n'  # aaa is not a valid command type
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'command aaa not in'):
            self.system.parse(msg[-1])

    def test_get_channel_not_integer(self):
        """Raise ValueError in case the channel ID is not an integer."""
        msg = b'#ATT XX?\n'  # The ID XX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'the channel ID must be an integer'):
            self.system.parse(msg[-1])

    def test_get_channel_not_allowed(self):
        """Raise ValueError in case of wrong channel ID."""
        msg = b'#ATT 99?\n'  # The ID 99 does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'channel 99 does not exist'):
            self.system.parse(msg[-1])

    def test_set_and_get_value(self):
        value = 100
        # Set the value
        for byte in b'#ATT 00 %03d\n' % value:
            self.system.parse(byte)
        # Get the value
        msg = b'#ATT 00?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, b'#%s\n' % (value * self.system.att_step))

    def test_idn_command(self):
        version = self.system.version
        # Get the value
        for byte in b'#*IDN?\n':
            response = self.system.parse(byte)
        self.assertEqual(response, version)

    def test_rst(self):
        # Set a non-default value
        value = 100
        for byte in b'#ATT 00 %03d\n' % value:
            self.system.parse(byte)
        # Get the value
        msg = b'#ATT 00?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, b'#%s\n' % (value * self.system.att_step))
        # Set the default values
        for byte in b'#*RST\n':
            self.system.parse(byte)
        # Get the value
        msg = b'#ATT 00?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        default_value = self.system.max_att_multiplier * self.system.att_step
        response = self.system.parse(msg[-1])
        self.assertEqual(response, '#%s\n' % default_value)

    def test_wrong_command(self):
        for byte in b'#abcdefg\n':
            response = self.system.parse(byte)
        self.assertEqual(response, b'#COMMAND UNKNOWN\n')

    def test_set_switch(self):
        msg = b'#SWT 00 001\n'
        for byte in msg:
            self.system.parse(byte)
        self.assertTrue(self.system.switched)

    def test_enable_and_disable_switch(self):
        msg = b'#SWT 00 001\n'
        for byte in msg:
            self.system.parse(byte)
        self.assertTrue(self.system.switched)
        msg = b'#SWT 00 000\n'
        for byte in msg:
            self.system.parse(byte)
        self.assertFalse(self.system.switched)

    def test_get_switch(self):
        msg = b'#SWT 00?\n'
        for byte in msg:
            response = self.system.parse(byte)
        expected_response = b'#0\n'
        self.assertEqual(expected_response, response)

    def test_set_and_get_switch(self):
        msg = b'#SWT 00 001\n'
        for byte in msg:
            self.system.parse(byte)
        msg = b'#SWT 00?\n'
        for byte in msg:
            response = self.system.parse(byte)
        expected_response = b'#1\n'
        self.assertEqual(expected_response, response)

    def test_set_wrong_switch(self):
        msg = b'#SWT 00 002\n'  # Only 000 and 001 are accepted
        for byte in msg[:-1]:
            self.system.parse(byte)
        with self.assertRaisesRegexp(
            ValueError, 'SWT command accepts only values 00 or 01'):
            self.system.parse(msg[-1])


if __name__ == '__main__':
    unittest.main()
