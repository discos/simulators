import unittest
import time
from simulators import acu
from simulators import utils
from simulators.acu import start_flag, end_flag

class TestACU(unittest.TestCase):

    def setUp(self):
        self.system = acu.System(0)

    def test_status_message_length(self):
        status = self.system.get_status()
        msg_length = utils.bytes_to_int(status[4:8])
        self.assertEqual(msg_length, 539)

    def test_status_message_counter(self):
        for i in range(10):
            status = self.system.get_status()
            msg_counter = utils.bytes_to_int(status[8:12])
            self.assertEqual(msg_counter, i)

    def test_status_message_sampling_time(self):
        self.system = acu.System()
        time.sleep(1)
        status = self.system.get_status()
        msg_counter = utils.bytes_to_int(status[8:12])
        self.assertGreater(msg_counter, 1)

    def test_parse_correct_end_flag(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_parse_wrong_end_flag(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse('\x00')  # Wrong ending byte

    def test_parse_wrong_start_flag(self):
        self.assertFalse(self.system.parse('\x00'))

    def test_mode_command_azimut(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_mode_command_elevation(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(1, 2)
        sub_id = utils.int_to_twos(2, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_mode_command_unknown_subsystem(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(1, 2)
        sub_id = utils.int_to_twos(3, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(msg[-1])

    def test_mode_command_unknown_mode_id(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(1, 2)
        sub_id = utils.int_to_twos(1, 2)
        counter = utils.int_to_twos(utils.day_milliseconds())
        mode_id = utils.int_to_twos(0, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(msg[-1])

    def test_parameter_command_azimut(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(2, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_parameter_command_elevation(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(2, 2)
        sub_id = utils.int_to_twos(2, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_parameter_command_pointing(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(2, 2)
        sub_id = utils.int_to_twos(5, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_parameter_command_unknown_subsystem(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(2, 2)
        sub_id = utils.int_to_twos(3, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(msg[-1])

    def test_multiple_commands(self):
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(3)

        commands = b''

        cmd_id = utils.int_to_twos(4, 2)
        sub_id = utils.int_to_twos(1, 2)
        counter = utils.int_to_twos(utils.day_milliseconds())
        parameter_id = utils.int_to_twos(1, 2)
        interpolation_mode = utils.int_to_twos(0, 2)
        tracking_mode = utils.int_to_twos(0, 2)
        load_mode = utils.int_to_twos(0, 2)
        sequence_length = utils.int_to_twos(0, 2)
        start_time = utils.real_to_binary(utils.mjd(), 2)
        max_rate_azimut = utils.int_to_twos(0, 8)
        max_rate_elevation = utils.int_to_twos(0, 8)
        relative_time = utils.int_to_twos(0, 4)
        azimut_position = utils.int_to_twos(0, 8)
        elevation_position = utils.int_to_twos(0, 8)

        command = (
            cmd_id
            + sub_id
            + counter
            + parameter_id
            + interpolation_mode
            + tracking_mode
            + load_mode
            + sequence_length
            + start_time
            + max_rate_azimut
            + max_rate_elevation
            + relative_time
            + azimut_position
            + elevation_position
            + utils.int_to_twos(utils.bytes_to_int(end_flag))
        )
        commands += command

        for i in range(1, 3):
            cmd_id = utils.int_to_twos(i, 2)
            sub_id = utils.int_to_twos(1, 2)
            counter = utils.int_to_twos(utils.day_milliseconds())
            mode_parameter_id = utils.int_to_twos(1, 2)
            par_1 = utils.int_to_twos(0, 8)
            par_2 = utils.int_to_twos(0, 8)
            command = (
                cmd_id
                + sub_id
                + counter
                + mode_parameter_id
                + par_1
                + par_2
            )
            commands += command

        msg_length = utils.int_to_twos(20 + (len(commands) / 8))

        binary_msg = (
            msg_length
            + cmd_counter
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_multiple_commands_wrong_count(self):
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(4)  # Actually sending 3 commands

        commands = b''

        cmd_id = utils.int_to_twos(4, 2)
        sub_id = utils.int_to_twos(1, 2)
        counter = utils.int_to_twos(utils.day_milliseconds())
        parameter_id = utils.int_to_twos(1, 2)
        interpolation_mode = utils.int_to_twos(0, 2)
        tracking_mode = utils.int_to_twos(0, 2)
        load_mode = utils.int_to_twos(0, 2)
        sequence_length = utils.int_to_twos(0, 2)
        start_time = utils.real_to_binary(utils.mjd(), 2)
        max_rate_azimut = utils.int_to_twos(0, 8)
        max_rate_elevation = utils.int_to_twos(0, 8)
        relative_time = utils.int_to_twos(0, 4)
        azimut_position = utils.int_to_twos(0, 8)
        elevation_position = utils.int_to_twos(0, 8)

        command = (
            cmd_id
            + sub_id
            + counter
            + parameter_id
            + interpolation_mode
            + tracking_mode
            + load_mode
            + sequence_length
            + start_time
            + max_rate_azimut
            + max_rate_elevation
            + relative_time
            + azimut_position
            + elevation_position
            + utils.int_to_twos(utils.bytes_to_int(end_flag))
        )
        commands += command

        for i in range(1, 3):
            cmd_id = utils.int_to_twos(i, 2)
            sub_id = utils.int_to_twos(1, 2)
            counter = utils.int_to_twos(utils.day_milliseconds())
            mode_parameter_id = utils.int_to_twos(1, 2)
            par_1 = utils.int_to_twos(0, 8)
            par_2 = utils.int_to_twos(0, 8)
            command = (
                cmd_id
                + sub_id
                + counter
                + mode_parameter_id
                + par_1
                + par_2
            )
            commands += command

        msg_length = utils.int_to_twos(20 + (len(commands) / 8))

        binary_msg = (
            msg_length
            + cmd_counter
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(msg[-1])

    def test_unknown_command(self):
        msg_length = utils.int_to_twos(46)
        cmd_counter = utils.int_to_twos(utils.day_milliseconds())
        cmds_number = utils.int_to_twos(1)

        # Command
        cmd_id = utils.int_to_twos(3, 2)
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
            + cmds_number
            + commands
        )

        msg = start_flag
        msg += utils.binary_to_bytes(binary_msg)
        msg += end_flag

        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(msg[-1])


if __name__ == '__main__':
    unittest.main()
