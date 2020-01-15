import unittest
from simulators.mscu import System


class TestMSCU(unittest.TestCase):

    def setUp(self):
        self.system = System()


if __name__ == '__main__':
    unittest.main()
