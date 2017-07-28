import unittest
from simulators import acu, utils


class TestACU(unittest.TestCase):

    n = 10

    def setUp(self):
        self.system = acu.System()

    def test_status_queue_size(self):
        self.system = acu.System(0, self.n)
        msg_queue = []
        elapsed = 0
        last = utils.day_milliseconds()
        while len(msg_queue) < self.n and elapsed < 3000:
            msg_queue += self.system.message_queue()
            now = utils.day_milliseconds()
            elapsed += now - last
            last = now
        self.assertEqual(len(msg_queue), self.n)

    def test_status_message_length(self):
        status = self.system.get_status()
        msg_length = (
            ord(status[4]) * 0x1000000
            + ord(status[5]) * 0x10000
            + ord(status[6]) * 0x100
            + ord(status[7])
        )
        self.assertEqual(msg_length, 539)

    def test_status_message_counter(self):
        for i in xrange(10):
            status = self.system.get_status()
            msg_counter = (
                ord(status[8]) * 0x1000000
                + ord(status[9]) * 0x10000
                + ord(status[10]) * 0x100
                + ord(status[11])
            )
            self.assertEqual(msg_counter, i)

if __name__ == '__main__':
    unittest.main()
