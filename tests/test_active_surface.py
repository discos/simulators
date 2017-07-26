import unittest
from simulators import active_surface


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
        checksum = b'\xE4'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_soft_reset(self):
        """A proper broadcast command always returns True, also when
        the message is completed."""
        msg = b'\xFA\x00\x01\x01'
        checksum = b'\x03'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_soft_trigger(self):
        msg = b'\xFA\x20\x02'
        checksum = b'\xE3'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_soft_trigger(self):
        msg = b'\xFA\x00\x01\x02'
        checksum = b'\x02'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_get_version(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the driver version
        expressed as a byte when the message is completed."""
        msg = b'\xFA\x20\x10'
        checksum = b'\xD5'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(checksum)
        # byte_ack + byte_start + version + byte_checksum
        expected_length = 4
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_broadcast_get_version(self):
        msg = b'\xFA\x00\x01\x10'
        checksum = b'\xF4'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_soft_stop(self):
        msg = b'\xFA\x20\x11'
        checksum = b'\xD4'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_soft_stop(self):
        msg = b'\xFA\x00\x01\x11'
        checksum = b'\xF3'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_get_position(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver position
        expressed as 4 bytes when the message is completed."""
        msg = b'\xFA\x20\x12'
        checksum = b'\xD3'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(checksum)
        expected_length = 7  # byte_ack + byte_start + pos 3-0 + byte_checksum
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_broadcast_get_position(self):
        msg = b'\xFA\x00\x01\x12'
        checksum = b'\xF2'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_get_status(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver status
        expressed as 3 bytes when the message is completed."""
        msg = b'\xFA\x20\x13'
        checksum = b'\xD2'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(checksum)
        # byte_ack + byte_start + status 0-2 + byte_checksum
        expected_length = 6
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_broadcast_get_status(self):
        msg = b'\xFA\x00\x01\x13'
        checksum = b'\xF1'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_get_driver_type(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver type
        expressed as a byte when the message is completed."""
        msg = b'\xFA\x20\x14'
        checksum = b'\xD1'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(checksum)
        # byte_ack + byte_start + driver_type + byte_checksum
        expected_length = 4
        self.assertEqual(expected_length, len(response))
        self.assertEqual(response[0], byte_ack)

    def test_broadcast_get_driver_type(self):
        msg = b'\xFA\x00\x01\x14'
        checksum = b'\xF0'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_in_range_min_frequency(self):
        """Setting min freq to 1000Hz (\x03\xE8), allowed range is 20-10000Hz,
        so the system returns the byte_ack"""
        msg = b'\xFA\x60\x20\x03\xE8'
        checksum = b'\x9A'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_in_range_min_frequency(self):
        msg = b'\xFA\x00\x03\x20\x03\x08'
        checksum = b'\xD7'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_out_range_min_frequency(self):
        """Setting min freq to 10Hz (\x00\x0A), outside the allowed range,
        so the system returns the byte_nak"""
        msg = b'\xFA\x60\x20\x00\x0A'
        checksum = b'\x7B'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_nak

    def test_broadcast_set_out_range_min_frequency(self):
        msg = b'\xFA\x00\x03\x20\x00\x0A'
        checksum = b'\xD8'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_in_range_max_frequency(self):
        """Setting max freq to 9000Hz (\x23\x28), allowed range is 20-10000Hz,
        so the system returns the byte_ack"""
        msg = b'\xFA\x60\x21\x23\x28'
        checksum = b'\x39'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_in_range_max_frequency(self):
        msg = b'\xFA\x00\x03\x21\x23\x28'
        checksum = b'\x96'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_out_range_max_frequency(self):
        """Setting max freq to 11000Hz (\x2A\xF8), outside the allowed range,
        so the system returns the byte_nak"""
        msg = b'\xFA\x60\x21\x2A\xF8'
        checksum = b'\x62'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_nak)

    def test_broadcast_set_out_range_max_frequency(self):
        msg = b'\xFA\x00\x03\x21\x2A\xF8'
        checksum = b'\xBF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_slope(self):
        msg = b'\xFA\x40\x22\x00'
        checksum = b'\xA3'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_slope(self):
        msg = b'\xFA\x00\x02\x22\x00'
        checksum = b'\xE1'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_reference_position(self):
        msg = b'\xFA\xA0\x23\x00\x00\x00\x00'
        checksum = b'\x42'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_reference_position(self):
        msg = b'\xFA\x00\x05\x23\x00\x00\x00\x00'
        checksum = b'\xDD'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_IO_pins(self):
        msg = b'\xFA\x40\x25\x00'
        checksum = b'\xA0'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_IO_pins(self):
        msg = b'\xFA\x00\x02\x25\x00'
        checksum = b'\xDE'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_resolution(self):
        msg = b'\xFA\x40\x26\x00'
        checksum = b'\x9F'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_resolution(self):
        msg = b'\xFA\x00\x02\x26\x00'
        checksum = b'\xDD'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_reduce_current(self):
        msg = b'\xFA\x40\x27\x00'
        checksum = b'\x9E'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_reduce_current(self):
        msg = b'\xFA\x00\x02\x27\x00'
        checksum = b'\xDC'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_finite_delay(self):
        msg = b'\xFA\x40\x28\x00'  # Setting a delay step equal to 0
        checksum = b'\x9D'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_finite_delay(self):
        msg = b'\xFA\x00\x02\x28\x00'
        checksum = b'\xDB'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_infinite_delay(self):
        msg = b'\xFA\x40\x28\xFF'  # Setting an infinite delay
        checksum = b'\x9E'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_broadcast_set_inifinte_delay(self):
        msg = b'\xFA\x00\x02\x28\xFF'
        checksum = b'\xDC'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_toggle_delayed_execution(self):
        msg = b'\xFA\x40\x29\x00'
        checksum = b'\x9C'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_toggle_delayed_execution(self):
        msg = b'\xFA\x00\x02\x29\x00'
        checksum = b'\xDA'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_absolute_position(self):
        msg = b'\xFA\xA0\x30\x00\x00\x00\x00'
        checksum = b'\x35'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_absolute_position(self):
        msg = b'\xFA\x00\x05\x30\x00\x00\x00\x00'
        checksum = b'\xD0'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_relative_position(self):
        msg = b'\xFA\xA0\x31\x00\x00\x00\x00'
        checksum = b'\x34'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_relative_position(self):
        msg = b'\xFA\x00\x05\x31\x00\x00\x00\x00'
        checksum = b'\xCF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_rotate(self):
        """The driver starts to rotate according to its set velocity.
        The last byte of the message (before the checksum, \x00)
        holds an int in twos complement notation, its sign (+ or -)
        represents the direction in which the motor will rotate"""
        msg = b'\xFA\x40\x32\x00'
        checksum = b'\x93'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_rotate(self):
        msg = b'\xFA\x00\x02\x32\x00'
        checksum = b'\xD1'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_in_range_velocity(self):
        """Setting velocity in a range between -100000 and +100000
        tenths of Hz.  The value is stored in the last 3 bytes
        (\x00\x00\x00 in this case)"""
        msg = b'\xFA\x80\x35\x00\x00\x00'
        checksum = b'\x50'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_in_range_velocity(self):
        msg = b'\xFA\x00\x04\x35\x00\x00\x00'
        checksum = b'\xCC'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_out_range_velocity(self):
        """Setting velocity outside allowed range.
        Bytes \xEF\xFF\xFF represents a velocity of 8388607 tenths of Hz"""
        msg = b'\xFA\x80\x35\xEF\xFF\xFF'
        checksum = b'\x63'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_nak)

    def test_broadcast_set_out_range_velocity(self):
        msg = b'\xFA\x00\x04\x35\xEF\xFF\xFF'
        checksum = b'\xDF'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_stop_IO(self):
        msg = b'\xFA\x40\x2A\x09'
        checksum = b'\x92'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_stop_IO(self):
        msg = b'\xFA\x00\x02\x2A\x09'
        checksum = b'\xD0'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_positioning_IO(self):
        msg = b'\xFA\x40\x2B\x00'
        checksum = b'\x9A'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_positioning_IO(self):
        msg = b'\xFA\x00\x02\x2B\x00'
        checksum = b'\xD8'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_home_IO(self):
        msg = b'\xFA\x40\x2C\x00'
        checksum = b'\x99'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_home_IO(self):
        msg = b'\xFA\x00\x02\x2C\x00'
        checksum = b'\xD7'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))

    def test_set_working_mode(self):
        msg = b'\xFA\x60\x2D\x00\x00'
        checksum = b'\x78'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.parse(checksum), byte_ack)

    def test_broadcast_set_working_mode(self):
        msg = b'\xFA\x00\x03\x2D\x00\x00'
        checksum = b'\xD5'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))


if __name__ == '__main__':
    unittest.main()
