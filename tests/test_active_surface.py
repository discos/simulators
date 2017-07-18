import unittest
from simulators import active_surface


byte_ack = '\x06'
byte_nak = '\x15'


class TestASParse(unittest.TestCase):

    def setUp(self):
        self.system = active_surface.System()

    def test_fa_header(self):
        """The system returns True when the first byte is the header."""
        # '\xFA' header -> we do not get the driver address in the response
        self.assertTrue(self.system.parse('\xFA'))

    def test_fc_header(self):
        """The system returns True when the first byte is the 0xFC header."""
        # '\xFC' header -> we get the driver address in the response
        self.assertTrue(self.system.parse('\xFC'))

    def test_wrong_header(self):
        """The system returns False when the first byte is not an allowed header."""
        self.assertFalse(self.system.parse(b'w'))

    def test_broadcast(self):
        """Return True in case of broadcast byte (byte_switchall)."""
        self.system.parse('\xFA')  # Send the header
        self.assertTrue(self.system.parse('\x00'))  # Send broadcast byte

    def test_expected_second_byte(self):
        """The second byte should have a value > 0x1F."""
        self.system.parse('\xFA')  # Send the header
        self.assertTrue(self.system.parse('\xAF'))

    def test_wrong_second_byte(self):
        """The second byte should have the value 0x00 or > 0x1F."""
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

    def test_broadcast_command(self):
        """A proper broadcast command always returns True, also when
        the message is completed."""
        msg = b'\xFA\x00\x01\x01'
        checksum = b'\x03'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertTrue(self.system.parse(checksum))


if __name__ == '__main__':
    unittest.main()
