import unittest
import time
from simulators import dbesm


class TestDBESM(unittest.TestCase):

    def setUp(self):
        self.system = dbesm.System()

    def _send(self, message):
        for byte in message[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(message[-1])
        return response

    def test_all_diag(self):
        message = "DBE ALLDIAG\x0D"
        response = self._send(message)
        print(response)
        # self.assertEqual(len(response), 1)
        # self.assertEqual(response[0], 'ack')


if __name__ == '__main__':
    unittest.main()
