import unittest
from simulators.switch_matrix import System


class TestSwitchMatrix(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def tearDown(self):
        del self.system

    def test_get_IF_switch_config(self, swmatrix=1):
        msg = 'get IF_switch_config\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg)
        self.assertEqual(response, swmatrix)

    def test_set_IF_switch_config(self, ans=True):
        msg = 'set IF_switch_config=2\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        print(msg)
        response = self.system.parse(msg)
        self.assertEqual(response, ans)

    def test_set_IF_switch_matrix(self, ans="ack\r\n"):
        msg = 'set IF_switch_config=2\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        print(msg)
        response = self.system.set_IF_switch_config("2")
        self.assertEqual(response, ans)

    def test_wrong_commands(self):
        msg = 'dummy;;\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_empty_commands(self):
        msg = '\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))


if __name__ == '__main__':
    unittest.main()
