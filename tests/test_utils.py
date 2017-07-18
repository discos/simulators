import unittest
from simulators import utils


class TestServer(unittest.TestCase):

    def test_checksum(self):
        self.assertEqual(utils.checksum('foo'), 187)


if __name__ == '__main__':
    unittest.main()
