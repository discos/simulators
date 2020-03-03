import unittest
from simulators.if_distributor import System


class TestIFDistributorDefaultConfiguration(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='IFD')

    def _send(self, message):
        for byte in message[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(message[-1])
        response = response.strip().split('\n')
        if len(response) == 2:
            response[1] = [int(v) for v in response[1].split(',')]
            self.assertEqual(len(response[1]), 12)
        if response[0] == 'nak':
            raise Exception('Received nak')
        return response

    def test_known_headers(self):
        for header in ['?', 'B', 'S', 'A', 'I']:
            self.assertTrue(self.system.parse(header))
            self.system.msg = b''

    def test_unknown_header(self):
        self.assertFalse(self.system.parse('U'))

    def test_max_msg_length_reached(self):
        message = b'? 0000000000000'
        with self.assertRaises(ValueError):
            self._send(message)

    def test_message_too_short(self):
        with self.assertRaises(ValueError):
            self._send(b'? \n')

    def test_too_few_arguments(self):
        with self.assertRaises(ValueError):
            self._send(b'????????\n')

    def test_unrecognized_command(self):
        with self.assertRaisesRegexp(Exception, 'Received nak'):
            self._send(b'??? 0\n')

    def test_wrong_args_type(self):
        with self.assertRaises(ValueError):
            self._send(b'? ONE\n')

    def test_out_of_range_board(self):
        with self.assertRaises(IndexError):
            self.test_get_status(board=50)

    def test_get_status(self, board=0):
        message = b'? %d\n' % board

        response = self._send(message)

        self.assertEqual(len(response), 2)
        self.assertEqual(response[0], 'ack')
        self.assertEqual(response[1][0], board)

        return response

    def test_get_status_wrong_argc(self):
        with self.assertRaises(ValueError):
            self._send(b'? 0 0\n')

    def test_set_lo(self, board=0, ref_freq=10, lo_freq=2300, lo_enable=1):
        message = b'S %d %d %d %d\n' % (board, ref_freq, lo_freq, lo_enable)

        response = self._send(message)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0], 'ack')

        response = self.test_get_status(board=board)

        self.assertEqual(response[1][0], board)
        self.assertEqual(response[1][3], ref_freq)
        self.assertEqual(response[1][4], lo_freq)
        self.assertEqual(response[1][9], 8 * lo_enable)
        self.assertEqual(response[1][10], lo_enable ^ 1)
        self.assertEqual(response[1][11], lo_enable)

    def test_set_lo_off(self):
        self.test_set_lo(lo_enable=0)

    def test_set_lo_wrong_board(self):
        with self.assertRaisesRegexp(Exception, 'Received nak'):
            self.test_set_lo(board=5)

    def test_set_lo_wrong_argc(self):
        with self.assertRaises(ValueError):
            self._send(b'S 0\n')

    def test_set_lo_wrong_enable(self):
        with self.assertRaises(ValueError):
            self._send(b'S 0 10 2300 5\n')

    def test_set_lo_wrong_ref_freq(self):
        with self.assertRaises(ValueError):
            self._send(b'S 0 100 2300 1\n')

    def test_set_bw(self, board=1, bandwidth=3):
        message = b'B %d %d\n' % (board, bandwidth)

        response = self._send(message)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0], 'ack')

        response = self.test_get_status(board=board)

        self.assertEqual(response[1][0], board)
        self.assertEqual(response[1][9], 8 * bandwidth)

    def test_set_bw_wrong_board(self):
        with self.assertRaisesRegexp(Exception, 'Received nak'):
            self.test_set_bw(board=5)

    def test_set_bw_wrong_bandwidth(self):
        with self.assertRaises(ValueError):
            self.test_set_bw(bandwidth=4)

    def test_set_bw_wrong_argc(self):
        with self.assertRaises(ValueError):
            self._send(b'B 1 3 0\n')

    def test_set_att(self, board=5, channel=0, attenuation=25.5):
        message = b'A %d %d %.2f\n' % (board, channel, attenuation)

        response = self._send(message)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0], 'ack')

        response = self.test_get_status(board=board)

        self.assertEqual(response[1][0], board)
        self.assertEqual(response[1][5 + channel], int(attenuation * 2))

    def test_set_att_out_of_range_board(self):
        with self.assertRaisesRegexp(Exception, 'Received nak'):
            self.test_set_att(board=1)

    def test_set_att_out_of_range_channel(self):
        with self.assertRaises(IndexError):
            self.test_set_att(channel=10)

    def test_set_att_out_of_range_attenuation(self):
        with self.assertRaisesRegexp(Exception, 'Received nak'):
            self.test_set_att(attenuation=50)

    def test_set_att_wrong_argc(self):
        with self.assertRaises(ValueError):
            self._send('A 5 0\n')

    def test_set_input(self, board=2, conversion=0):
        message = b'I %d %d\n' % (board, conversion)

        response = self._send(message)
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0], 'ack')

        response = self.test_get_status(board=board)

        self.assertEqual(response[1][0], board)

        received_input = bin(response[1][9])[2:].zfill(8)[-3:-1]
        expected_input = bin(conversion + 1)[2:].zfill(2)

        self.assertEqual(received_input, expected_input)

    def test_set_input_no_conversion(self):
        self.test_set_input(conversion=1)

    def test_set_input_wrong_argc(self):
        with self.assertRaises(ValueError):
            self._send(b'I 2\n')

    def test_set_input_out_of_range_board(self):
        with self.assertRaisesRegexp(Exception, 'Received nak'):
            self.test_set_input(board=0)

    def test_set_input_wrong_conversion(self):
        with self.assertRaises(ValueError):
            self.test_set_input(conversion=2)


class TestIFDistributor14Channels(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='IFD_14_channels')

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
        with self.assertRaisesRegexp(ValueError, 'Command aaa not in'):
            self.system.parse(msg[-1])

    def test_setup_channel_not_integer(self):
        """Raise ValueError in case the channel ID is not an integer."""
        msg = b'#ATT XX 999\n'  # The ID XX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'The channel ID must be an integer'):
            self.system.parse(msg[-1])

    def test_setup_channel_not_allowed(self):
        """Raise ValueError in case of wrong channel ID."""
        msg = b'#ATT 99 999\n'  # The ID 99 does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'Channel 99 does not exist'):
            self.system.parse(msg[-1])

    def test_setup_value_not_integer(self):
        """Raise ValueError in case the setup value is not an integer."""
        msg = b'#ATT 00 XXX\n'  # The value XXX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'The command value must be an integer'):
            self.system.parse(msg[-1])

    def test_setup_value_not_allowed(self):
        """Raise ValueError in case of wrong setup value."""
        msg = b'#ATT 00 999\n'  # The value 999, for the ATT 00, does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'Value 999 not allowed'):
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
        with self.assertRaisesRegexp(ValueError, 'Command aaa not in'):
            self.system.parse(msg[-1])

    def test_get_channel_not_integer(self):
        """Raise ValueError in case the channel ID is not an integer."""
        msg = b'#ATT XX?\n'  # The ID XX is not an integer
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(
                ValueError, 'The channel ID must be an integer'):
            self.system.parse(msg[-1])

    def test_get_channel_not_allowed(self):
        """Raise ValueError in case of wrong channel ID."""
        msg = b'#ATT 99?\n'  # The ID 99 does not exist
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        with self.assertRaisesRegexp(ValueError, 'Channel 99 does not exist'):
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


class TestIFDistributorUnknownType(unittest.TestCase):

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            self.system = System(system_type='unknown')


if __name__ == '__main__':
    unittest.main()
