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
        self.system = acu.System()

    def _send(self, message):
        for byte in message:
            self.assertTrue(self.system.parse(byte))

    def test_status_message_length(self):
        status = self.system.get_message()
        msg_length = utils.bytes_to_int(status[4:8])
        self.assertEqual(msg_length, 813)

    def test_duplicated_macro_command_counter(self):
        command_string = Command(ModeCommand(1, 1)).get()
        self._send(command_string)

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_duplicated_command_counter(self):
        pass

    def test_parse_correct_end_flag(self):
        command_string = Command(ModeCommand(1, 1)).get()
        self._send(command_string)

    def test_parse_wrong_end_flag(self):
        command_string = Command(ModeCommand(1, 1)).get()
        command_string = command_string[:-1] + '\x00'  # Wrong ending byte

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_parse_wrong_start_flag(self):
        self.assertFalse(self.system.parse('\x00'))

    def test_mode_command_azimuth(self):
        command_string = Command(ModeCommand(1, 1)).get()
        self._send(command_string)

    def test_mode_command_elevation(self):
        command_string = Command(ModeCommand(2, 1)).get()
        self._send(command_string)

    def test_mode_command_unknown_subsystem(self):
        command_string = Command(ModeCommand(3, 1)).get()

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_mode_command_unknown_mode_id(self):
        command = Command(ModeCommand(1, 0))  # 0: Unknown mode id
        self._send(command.get())

        command_counter = command.get_counter(0)
        mcs = self.system.AZ.mcs

        # Check if the command has been received
        self.assertEqual(mcs.received.counter, command_counter)
        self.assertEqual(mcs.received.command, 0)  # 0: _ignore
        self.assertEqual(mcs.received.answer, 0)

        # Make sure the command has not been executed
        self.assertEqual(mcs.executed.counter, 0)
        self.assertEqual(mcs.executed.command, 0)
        self.assertEqual(mcs.executed.answer, 0)

    def test_mode_command_inactive(self):
        mode_id = 1  # 1: inactive
        az = ModeCommand(1, mode_id)  # 1: azimuth subsystem
        el = ModeCommand(2, mode_id)  # 2: elevation subsystem
        command = Command(az, el)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_active(self):
        mode_id = 2  # 2: active
        az = ModeCommand(1, mode_id)
        el = ModeCommand(2, mode_id)
        command = Command(az, el)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_preset_absolute(self):
        # Axis needs to be activated before sending this command
        self.test_mode_command_active()

        preset_abs_id = 3

        az_des_pos = 175.0
        az_des_rate = -0.75
        az_preset_abs = ModeCommand(1, preset_abs_id, az_des_pos, az_des_rate)

        el_des_pos = 87.5
        el_des_rate = -0.5
        el_preset_abs = ModeCommand(2, preset_abs_id, el_des_pos, el_des_rate)

        command = Command(az_preset_abs, el_preset_abs)
        self._send(command.get())

        az_command_counter = command.get_counter(-2)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(-1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, preset_abs_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, preset_abs_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Should be both in position in ~7 seconds but we give it 8 to be sure
        time.sleep(8)

        az_res_pos = round(float(self.system.AZ.p_Ist) / 1000000, 1)
        self.assertEqual(az_res_pos, az_des_pos)
        el_res_pos = round(float(self.system.EL.p_Ist) / 1000000, 1)
        self.assertEqual(el_res_pos, el_des_pos)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, preset_abs_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, preset_abs_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_preset_relative(self):
        # We save the current axis positions for further comparison
        az_start_pos = round(float(self.system.AZ.p_Ist) / 1000000, 1)
        el_start_pos = round(float(self.system.EL.p_Ist) / 1000000, 1)

        # Axis needs to be activated before sending this command
        self.test_mode_command_active()

        pres_rel_id = 4

        az_des_delta = -5.0
        az_des_rate = -0.75
        az_preset_rel = ModeCommand(1, pres_rel_id, az_des_delta, az_des_rate)

        el_des_delta = -3.5
        el_des_rate = -0.5
        el_preset_rel = ModeCommand(2, pres_rel_id, el_des_delta, el_des_rate)

        command = Command(az_preset_rel, el_preset_rel)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, pres_rel_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, pres_rel_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Check if azimuth command has started the execution
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, pres_rel_id)
        self.assertEqual(az_mcs.executed.answer, 2)  # 2 == executing

        # Check if elevation command has started the execution
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, pres_rel_id)
        self.assertEqual(el_mcs.executed.answer, 2)  # 2 == executing

        # Should be in position in ~7 seconds but we give it 8 to be sure
        time.sleep(8)

        az_res_pos = round(float(self.system.AZ.p_Ist) / 1000000, 1)
        self.assertEqual(az_res_pos, az_start_pos + az_des_delta)

        el_res_pos = round(float(self.system.EL.p_Ist) / 1000000, 1)
        self.assertEqual(el_res_pos, el_start_pos + el_des_delta)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, pres_rel_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, pres_rel_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_slew(self):
        # We save the current axis positions for further comparison
        az_start_pos = self.system.AZ.p_Ist
        el_start_pos = self.system.EL.p_Ist

        # Axis needs to be activated before sending this command
        self.test_mode_command_active()

        slew_id = 5
        az_slew = ModeCommand(1, slew_id, 1, 0.5)
        el_slew = ModeCommand(2, slew_id, -1, 0.5)

        command = Command(az_slew, el_slew)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, slew_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, slew_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Check if azimuth command has started the execution
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, slew_id)
        self.assertEqual(az_mcs.executed.answer, 2)

        # Check if elevation command has started the execution
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, slew_id)
        self.assertEqual(el_mcs.executed.answer, 2)

        time.sleep(0.1)

        # Make sure the azimuth axis has started moving
        az_res_pos = self.system.AZ.p_Ist
        self.assertNotEqual(az_res_pos, az_start_pos)

        # Make sure the elevation axis has started moving
        el_res_pos = self.system.EL.p_Ist
        self.assertNotEqual(el_res_pos, el_start_pos)

    def test_mode_command_stop(self):
        # Axis needs to be activated before sending this command
        self.test_mode_command_active()

        stop_id = 7
        az_stop = ModeCommand(1, stop_id)
        el_stop = ModeCommand(2, stop_id)

        command = Command(az_stop, el_stop)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, stop_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, stop_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, stop_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, stop_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_program_track(self):
        # Axis needs to be activated before sending this command
        self.test_mode_command_active()

        program_track_id = 8
        az_program_track = ModeCommand(1, program_track_id)
        el_program_track = ModeCommand(2, program_track_id)

        command = Command(az_program_track, el_program_track)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, program_track_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, program_track_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has not been executed (no table)
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, program_track_id)
        self.assertEqual(az_mcs.executed.answer, 3)

        # Make sure the elevation command has not been executed (no table)
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, program_track_id)
        self.assertEqual(el_mcs.executed.answer, 3)

    def test_mode_command_interlock(self):
        mode_id = 14  # 14: interlock
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_reset(self):
        mode_id = 15  # 15: reset
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_stow(self):
        mode_id = 50  # 50: stow
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_unstow(self):
        mode_id = 51  # 51: unstow
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_drive_to_stow(self):
        # Axis needs to be activated before sending this command
        self.test_mode_command_active()

        mode_id = 52  # 52: drive_to_stow
        az_drive_to_stow = ModeCommand(1, mode_id)
        el_drive_to_stow = ModeCommand(2, mode_id)

        command = Command(az_drive_to_stow, el_drive_to_stow)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_program_track_command_load_new_table(self):
        start_time = datetime.utcnow() + timedelta(seconds=1)

        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=utils.mjd(start_time),
            axis_rates=(0.5, 0.5)
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=181,
            elevation_position=91
        )
        pt_command.add_entry(2000, 182, 92)
        pt_command.add_entry(4000, 183, 93)
        pt_command.add_entry(6000, 182, 92)
        pt_command.add_entry(8000, 181, 91)

        command = Command(pt_command)
        self._send(command.get())

    def test_program_track_command_add_entries(self):
        self.test_program_track_command_load_new_table()

        pt_command = ProgramTrackCommand(
            load_mode=2,
            start_time=0,
            axis_rates=(1, 1)
        )
        entry = ProgramTrackEntry(
            relative_time=10000,
            azimuth_position=180,
            elevation_position=90
        )
        pt_command.append_entry(entry)

        command = Command(pt_command)
        self._send(command.get())

    def test_program_track_command_add_entries_empty_table(self):
        pt_command = ProgramTrackCommand(2, 0, (1, 1))
        pt_command.add_entry(1, 1, 1)

        command = Command(pt_command)
        self._send(command.get())

    def test_program_track_unknown_subsystem(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
            subsystem_id=0,
        )
        pt_command.add_entry(
            relative_time=1,
            azimuth_position=1,
            elevation_position=1
        )
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)

        command = Command(pt_command)

        with self.assertRaises(ValueError):
            self._send(command.get())

    def test_program_track_execution(self):
        self.test_program_track_command_load_new_table()

        activate_azimuth = ModeCommand(1, 2)
        activate_elevation = ModeCommand(2, 2)

        start_azimuth = ModeCommand(1, 8, 0, 0.5)
        start_elevation = ModeCommand(2, 8, 0, 0.5)

        command = Command(
            activate_azimuth,
            activate_elevation,
            start_azimuth,
            start_elevation
        )

        self._send(command.get())

        time.sleep(10)

        self.assertEqual(self.system.AZ.p_Ist, 181000000)
        self.assertEqual(self.system.EL.p_Ist, 91000000)

    def test_multiple_commands_wrong_count(self):
        command_1 = ModeCommand(1, 1)
        command_2 = ParameterCommand(2, 2)

        command_string = Command(command_1, command_2).get()

        command_string = (
            command_string[:12]
            + utils.uint_to_bytes(3)
            + command_string[16:]
        )

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_unknown_command(self):
        command_string = Command(ModeCommand(1, 1)).get()

        # Change the command id with an unknown one
        command_string = (
            command_string[:16]
            + utils.uint_to_bytes(3, 2)
            + command_string[18:]
        )

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_utils_program_track_command_wrong_entry(self):
        command = ProgramTrackCommand(1, 0, (0, 0))

        with self.assertRaises(ValueError):
            command.append_entry('dummy')

    def test_utils_program_track_get_empty_table(self):
        command = ProgramTrackCommand(1, 0, (0, 0))

        with self.assertRaises(ValueError):
            command.get(0)  # 0: a fake command counter

    def test_utils_macro_command_wrong_type_init(self):
        with self.assertRaises(ValueError):
            Command('dummy')

    @staticmethod
    def test_utils_macro_command_append():
        command = Command()
        command.append(ModeCommand(1, 1))

    def test_utils_macro_command_append_wrong(self):
        command = Command()

        with self.assertRaises(ValueError):
            command.append('dummy')


if __name__ == '__main__':
    unittest.main()
