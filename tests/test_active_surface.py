import unittest
from simulators import active_surface


class TestAS(unittest.TestCase):

    def test_checksum(self):
        self.assertEqual(utils.checksum('foo'), 187)


if __name__ == '__main__':
    unittest.main()
