import unittest
from simulators import active_surface, utils


byte_ack = '\x06'
byte_nak = '\x15'


class TestASParse(unittest.TestCase):

    def setUp(self):
        self.system = active_surface.System()

    def test_fa_header(self):
        """Return True when the first byte is the 0xFA header."""
        # '\xFA' header -> we do not get the driver address in the response
        self.assertTrue(self.system.parse('\xFA'))

    def test_fc_header(self):
        """Return True when the first byte is the 0xFC header."""
        # '\xFC' header -> we get the driver address in the response
        self.assertTrue(self.system.parse('\xFC'))

    def test_wrong_header(self):
        """Return False when the first byte is not an allowed header."""
        self.assertFalse(self.system.parse(b'w'))

    def test_broadcast(self):
        """Return True in case of broadcast byte (byte_switchall)."""
        self.system.parse('\xFA')  # Send the header
        self.assertTrue(self.system.parse('\x00'))  # Send broadcast byte

    def test_expected_second_byte(self):
        """The second byte should have the value 0x00 or > 0x1F."""
        self.system.parse('\xFA')  # Send the header
        self.assertTrue(self.system.parse('\xAF'))

    def test_wrong_second_byte(self):
        self.system.parse('\xFA')  # Send the header
        with self.assertRaises(ValueError):
            self.system.parse('\x0F')

    def test_wrong_message_lenght(self):
        msg = b'\xFA\x40\x01\x02'  # The ckecksum is '0xC2'
        for byte in msg:
            self.system.parse(byte)
        # Declaring a lenght of 2 but sending 3 bytes
        with self.assertRaises(ValueError):
            self.system.parse('\x01')

    def test_wrong_message_broadcast_lenght(self):
        msg = b'\xFA\x00\x02\x01\x02'  # The ckecksum is 0
        for byte in msg:
            self.system.parse(byte)
        # Declaring a lenght of 2 but sending 3 bytes
        with self.assertRaises(ValueError):
            self.system.parse('\x01')

    def test_unknown_command(self):
        msg = b'\xFA\x20\x00'
        for byte in msg:
            self.system.parse(byte)
        with self.assertRaises(ValueError):
            self.system.parse(utils.checksum(msg))

    def test_too_high_message_length(self):
        msg = b'\xFA\x00\x08'
        for byte in msg[:-1]:
            self.system.parse(byte)
        with self.assertRaises(ValueError):
            self.system.parse(msg[-1])

    def test_wait_for_header_after_wrong_message_lenght(self):
        msg = b'\xFA\x40\x01\x02\x01'  # The ckecksum is '0xC2'
        for byte in msg:
            try:
                self.system.parse(byte)
            except ValueError:
                pass
        self.assertFalse(self.system.parse(b'w'))
        self.assertTrue(self.system.parse('\xFA'))

    def test_soft_reset(self):
        """The system returns True for every proper byte, and
        returns the byte_ack when the message is completed."""
        msg = b'\xFA\x20\x01'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_soft_reset(self):
        msg = b'\xFA\x40\x01\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_soft_reset(self):
        """A proper broadcast command always returns True, also when
        the message is completed."""
        msg = b'\xFA\x00\x01\x01'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_soft_reset(self):
        msg = b'\xFA\x00\x02\x01\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_soft_trigger(self):
        msg = b'\xFA\x20\x02'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_soft_trigger(self):
        msg = b'\xFA\x40\x02\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_soft_trigger(self):
        msg = b'\xFA\x00\x01\x02'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_soft_trigger(self):
        msg = b'\xFA\x00\x02\x02\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_get_version_1(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the driver version
        expressed as a byte when the message is completed."""
        msg = b'\xFA\x20\x10'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        # byte_ack + byte_start + version + byte_checksum
        expected_length = 4
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_get_version_2(self):
        msg = b'\xFC\x20\x10'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        # byte_ack + byte_start + byte_nbyte_address + version + byte_checksum
        expected_length = 5
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_wrong_get_version(self):
        msg = b'\xFA\x40\x10\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        # byte_ack + byte_start + version + byte_checksum
        expected_length = 1
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_nak)

    def test_broadcast_get_version(self):
        msg = b'\xFA\x00\x01\x10'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_get_version(self):
        msg = b'\xFA\x00\x02\x10\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_soft_stop(self):
        msg = b'\xFA\x20\x11'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_soft_stop(self):
        msg = b'\xFA\x40\x11\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_soft_stop(self):
        msg = b'\xFA\x00\x01\x11'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_soft_stop(self):
        msg = b'\xFA\x00\x02\x11\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_get_position_1(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver position
        expressed as 4 bytes when the message is completed."""
        msg = b'\xFA\x20\x12'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        expected_length = 7  # byte_ack + byte_start + pos 3-0 + byte_checksum
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_get_position_2(self):
        msg = b'\xFC\x20\x12'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        expected_length = 8
        # byte_ack + byte_start + byte_nbyte_address + pos 3-0 + byte_checksum
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_wrong_get_position(self):
        msg = b'\xFA\x40\x12\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_get_position(self):
        msg = b'\xFA\x00\x01\x12'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_get_position(self):
        msg = b'\xFA\x00\x02\x12\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_get_status_1(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver status
        expressed as 3 bytes when the message is completed."""
        msg = b'\xFA\x20\x13'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        # byte_ack + byte_start + status 0-2 + byte_checksum
        expected_length = 6
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_get_status_2(self):
        msg = b'\xFC\x20\x13'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        # byte_ack
        # + byte_start
        # + byte_nbyte_address
        # + status 0-2
        # + byte_checksum
        expected_length = 7
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_wrong_get_status(self):
        msg = b'\xFA\x40\x13\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_get_status(self):
        msg = b'\xFA\x00\x01\x13'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_get_status(self):
        msg = b'\xFA\x00\x02\x13\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_get_driver_type_1(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver type
        expressed as a byte when the message is completed."""
        msg = b'\xFA\x20\x14'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        # byte_ack + byte_start + driver_type + byte_checksum
        expected_length = 4
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_get_driver_type_2(self):
        msg = b'\xFC\x20\x14'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(utils.checksum(msg))
        # byte_ack
        # + byte_start
        # + byte_nbyte_address
        # + driver_type
        # + byte_checksum
        expected_length = 5
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_wrong_get_driver_type(self):
        msg = b'\xFA\x40\x14\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_get_driver_type(self):
        msg = b'\xFA\x00\x01\x14'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_get_driver_type(self):
        msg = b'\xFA\x00\x02\x14\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_in_range_min_frequency(self):
        """Setting min freq to 1000Hz (\x03\xE8), allowed range is 20-10000Hz,
        so the system returns the byte_ack"""
        msg = b'\xFA\x60\x20\x03\xE8'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_broadcast_set_in_range_min_frequency(self):
        msg = b'\xFA\x00\x03\x20\x03\x08'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_out_range_min_frequency(self):
        """Setting min freq to 10Hz (\x00\x0A), outside the allowed range,
        so the system returns the byte_nak"""
        msg = b'\xFA\x60\x20\x00\x0A'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_out_range_min_frequency(self):
        msg = b'\xFA\x00\x03\x20\x00\x0A'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_set_min_frequency(self):
        msg = b'\xFA\x20\x20'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_wrong_broadcast_set_min_frequency(self):
        msg = b'\xFA\x00\x01\x20'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_in_range_max_frequency(self):
        """Setting max freq to 9000Hz (\x23\x28), allowed range is 20-10000Hz,
        so the system returns the byte_ack"""
        msg = b'\xFA\x60\x21\x23\x28'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_broadcast_set_in_range_max_frequency(self):
        msg = b'\xFA\x00\x03\x21\x23\x28'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_out_range_max_frequency(self):
        """Setting max freq to 11000Hz (\x2A\xF8), outside the allowed range,
        so the system returns the byte_nak"""
        msg = b'\xFA\x60\x21\x2A\xF8'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_out_range_max_frequency(self):
        msg = b'\xFA\x00\x03\x21\x2A\xF8'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_set_max_frequency(self):
        msg = b'\xFA\x20\x21'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_wrong_broadcast_set_max_frequency(self):
        msg = b'\xFA\x00\x01\x21'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_slope(self):
        msg = b'\xFA\x40\x22\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_slope(self):
        msg = b'\xFA\x20\x22'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_slope(self):
        msg = b'\xFA\x00\x02\x22\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_slope(self):
        msg = b'\xFA\x00\x01\x22'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_reference_position(self):
        msg = b'\xFA\xA0\x23\x00\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_reference_position(self):
        msg = b'\xFA\x20\x23'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_reference_position(self):
        msg = b'\xFA\x00\x05\x23\x00\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_reference_position(self):
        msg = b'\xFA\x00\x01\x23'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_IO_pins_1(self):
        msg = b'\xFA\x40\x25\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_set_IO_pins_2(self):
        msg = b'\xFA\x40\x25\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_IO_pins(self):
        msg = b'\xFA\x20\x25'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_IO_pins(self):
        msg = b'\xFA\x00\x02\x25\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_IO_pins(self):
        msg = b'\xFA\x00\x01\x25'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_resolution(self):
        msg = b'\xFA\x40\x26\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_set_auto_resolution(self):
        msg = b'\xFA\x40\x26\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_resolution(self):
        msg = b'\xFA\x20\x26'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_resolution(self):
        msg = b'\xFA\x00\x02\x26\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_resolution(self):
        msg = b'\xFA\x00\x01\x26'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_reduce_current(self):
        msg = b'\xFA\x40\x27\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_reduce_current(self):
        msg = b'\xFA\x20\x27'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_reduce_current(self):
        msg = b'\xFA\x00\x02\x27\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_reduce_current(self):
        msg = b'\xFA\x00\x01\x27'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_finite_delay(self):
        msg = b'\xFA\x40\x28\x00'  # Setting a delay step equal to 0
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_broadcast_set_finite_delay(self):
        msg = b'\xFA\x00\x02\x28\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_infinite_delay(self):
        msg = b'\xFA\x40\x28\xFF'  # Setting an infinite delay
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_broadcast_set_inifinte_delay(self):
        msg = b'\xFA\x00\x02\x28\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_set_delay(self):
        msg = b'\xFA\x20\x28'  # Setting a delay step equal to 0
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_wrong_broadcast_set_delay(self):
        msg = b'\xFA\x00\x01\x28'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_toggle_delayed_execution_1(self):
        msg = b'\xFA\x40\x29\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_toggle_delayed_execution_2(self):
        msg = b'\xFA\x40\x29\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_toggle_delayed_execution(self):
        msg = b'\xFA\x20\x29'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_toggle_delayed_execution(self):
        msg = b'\xFA\x00\x02\x29\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_toggle_delayed_execution(self):
        msg = b'\xFA\x00\x01\x29'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_absolute_position(self):
        msg = b'\xFA\xA0\x30\x00\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_absolute_position(self):
        msg = b'\xFA\x20\x30'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_absolute_position(self):
        msg = b'\xFA\x00\x05\x30\x00\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_absolute_position(self):
        msg = b'\xFA\x00\x01\x30'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_relative_position(self):
        msg = b'\xFA\xA0\x31\x00\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_relative_position(self):
        msg = b'\xFA\x20\x31'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_relative_position(self):
        msg = b'\xFA\x00\x05\x31\x00\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_relative_position(self):
        msg = b'\xFA\x00\x01\x31'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_rotate(self):
        """The driver starts to rotate according to its set velocity.
        The last byte of the message (before the checksum, \x00)
        holds an int in twos complement notation, its sign (+ or -)
        represents the direction in which the motor will rotate"""
        msg = b'\xFA\x40\x32\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_rotate(self):
        msg = b'\xFA\x20\x32'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_rotate(self):
        msg = b'\xFA\x00\x02\x32\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_rotate(self):
        msg = b'\xFA\x00\x01\x32'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_in_range_velocity(self):
        """Setting velocity in a range between -100000 and +100000
        tenths of Hz.  The value is stored in the last 3 bytes
        (\x00\x00\x00 in this case)"""
        msg = b'\xFA\x80\x35\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_broadcast_set_in_range_velocity(self):
        msg = b'\xFA\x00\x04\x35\x00\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_out_range_velocity(self):
        """Setting velocity outside allowed range.
        Bytes \xEF\xFF\xFF represents a velocity of 8388607 tenths of Hz"""
        msg = b'\xFA\x80\x35\xEF\xFF\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_out_range_velocity(self):
        msg = b'\xFA\x00\x04\x35\xEF\xFF\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_set_velocity(self):
        msg = b'\xFA\x20\x35'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_wrong_broadcast_set_velocity(self):
        msg = b'\xFA\x00\x01\x35'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_stop_IO_1(self):
        msg = b'\xFA\x40\x2A\x09'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_set_stop_IO_2(self):
        msg = b'\xFA\x40\x2A\x36'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_stop_IO(self):
        msg = b'\xFA\x20\x2A'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_stop_IO(self):
        msg = b'\xFA\x00\x02\x2A\x09'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_stop_IO(self):
        msg = b'\xFA\x00\x01\x2A'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_positioning_IO_1(self):
        msg = b'\xFA\x40\x2B\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_set_positioning_IO_2(self):
        msg = b'\xFA\x40\x2B\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_positioning_IO(self):
        msg = b'\xFA\x20\x2B'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_positioning_IO(self):
        msg = b'\xFA\x00\x02\x2B\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_positioning_IO(self):
        msg = b'\xFA\x00\x01\x2B'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_home_IO_1(self):
        msg = b'\xFA\x40\x2C\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_set_home_IO_2(self):
        msg = b'\xFA\x40\x2C\xFF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_home_IO(self):
        msg = b'\xFA\x20\x2C'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_home_IO(self):
        msg = b'\xFA\x00\x02\x2C\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_home_IO(self):
        msg = b'\xFA\x00\x01\x2C'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_set_working_mode(self):
        msg = b'\xFA\x60\x2D\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_ack)

    def test_wrong_set_working_mode(self):
        msg = b'\xFA\x20\x2D'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(utils.checksum(msg)), byte_nak)

    def test_broadcast_set_working_mode(self):
        msg = b'\xFA\x00\x03\x2D\x00\x00'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_wrong_broadcast_set_working_mode(self):
        msg = b'\xFA\x00\x01\x2D'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(utils.checksum(msg)))

    def test_delayed_execution(self):
        self.test_toggle_delayed_execution_1()
        self.test_set_relative_position()
        self.test_set_absolute_position()
        self.test_soft_trigger()
        self.test_soft_trigger()


if __name__ == '__main__':
    unittest.main()
