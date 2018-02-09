import unittest
import time
from datetime import datetime, timedelta
from simulators import acu
from simulators import utils
from simulators.acu_status.acu_utils import Command
from simulators.acu_status.acu_utils import ModeCommand
from simulators.acu_status.acu_utils import ParameterCommand
from simulators.acu_status.acu_utils import ProgramTrackCommand
from simulators.acu_status.acu_utils import ProgramTrackEntry

class TestACU(unittest.TestCase):

    def setUp(self):
        self.system = acu.System(0)

    def tearDown(self):
        del self.system

    def test_status_message_length(self):
        status = self.system.get_status()
        msg_length = utils.bytes_to_int(status[4:8])
        self.assertEqual(msg_length, 813)

    def test_status_message_counter(self):
        for i in range(10):
            status = self.system.get_status()
            msg_counter = utils.bytes_to_int(status[8:12])
            self.assertEqual(msg_counter, i)

    def test_status_message_sampling_time(self):
        self.system = acu.System()
        time.sleep(2)
        status = self.system.get_status()
        msg_counter = utils.bytes_to_int(status[8:12])
        self.assertGreater(msg_counter, 1)

    def test_parse_correct_end_flag(self):
        commands = Command(ModeCommand(1, 1)).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_parse_wrong_end_flag(self):
        commands = Command(ModeCommand(1, 1)).get()

        for byte in commands[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse('\x00')  # Wrong ending byte

    def test_parse_wrong_start_flag(self):
        self.assertFalse(self.system.parse('\x00'))

    def test_mode_command_azimuth(self):
        commands = Command(ModeCommand(1, 1)).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_mode_command_elevation(self):
        commands = Command(ModeCommand(2, 1)).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_mode_command_unknown_subsystem(self):
        commands = Command(ModeCommand(3, 1)).get()

        for byte in commands[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(commands[-1])

    def test_mode_command_unknown_mode_id(self):
        mode_id = 0  # 0: unknown mode id
        commands = Command(ModeCommand(1, mode_id))

        msg = commands.get()

        command_counter = commands.command_list[-1].command_counter

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, mode_id)
        self.assertEqual(mcs.received_command_answer, 0)

        # Make sure the command has not been executed (unknown mode id)
        self.assertEqual(mcs.executed_mode_command_counter, 0)
        self.assertEqual(mcs.executed_mode_command, 0)
        self.assertEqual(mcs.executed_command_answer, 0)

    def test_mode_command_azimuth_inactive(self):
        mode_id = 1  # 1: inactive
        commands = Command(ModeCommand(1, mode_id))

        msg = commands.get()

        command_counter = commands.command_list[-1].command_counter

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, mode_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, mode_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_active(self):
        mode_id = 2  # 2: active
        commands = Command(ModeCommand(1, mode_id))

        msg = commands.get()

        command_counter = commands.command_list[-1].command_counter

        for byte in msg:
            self.assertTrue(self.system.parse(byte))

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, mode_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, mode_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_preset_absolute(self):
        # Axis needs to be activated before sending the command
        activate_id = 2
        activate = ModeCommand(1, activate_id)

        commands = Command(activate)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        preset_abs_id = 3
        des_pos = 175.0
        des_rate = -0.75
        preset_absolute = ModeCommand(1, preset_abs_id, des_pos, des_rate)

        commands = Command(preset_absolute)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        # We let the system start executing the given command
        time.sleep(0.2)

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, preset_abs_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Check if command has started the execution
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, preset_abs_id)
        self.assertEqual(mcs.executed_command_answer, 2)  # 2 == executing

        # Should be in position in ~7 seconds but we give it 8 to be sure
        time.sleep(8)

        res_pos = int(round(self.system.acu.Azimuth.p_Ist / 1000000))
        self.assertEqual(res_pos, des_pos)

        mcs = self.system.acu.Azimuth.mcs

        # Check if command has been correctly executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, preset_abs_id)
        self.assertEqual(mcs.executed_command_answer, 1)  # 1 == executed

    def test_mode_command_azimuth_preset_relative(self):
        # We save the current axis position for further comparison
        start_pos = int(round(self.system.acu.Azimuth.p_Ist / 1000000))

        # Axis needs to be activated before sending this command
        activate_id = 2
        activate = ModeCommand(1, activate_id)

        commands = Command(activate)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        preset_rel_id = 4
        des_delta = -5.0
        des_rate = -0.75
        preset_relative = ModeCommand(1, preset_rel_id, des_delta, des_rate)

        commands = Command(preset_relative)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        # We let the system start executing the given command
        time.sleep(0.2)

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, preset_rel_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Check if command has started the execution
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, preset_rel_id)
        self.assertEqual(mcs.executed_command_answer, 2)  # 2 == executing

        # Should be in position in ~7 seconds but we give it 8 to be sure
        time.sleep(8)

        res_pos = int(round(self.system.acu.Azimuth.p_Ist / 1000000))
        self.assertEqual(res_pos, start_pos + des_delta)

        mcs = self.system.acu.Azimuth.mcs

        # Check if command has been correctly executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, preset_rel_id)
        self.assertEqual(mcs.executed_command_answer, 1)  # 1 == executed

    def test_mode_command_azimuth_slew(self):
        # We save the current axis position for further comparison
        start_pos = int(round(self.system.acu.Azimuth.p_Ist / 1000000))

        # Axis needs to be activated before sending this command
        activate_id = 2
        activate = ModeCommand(1, activate_id)

        commands = Command(activate)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        slew_id = 5
        slew = ModeCommand(1, slew_id, 1, 0.5)

        commands = Command(slew)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        # We let the system start executing the given command
        time.sleep(0.2)

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, slew_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Check if command has started the execution
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, slew_id)
        self.assertEqual(mcs.executed_command_answer, 2)

        time.sleep(1)

        # Make sure the axis has started moving
        res_pos = int(round(self.system.acu.Azimuth.p_Ist / 1000000))
        self.assertNotEqual(res_pos, start_pos)

    def test_mode_command_azimuth_stop(self):
        # Axis needs to be activated before sending this command
        activate_id = 2
        activate = ModeCommand(1, activate_id)

        commands = Command(activate)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        stop_id = 7
        stop = ModeCommand(1, stop_id)

        commands = Command(stop)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, stop_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, stop_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_program_track(self):
        # Axis needs to be activated before sending this command
        activate_id = 2
        activate = ModeCommand(1, activate_id)

        commands = Command(activate)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        program_track_id = 8
        program_track = ModeCommand(1, program_track_id)

        commands = Command(program_track)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, program_track_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, program_track_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_interlock(self):
        mode_id = 14  # 14: interlock
        commands = Command(ModeCommand(1, mode_id))

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, mode_id)
        self.assertEqual(mcs.received_command_answer, 9)

        time.sleep(0.05)

        mcs = self.system.acu.Azimuth.mcs

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, mode_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_reset(self):
        mode_id = 15  # 15: reset
        commands = Command(ModeCommand(1, mode_id))

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, mode_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, mode_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_stow(self):
        mode_id = 50  # 50: stow
        commands = Command(ModeCommand(1, mode_id))

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, mode_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, mode_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_unstow(self):
        mode_id = 51  # 51: unstow
        commands = Command(ModeCommand(1, mode_id))

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, mode_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, mode_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_mode_command_azimuth_drive_to_stow(self):
        # Axis needs to be activated before sending this command
        activate_id = 2
        activate = ModeCommand(1, activate_id)

        commands = Command(activate)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        drive_to_stow_id = 52
        drive_to_stow = ModeCommand(1, drive_to_stow_id)

        commands = Command(drive_to_stow)

        for byte in commands.get():
            self.assertTrue(self.system.parse(byte))

        command_counter = commands.command_list[-1].command_counter

        # We let the system execute the given command
        time.sleep(0.2)

        mcs = self.system.acu.Azimuth.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received_mode_command_counter, command_counter)
        self.assertEqual(mcs.received_mode_command, drive_to_stow_id)
        self.assertEqual(mcs.received_command_answer, 9)

        # Make sure the command has been executed
        self.assertEqual(mcs.executed_mode_command_counter, command_counter)
        self.assertEqual(mcs.executed_mode_command, drive_to_stow_id)
        self.assertEqual(mcs.executed_command_answer, 1)

    def test_parameter_command_azimuth(self):
        commands = Command(ParameterCommand(1, 1)).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_parameter_command_elevation(self):
        commands = Command(ParameterCommand(2, 1)).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_parameter_command_pointing(self):
        commands = Command(ParameterCommand(5, 1)).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_parameter_command_unknown_subsystem(self):
        commands = Command(ParameterCommand(3, 1)).get()

        for byte in commands[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(commands[-1])

    def test_program_track_command_load_new_table(self):
        command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1)
        )
        command.add_entry(
            relative_time=1,
            azimuth_position=1,
            elevation_position=1
        )
        command.add_entry(2, 2, 2)
        command.add_entry(3, 3, 3)
        command.add_entry(4, 4, 4)
        command.add_entry(5, 5, 5)

        commands = Command(command).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_program_track_command_add_entries(self):
        command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1)
        )
        command.add_entry(
            relative_time=1,
            azimuth_position=1,
            elevation_position=1
        )
        command.add_entry(2, 2, 2)
        command.add_entry(3, 3, 3)
        command.add_entry(4, 4, 4)
        command.add_entry(5, 5, 5)

        commands = Command(command).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

        command = ProgramTrackCommand(2, 0, (1, 1))
        command.add_entry(6, 6, 6)

        commands = Command(command).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_program_track_command_add_entries_empty_table(self):
        command = ProgramTrackCommand(2, 0, (1, 1))
        command.add_entry(1, 1, 1)
        pte = ProgramTrackEntry(
            relative_time=2,
            azimuth_position=2,
            elevation_position=2
        )
        command.append_entry(pte)

        commands = Command(command).get()

        for byte in commands[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(commands[-1])

    def test_program_track_execution(self):
        start_time = datetime.utcnow() + timedelta(milliseconds=100)

        command = ProgramTrackCommand(
            load_mode=1,
            start_time=utils.mjd(start_time),
            axis_rates=(0.5, 0.5)
        )
        command.add_entry(
            relative_time=10,
            azimuth_position=181,
            elevation_position=91
        )
        command.add_entry(2000, 182, 92)
        command.add_entry(4000, 183, 93)
        command.add_entry(6000, 182, 92)
        command.add_entry(8000, 181, 91)

        for byte in Command(command).get():
            self.assertTrue(self.system.parse(byte))

        activate_azimuth = ModeCommand(1, 2)
        activate_elevation = ModeCommand(2, 2)

        for byte in Command(activate_azimuth, activate_elevation).get():
            self.assertTrue(self.system.parse(byte))

        start_azimuth = ModeCommand(1, 8, 0, 0.5)
        start_elevation = ModeCommand(2, 8, 0, 0.5)

        for byte in Command(start_azimuth, start_elevation).get():
            self.assertTrue(self.system.parse(byte))

        time.sleep(10.2)

        self.assertEqual(self.system.acu.Azimuth.p_Ist, 181000000)
        self.assertEqual(self.system.acu.Elevation.p_Ist, 91000000)

    def test_multiple_commands(self):
        command_1 = ModeCommand(1, 1)
        command_2 = ParameterCommand(2, 2)

        commands = Command(command_1, command_2).get()

        for byte in commands:
            self.assertTrue(self.system.parse(byte))

    def test_multiple_commands_wrong_count(self):
        command_1 = ModeCommand(1, 1)
        command_2 = ParameterCommand(2, 2)

        commands = Command(command_1, command_2).get()

        commands = commands[:12] + utils.uint_to_bytes(3) + commands[16:]

        for byte in commands[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(commands[-1])

    def test_unknown_command(self):
        commands = Command(ModeCommand(1, 1)).get()

        # Change the command id with an unknown one
        commands = commands[:16] + utils.uint_to_bytes(3, 2) + commands[18:]

        for byte in commands[:-1]:
            self.assertTrue(self.system.parse(byte))

        with self.assertRaises(ValueError):
            self.system.parse(commands[-1])

    def test_utils_program_track_command_wrong_entry(self):
        command = ProgramTrackCommand(1, 0, (0, 0))

        with self.assertRaises(ValueError):
            command.append_entry('dummy')

    def test_utils_program_track_get_empty_table(self):
        command = ProgramTrackCommand(1, 0, (0, 0))
        fake_cmd_counter = 0

        with self.assertRaises(ValueError):
            command.get(fake_cmd_counter)

    def test_utils_macro_command_wrong_type_init(self):
        with self.assertRaises(ValueError):
            Command('dummy')

    def test_utils_macro_command_append(self):
        command = Command()

        command.append(ModeCommand(1, 1)) # This should not raise an exception

        with self.assertRaises(ValueError):
            command.append('dummy')


if __name__ == '__main__':
    unittest.main()
