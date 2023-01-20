import unittest
from simulators import dbesm


class TestDBESM(unittest.TestCase):

    def setUp(self):
        self.system = dbesm.System()

if __name__ == '__main__':
    unittest.main()