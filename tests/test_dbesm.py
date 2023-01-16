import unittest
from simulators.dbesm import System


class TestDBESM(unittest.TestCase):
    
    def setUp(self):
        self.system = System(system_type='DBESM')


if __name__ == '__main__':
    unittest.main()
