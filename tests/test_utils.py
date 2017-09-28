import unittest
from simulators import utils


class TestServer(unittest.TestCase):

    def test_right_checksum(self):
        """Return the sum of bytes that compose the string, capped to 8 bits
        and then inverted (one's complement)."""
        self.assertEqual(utils.checksum('fooo'), 'L')

    def test_wrong_checksum(self):
        """Compare the actual checksum with a wrong one."""
        self.assertNotEqual(utils.checksum('fooo'), 'A')

    def test_right_twos_to_int(self):
        """Return the signed integer of the given binary string
        (two's complement)"""
        self.assertEqual(utils.twos_to_int('101'.zfill(8)), 5)

    def test_wrong_twos_to_int(self):
        """Compare the acual signed integer of the given binary string
        with a wrong one (correct is -5)."""
        self.assertNotEqual(utils.twos_to_int('11111011'), 251)

    def test_int_to_twos(self):
        """Return the binary string (two's complement) expressed in 32 bits
        of the given signed integer"""
        self.assertEqual(
            utils.int_to_twos(5),
            '00000000000000000000000000000101'
        )
        self.assertEqual(
            utils.int_to_twos(5, 2),
            '0000000000000101'
        )

    def test_out_of_range_int_to_twos(self):
        """Raise a ValueError in case of out of range integer value"""
        with self.assertRaises(ValueError):
            utils.int_to_twos(4294967295)

    def test_mjd(self):
        """Make sure that the datatype of the response is the correct one."""
        self.assertIsInstance(utils.mjd(), float)

    def test_day_milliseconds(self):
        """Make sure that the datatype of the response is the correct one.
        Also make sure that the returned value is inside the expected range."""
        day_milliseconds = utils.day_milliseconds()
        self.assertIsInstance(day_milliseconds, int)
        self.assertGreaterEqual(day_milliseconds, 0)
        self.assertLess(day_milliseconds, 86400000)

    def test_binary_to_bytes_correct(self):
        """Convert a binary string into a string of bytes."""
        binary_string = '00000101000110100010100011010010'
        byte_string = utils.binary_to_bytes(binary_string)
        expected_byte_string = b'\x05\x1A\x28\xD2'
        self.assertEqual(byte_string, expected_byte_string)

    def test_binary_to_bytes_wrong(self):
        binary_string = '00000101000110100010100011010010'
        byte_string = utils.binary_to_bytes(binary_string)
        expected_byte_string = b'\x05\x1A\x28\xD3'
        self.assertNotEqual(byte_string, expected_byte_string)

    def test_bytes_to_int_correct(self):
        """Convert a string of bytes into an integer (like C atoi function)."""
        byte_string = b'\x00\x00\xFA\xFF'
        result = utils.bytes_to_int(byte_string)
        expected_result = 64255
        self.assertEqual(result, expected_result)

    def test_bytes_to_int_wrong(self):
        byte_string = b'\x00\x00\xFA\xFF'
        result = utils.bytes_to_int(byte_string)
        expected_result = -1281
        self.assertNotEqual(result, expected_result)

    def test_double_to_binary(self):
        """Convert a double to its binary representation."""
        number = 3.14159265358979323846264338327950288419716939937510582097494
        result = utils.double_to_binary(number)
        expected_result = (
            '0100000000001001001000011111101101010100010001000010110100011000'
        )
        self.assertEqual(result, expected_result)

    def test_double_to_binary_wrong(self):
        number = 3.14159265358979323846264338327950288419716939937510582097494
        result = utils.double_to_binary(number)
        expected_result = (
            '0100000000001001001010011111101101010100010001000010110100011000'
        )
        self.assertNotEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
