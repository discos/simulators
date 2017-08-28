import unittest
from simulators import acu, utils


class TestACU(unittest.TestCase):

    n = 10
    start_flag = b'\x1D\xFC\xCF\x1A'
    end_flag = b'\xA1\xFC\xCF\xD1'

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

    def test_parse(self):
        msg_length = bin(46)[2:].zfill(32)
        cmd_counter = bin(utils.day_milliseconds())[2:].zfill(32)
        cmds_counter = bin(1)[2:].zfill(32)

        # Command
        cmd_id = bin(1)[2:].zfill(16)
        sub_id = bin(1)[2:].zfill(16)
        counter = bin(utils.day_milliseconds())[2:].zfill(32)
        mode_id = bin(1)[2:].zfill(16)
        par_1 = bin(0)[2:].zfill(64)
        par_2 = bin(0)[2:].zfill(64)

        command = (
            cmd_id
            + sub_id
            + counter
            + mode_id
            + par_1
            + par_2
        )

        commands = command  # Could be more than one command

        binary_msg = (
            msg_length
            + cmd_counter
            + cmds_counter
            + commands
        )

        msg = self.start_flag

        for i in range(0, len(binary_msg), 8):
            msg += chr(int(binary_msg[i:i + 8], 2))

        msg += self.end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        self.assertEqual(
            self.system.parse(msg[-1]),
            [hex(ord(x)) for x in msg]
        )


if __name__ == '__main__':
    unittest.main()
