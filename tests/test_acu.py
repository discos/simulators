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
        msg_length = utils.bytes_to_int(status[4:8])
        self.assertEqual(msg_length, 539)

    def test_status_message_counter(self):
        for i in xrange(10):
            status = self.system.get_status()
            msg_counter = utils.bytes_to_int(status[8:12])
            self.assertEqual(msg_counter, i)

    def test_parse_correct_end_flag(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_counter = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(1, 2)
        sub_id = utils.int_to_twos(1, 2)
        counter = utils.int_to_twos(utils.day_milliseconds())
        mode_id = utils.int_to_twos(1, 2)
        par_1 = utils.int_to_twos(0, 8)
        par_2 = utils.int_to_twos(0, 8)

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

        msg += utils.binary_to_bytes(binary_msg)

        msg += self.end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        self.assertEqual(
            self.system.parse(msg[-1]),
            [hex(ord(x)) for x in msg]
        )

    def test_parse_wrong_end_flag(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_counter = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(1, 2)
        sub_id = utils.int_to_twos(1, 2)
        counter = utils.int_to_twos(utils.day_milliseconds())
        mode_id = utils.int_to_twos(1, 2)
        par_1 = utils.int_to_twos(0, 8)
        par_2 = utils.int_to_twos(0, 8)

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

        msg += utils.binary_to_bytes(binary_msg)

        msg += self.end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse('\x00'),  # Wrong ending byte

    def test_parse_wrong_start_flag(self):
        self.assertFalse(self.system.parse('\x00'))

if __name__ == '__main__':
    unittest.main()
