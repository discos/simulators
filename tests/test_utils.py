import unittest
from simulators import utils


class TestServer(unittest.TestCase):

    def test_right_checksum(self):
        """Returns the sum of bytes that compose the string, capped to 8 bits
        and than inverted (one's complement)."""
        self.assertEqual(utils.checksum('foo'), 187)

    def test_wrong_checksum(self):
        self.assertNotEqual(utils.checksum('foo'), 186)

    def test_right_twos_to_int(self):
        self.assertEqual(utils.twos_to_int('101'.zfill(8)), 5)

    def test_wrong_twos_to_int(self):
        self.assertNotEqual(utils.twos_to_int('11111011'), 251)

    def test_int_to_twos(self):
        self.assertEqual(utils.int_to_twos(5), '00000000000000000000000000000101')

    def test_out_of_range_int_to_twos(self):
        with self.assertRaises(ValueError):
            utils.int_to_twos(4294967295)

    def test_mjd(self):
        self.assertEqual(type(utils.mjd()), float)

    def test_day_milliseconds(self):
        day_milliseconds = utils.day_milliseconds()
        self.assertEqual(type(day_milliseconds), int)
        self.assertTrue(day_milliseconds >= 0)
        self.assertTrue(day_milliseconds < 86400000)
        

if __name__ == '__main__':
    unittest.main()
