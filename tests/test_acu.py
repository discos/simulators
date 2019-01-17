import unittest
import time
from datetime import datetime, timedelta
from simulators import acu
from simulators import utils
from simulators.acu.acu_utils import (
    Command,
    ModeCommand,
    ParameterCommand,
    ProgramTrackCommand,
    ProgramTrackEntry
)


class TestACU(unittest.TestCase):

    def setUp(self):
        self.system = acu.System()

    def _send(self, message):
        for byte in message:
            self.assertTrue(self.system.parse(byte))
        # Wait for command to start its execution
        time.sleep(0.01)

    def test_status_message_length(self):
        status = self.system.get_message()
        msg_length = utils.bytes_to_uint(status[4:8])
        self.assertEqual(msg_length, 813)
        self.assertEqual(len(status), 813)

    def test_duplicated_command_counter(self):
        command_string = Command(ModeCommand(1, 1)).get()
        self._send(command_string)

        with self.assertRaises(ValueError):
            self._send(command_string)

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

    def test_multiple_command_same_subsystem(self):
        for subsystem in [1, 2]:
            command = Command(
                ModeCommand(subsystem_id=subsystem, mode_id=2),
                ModeCommand(subsystem_id=subsystem, mode_id=1)
            )

            with self.assertRaises(ValueError):
                self._send(command.get())

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

        # Update the status
        self.system.get_message()

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

    def test_mode_command_wrong_state_active(self):
        self.test_mode_command_active()

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
        self.assertEqual(az_mcs.received.answer, 4)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 4)

    def test_mode_command_without_activate(self):
        stop_id = 7  # Cannot stop a non-active axis
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
        self.assertEqual(az_mcs.received.answer, 4)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, stop_id)
        self.assertEqual(el_mcs.received.answer, 4)

    def test_mode_command_preset_absolute(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        preset_abs_id = 3

        az_des_pos = 179.25
        az_des_rate = -0.75
        az_preset_abs = ModeCommand(1, preset_abs_id, az_des_pos, az_des_rate)

        el_des_pos = 89.5
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

        # Should be both in position in ~1 seconds but we give it 2 to be sure
        time.sleep(2)

        az_res_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        self.assertEqual(az_res_pos, az_des_pos)
        el_res_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)
        self.assertEqual(el_res_pos, el_des_pos)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, preset_abs_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, preset_abs_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_preset_absolute_pause(self):
        # We save the starting position for further comparison
        az_start_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        el_start_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        preset_abs_id = 3

        az_des_pos = 179.25
        az_des_rate = -0.75
        az_preset_abs = ModeCommand(1, preset_abs_id, az_des_pos, az_des_rate)

        el_des_pos = 89.5
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

        # Should be both moving but we deactivate the axis after 0.3 seconds
        time.sleep(0.6)
        self.test_mode_command_inactive()

        # We check that the current position is
        # between the starting and the ending one
        az_cur_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        self.assertTrue(az_des_pos < az_cur_pos < az_start_pos)
        el_cur_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)
        self.assertTrue(el_des_pos < el_cur_pos < el_start_pos)

        # We activate the axis again after 1 second
        time.sleep(1)
        self.test_mode_command_active()

        # We finally wait for the command to be completed
        time.sleep(0.6)

        az_res_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        self.assertEqual(az_res_pos, az_des_pos)
        el_res_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)
        self.assertEqual(el_res_pos, el_des_pos)

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, preset_abs_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, preset_abs_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_preset_absolute_wrong_parameters(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        preset_abs_id = 3

        az_des_pos = 500.0
        az_des_rate = -1.75
        az_preset_abs = ModeCommand(1, preset_abs_id, az_des_pos, az_des_rate)

        el_des_pos = 95.0
        el_des_rate = -1.5
        el_preset_abs = ModeCommand(2, preset_abs_id, el_des_pos, el_des_rate)

        command = Command(az_preset_abs, el_preset_abs)
        self._send(command.get())

        az_command_counter = command.get_counter(-2)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(-1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received with wrong params
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, preset_abs_id)
        self.assertEqual(az_mcs.received.answer, 5)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, preset_abs_id)
        self.assertEqual(el_mcs.received.answer, 5)

    def test_mode_command_preset_relative(self):
        # We save the current axis positions for further comparison
        az_start_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        el_start_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        pres_rel_id = 4

        az_des_delta = -0.75
        az_des_rate = -0.75
        az_preset_rel = ModeCommand(1, pres_rel_id, az_des_delta, az_des_rate)

        el_des_delta = -0.5
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

        # Should be in position in ~1 seconds but we give it 2 to be sure
        time.sleep(2)

        az_res_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        self.assertEqual(az_res_pos, az_start_pos + az_des_delta)

        el_res_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)
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

    def test_mode_command_preset_relative_wrong_parameters(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        pres_rel_id = 4

        az_des_delta = 500.0
        az_des_rate = -1.75
        az_preset_rel = ModeCommand(1, pres_rel_id, az_des_delta, az_des_rate)

        el_des_delta = 10.0
        el_des_rate = -1.5
        el_preset_rel = ModeCommand(2, pres_rel_id, el_des_delta, el_des_rate)

        command = Command(az_preset_rel, el_preset_rel)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received with wrong params
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, pres_rel_id)
        self.assertEqual(az_mcs.received.answer, 5)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, pres_rel_id)
        self.assertEqual(el_mcs.received.answer, 5)

    def test_mode_command_slew(self):
        # Move the axis in different positions from the starting one
        self.test_mode_command_preset_absolute()

        # We save the current position for further comparison
        az_start_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        el_start_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)

        slew_id = 5
        az_slew = ModeCommand(1, slew_id, -1, 0.5)
        el_slew = ModeCommand(2, slew_id, 1, 0.5)

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

        time.sleep(2)

        # Make sure the azimuth axis moved
        az_res_pos = self.system.AZ.p_Ist
        self.assertNotEqual(az_res_pos, az_start_pos)

        # Make sure the elevation axis moved
        el_res_pos = self.system.EL.p_Ist
        self.assertNotEqual(el_res_pos, el_start_pos)

    def test_mode_command_slew_zero_speed(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        slew_id = 5
        az_slew = ModeCommand(1, slew_id, 0, 0)
        el_slew = ModeCommand(2, slew_id, 0, 0)

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

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, slew_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, slew_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_slew_wrong_parameters(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        slew_id = 5
        az_slew = ModeCommand(1, slew_id, 2, 1.5)
        el_slew = ModeCommand(2, slew_id, -2, 1.5)

        command = Command(az_slew, el_slew)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        az_mcs = self.system.AZ.mcs
        el_command_counter = command.get_counter(1)
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received with wrong params
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, slew_id)
        self.assertEqual(az_mcs.received.answer, 5)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, slew_id)
        self.assertEqual(el_mcs.received.answer, 5)

    def test_mode_command_stop(self, activate=True):
        # Axis needs to be unstowed and activated before sending this command
        if activate:
            self.test_mode_command_unstow()
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
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
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

        # Make sure the azimuth command has been executed
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, program_track_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, program_track_id)
        self.assertEqual(el_mcs.executed.answer, 1)

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

        # Check if the azimuth command has been received in wrong mode
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 4)

        # Check if the elevation command has been received
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 9)

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_stow_wrong_position(self):
        self.test_mode_command_preset_absolute()

        mode_id = 50  # 50: stow
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received in wrong mode
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 4)

        # Check if the elevation command has been received in wrong mode
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 4)

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
        self.test_mode_command_preset_absolute()

        mode_id = 52  # 52: drive_to_stow
        az_drive_to_stow = ModeCommand(1, mode_id, None, 0.42)
        el_drive_to_stow = ModeCommand(2, mode_id, None, 0.25)

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

        # Make sure the azimuth command has been executed (no stow pos)
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Check if elevation command has started the execution
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 2)

        time.sleep(2)

        el_mcs = self.system.EL.mcs

        # Make sure the elevation command has been executed
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 1)

    def test_mode_command_drive_to_stow_stop(self):
        self.test_mode_command_preset_absolute()

        mode_id = 52  # 52: drive_to_stow
        az_drive_to_stow = ModeCommand(1, mode_id, None, 0.42)
        el_drive_to_stow = ModeCommand(2, mode_id, None, 0.25)

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

        # Make sure the azimuth command has been executed (no stow pos)
        self.assertEqual(az_mcs.executed.counter, az_command_counter)
        self.assertEqual(az_mcs.executed.command, mode_id)
        self.assertEqual(az_mcs.executed.answer, 1)

        # Check if elevation command has started the execution
        self.assertEqual(el_mcs.executed.counter, el_command_counter)
        self.assertEqual(el_mcs.executed.command, mode_id)
        self.assertEqual(el_mcs.executed.answer, 2)

        time.sleep(1)

        # Send a stop command
        self.test_mode_command_stop(activate=False)

        time.sleep(1)

        # Make sure the elevation axis is not stowed
        self.assertEqual(self.system.EL.stowed, 0)

    def test_mode_command_drive_to_stow_wrong_parameters(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        mode_id = 52  # 52: drive_to_stow
        az_drive_to_stow = ModeCommand(1, mode_id, 1, 1.2)
        el_drive_to_stow = ModeCommand(2, mode_id, 1, 1.2)

        command = Command(az_drive_to_stow, el_drive_to_stow)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Check if the azimuth command has been received (no stow_pos)
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, mode_id)
        self.assertEqual(az_mcs.received.answer, 9)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, mode_id)
        self.assertEqual(el_mcs.received.answer, 5)

    def test_parameter_command_absolute_position_offset(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        command = Command(
            ParameterCommand(1, 11, 5, 0),
            ParameterCommand(2, 11, -5, 0)
        )
        self._send(command.get())

        az_pcs = self.system.AZ.pcs
        el_pcs = self.system.EL.pcs

        self.assertEqual(az_pcs.counter, command.get_counter(0))
        self.assertEqual(az_pcs.command, 11)
        self.assertEqual(az_pcs.answer, 1)

        self.assertEqual(el_pcs.counter, command.get_counter(1))
        self.assertEqual(el_pcs.command, 11)
        self.assertEqual(el_pcs.answer, 1)

        self.assertEqual(self.system.AZ.p_Offset, 5000000)
        self.assertEqual(self.system.EL.p_Offset, -5000000)

    def test_parameter_command_relative_position_offset(self):
        self.test_parameter_command_absolute_position_offset()

        command = Command(
            ParameterCommand(1, 12, 5, 0),
            ParameterCommand(2, 12, -5, 0)
        )
        self._send(command.get())

        az_pcs = self.system.AZ.pcs
        el_pcs = self.system.EL.pcs

        self.assertEqual(az_pcs.counter, command.get_counter(0))
        self.assertEqual(az_pcs.command, 12)
        self.assertEqual(az_pcs.answer, 1)

        self.assertEqual(el_pcs.counter, command.get_counter(1))
        self.assertEqual(el_pcs.command, 12)
        self.assertEqual(el_pcs.answer, 1)

        self.assertEqual(self.system.AZ.p_Offset, 10000000)
        self.assertEqual(self.system.EL.p_Offset, -10000000)

    def test_parameter_command_axis_unknown_parameter_id(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        command = Command(
            ParameterCommand(1, 100),  # 100: unknown parameter id
            ParameterCommand(2, 100)
        )
        self._send(command.get())

        az_pcs = self.system.AZ.pcs
        el_pcs = self.system.EL.pcs

        self.assertEqual(az_pcs.counter, command.get_counter(0))
        self.assertEqual(az_pcs.command, 100)
        self.assertEqual(az_pcs.answer, 5)

        self.assertEqual(el_pcs.counter, command.get_counter(1))
        self.assertEqual(el_pcs.command, 100)
        self.assertEqual(el_pcs.answer, 5)

    def test_parameter_command_axis_not_active(self):
        command = Command(
            ParameterCommand(1, 11),
            ParameterCommand(2, 11)
        )
        self._send(command.get())

        az_pcs = self.system.AZ.pcs
        el_pcs = self.system.EL.pcs

        self.assertEqual(az_pcs.counter, command.get_counter(0))
        self.assertEqual(az_pcs.command, 11)
        self.assertEqual(az_pcs.answer, 4)

        self.assertEqual(el_pcs.counter, command.get_counter(1))
        self.assertEqual(el_pcs.command, 11)
        self.assertEqual(el_pcs.answer, 4)

    def test_parameter_command_time_source_acu_time(self):
        acu_time_mode = 1
        acu_time = Command(ParameterCommand(5, 50, acu_time_mode))

        self._send(acu_time.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, acu_time.get_counter(0))
        self.assertEqual(pcs.command, 50)
        self.assertEqual(pcs.answer, 1)

        self.assertEqual(self.system.PS.timeSource, acu_time_mode)

        now_min = datetime.utcnow() - timedelta(milliseconds=50)
        now_max = datetime.utcnow() + timedelta(milliseconds=50)

        ps_time = self.system.PS.actual_time()

        self.assertTrue(
            now_min <= ps_time <= now_max
        )

    def test_parameter_command_time_source_clock_time(self):
        clock_time_mode = 2
        clock_time = Command(ParameterCommand(5, 50, clock_time_mode))

        self._send(clock_time.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, clock_time.get_counter(0))
        self.assertEqual(pcs.command, 50)
        self.assertEqual(pcs.answer, 1)

        self.assertEqual(self.system.PS.timeSource, clock_time_mode)

    def test_parameter_command_time_source_external(self):
        offset = timedelta(days=1)
        new_time = datetime.utcnow() + offset
        external_time_mode = 3

        external_time = Command(
            ParameterCommand(5, 50, external_time_mode, utils.mjd(new_time))
        )

        self._send(external_time.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, external_time.get_counter(0))
        self.assertEqual(pcs.command, 50)
        self.assertEqual(pcs.answer, 1)

        self.assertEqual(self.system.PS.timeSource, external_time_mode)

        now_min = datetime.utcnow() + offset - timedelta(milliseconds=25)
        now_max = datetime.utcnow() + offset + timedelta(milliseconds=25)

        ps_time = self.system.PS.actual_time()

        self.assertTrue(
            now_min <= ps_time <= now_max
        )

    def test_parameter_command_time_source_unknown(self):
        unknown_time_source = Command(
            ParameterCommand(5, 50, 100)  # 100: unknown time source
        )

        self._send(unknown_time_source.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, unknown_time_source.get_counter(0))
        self.assertEqual(pcs.command, 50)
        self.assertEqual(pcs.answer, 5)  # 5: command has invalid parameters

    def test_parameter_command_time_offset_add_second(self):
        add_second = Command(ParameterCommand(5, 51, 1))

        self._send(add_second.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, add_second.get_counter(0))
        self.assertEqual(pcs.command, 51)
        self.assertEqual(pcs.answer, 1)

        self.assertEqual(self.system.PS.actTimeOffset, 1.1574074074074073e-05)

    def test_parameter_command_time_offset_subtract_second(self):
        subtract_second = Command(ParameterCommand(5, 51, 2))

        self._send(subtract_second.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, subtract_second.get_counter(0))
        self.assertEqual(pcs.command, 51)
        self.assertEqual(pcs.answer, 1)

        self.assertEqual(self.system.PS.actTimeOffset, -1.1574074074074073e-05)

    def test_parameter_command_time_offset_absolute(self):
        absolute_offset = Command(
            ParameterCommand(5, 51, 3, 100)
        )

        self._send(absolute_offset.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, absolute_offset.get_counter(0))
        self.assertEqual(pcs.command, 51)
        self.assertEqual(pcs.answer, 1)

    def test_parameter_command_time_offset_relative(self):
        self.test_parameter_command_time_offset_absolute()

        relative_offset = Command(
            ParameterCommand(5, 51, 4, 100)
        )

        self._send(relative_offset.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, relative_offset.get_counter(0))
        self.assertEqual(pcs.command, 51)
        self.assertEqual(pcs.answer, 1)

    def test_parameter_command_time_offset_out_of_range(self):
        out_of_range_offset = Command(
            ParameterCommand(5, 51, 3, 100000000)  # Max offset: 86400000
        )

        self._send(out_of_range_offset.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, out_of_range_offset.get_counter(0))
        self.assertEqual(pcs.command, 51)
        self.assertEqual(pcs.answer, 5)  # 5: command has invalid parameters

    def test_parameter_command_time_offset_unknown(self):
        unknown_time_offset = Command(
            ParameterCommand(5, 50, 100)  # 100: unknown time offset
        )

        self._send(unknown_time_offset.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, unknown_time_offset.get_counter(0))
        self.assertEqual(pcs.command, 50)
        self.assertEqual(pcs.answer, 5)  # 5: command has invalid parameters

    def test_parameter_command_pt_time_correction(self):
        # Load a new program track table
        self.test_program_track_command_load_new_table()

        # Correct program track start time by adding 5 seconds
        seconds = 5
        time_correction = Command(ParameterCommand(5, 60, seconds))

        self._send(time_correction.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, time_correction.get_counter(0))
        self.assertEqual(pcs.command, 60)
        self.assertEqual(pcs.answer, 1)

        self.assertEqual(self.system.PS.actPtTimeOffset, seconds * 1000)

    def test_parameter_command_pt_time_correction_out_of_range_offset(self):
        # Load a new program track table
        self.test_program_track_command_load_new_table()

        # Maximum correction absolute value: 86400000
        time_correction = Command(ParameterCommand(5, 60, 100000000))

        self._send(time_correction.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, time_correction.get_counter(0))
        self.assertEqual(pcs.command, 60)
        self.assertEqual(pcs.answer, 5)  # 5: command has invalid parameters

    def test_parameter_command_pointing_unknown_parameter_id(self):
        unknown_par_id = Command(ParameterCommand(5, 100))  # 100: unknown id

        self._send(unknown_par_id.get())

        pcs = self.system.PS.pcs
        self.assertEqual(pcs.counter, unknown_par_id.get_counter(0))
        self.assertEqual(pcs.command, 100)
        self.assertEqual(pcs.answer, 5)  # 5: command has invalid parameters

    def test_parameter_command_unknown_subsystem(self):
        with self.assertRaises(ValueError):
            self._send(Command(ParameterCommand(3, 1)).get())

    def test_program_track_command_load_new_table(self, start_time=None):
        if not start_time:
            start_time = datetime.utcnow() + timedelta(seconds=2)

        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=utils.mjd(start_time),
            axis_rates=(0.5, 0.5)
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=181,
            elevation_position=89
        )
        pt_command.add_entry(2000, 182, 88)
        pt_command.add_entry(4000, 181, 89)
        pt_command.add_entry(6000, 182, 88)
        pt_command.add_entry(8000, 183, 87)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Check if the command has been correctly received
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 1)

    def test_program_track_command_add_entries(self):
        start_time = datetime.utcnow() + timedelta(seconds=1)

        self.test_program_track_command_load_new_table(start_time)

        pt_command = ProgramTrackCommand(
            load_mode=2,
            start_time=utils.mjd(start_time),
            axis_rates=(1, 1)
        )
        entry = ProgramTrackEntry(
            relative_time=10000,
            azimuth_position=182,
            elevation_position=88
        )
        pt_command.append_entry(entry)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Check if the command has been correctly received and executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 1)

    def test_program_track_command_add_entries_during_execution(self):
        start_time = datetime.utcnow() + timedelta(seconds=1)

        self.test_program_track_command_load_new_table(start_time)

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(
            start_azimuth,
            start_elevation,
        )

        self._send(command.get())

        # Wait for execution to start
        time.sleep(2)

        pt_command = ProgramTrackCommand(
            load_mode=2,
            start_time=utils.mjd(start_time),
            axis_rates=(1, 1)
        )
        entry = ProgramTrackEntry(
            relative_time=10000,
            azimuth_position=184,
            elevation_position=88
        )
        pt_command.append_entry(entry)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Check if the command has been correctly received and executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 1)

        # Wait for execution to complete
        time.sleep(10)

        self.assertEqual(self.system.AZ.p_Ist, 184000000)
        self.assertEqual(self.system.EL.p_Ist, 88000000)

    def test_program_track_command_add_entries_wrong_start_time(self):
        start_time = datetime.utcnow() + timedelta(seconds=1)

        self.test_program_track_command_load_new_table(start_time)

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

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Check if the command has been received and not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

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
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)

        command = Command(pt_command)

        with self.assertRaises(ValueError):
            self._send(command.get())

    def test_program_track_wrong_parameter_id(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
            parameter_id=0,
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 0)
        self.assertEqual(pcs.answer, 0)

    def test_program_track_wrong_interpolation_mode(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
            interpolation_mode=0,
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_wrong_tracking_mode(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
            tracking_mode=0,
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_wrong_load_mode(self):
        pt_command = ProgramTrackCommand(
            load_mode=0,
            start_time=0,
            axis_rates=(1, 1),
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_too_short_sequence(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_too_long_sequence(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
        )

        for i in range(60):
            pt_command.add_entry(
                relative_time=i,
                azimuth_position=i,
                elevation_position=i
            )

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_wrong_first_relative_time(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
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
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_wrong_subsequent_relative_time(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_wrong_delta_time(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)

        command = Command(pt_command)
        self._send(command.get())

        command_counter = command.get_counter(0)
        pcs = self.system.PS.pcs

        # Make sure that command has been received but not executed
        self.assertEqual(pcs.counter, command_counter)
        self.assertEqual(pcs.command, 61)
        self.assertEqual(pcs.answer, 5)

    def test_program_track_wrong_sequence_length_short(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)
        pt_command.add_entry(6, 6, 6)

        command = Command(pt_command)

        command_string = command.get()
        command_string = (
            command_string[:32]
            + utils.uint_to_bytes(5, 2)
            + command_string[34:]
        )

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_program_track_wrong_sequence_length_long(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)
        pt_command.add_entry(6, 6, 6)

        command = Command(pt_command)

        command_string = command.get()
        command_string = (
            command_string[:32]
            + utils.uint_to_bytes(10, 2)
            + command_string[34:]
        )

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_wrong_program_track_plus_mode_command(self):
        pt_command = ProgramTrackCommand(
            load_mode=1,
            start_time=0,
            axis_rates=(1, 1),
        )
        pt_command.add_entry(
            relative_time=0,
            azimuth_position=0,
            elevation_position=0
        )
        pt_command.add_entry(1, 1, 1)
        pt_command.add_entry(2, 2, 2)
        pt_command.add_entry(3, 3, 3)
        pt_command.add_entry(4, 4, 4)
        pt_command.add_entry(5, 5, 5)
        pt_command.add_entry(6, 6, 6)

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(pt_command, start_azimuth, start_elevation)

        command_string = command.get()
        command_string = (
            command_string[:32]
            + utils.uint_to_bytes(8, 2)
            + command_string[34:]
        )

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_program_track_execution(self):
        self.test_program_track_command_load_new_table()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(
            start_azimuth,
            start_elevation,
        )

        self._send(command.get())

        time.sleep(11)

        self.assertEqual(self.system.AZ.p_Ist, 183000000)
        self.assertEqual(self.system.EL.p_Ist, 87000000)

    def test_program_track_execution_with_offset(self):
        self.test_program_track_command_load_new_table()
        self.test_parameter_command_pt_time_correction()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(
            start_azimuth,
            start_elevation,
        )

        self._send(command.get())

        time.sleep(5.8)

        # Make sure that program track is not started yet
        self.assertEqual(self.system.PS.ptState, 2)
        self.assertEqual(self.system.AZ.p_Ist, 181000000)
        self.assertEqual(self.system.EL.p_Ist, 89000000)

        # Wait for program track execution
        time.sleep(11.2)

        self.assertEqual(self.system.AZ.p_Ist, 183000000)
        self.assertEqual(self.system.EL.p_Ist, 87000000)

    def test_program_track_load_new_table_while_running(self):
        self.test_program_track_command_load_new_table()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(
            start_azimuth,
            start_elevation,
        )

        self._send(command.get())

        t0 = time.time()
        # Wait for the pointing subsystem to start tracking
        while self.system.PS.ptState != 3:
            if time.time() - t0 >= 5:
                self.fail('Test is taking too long to complete.')
            time.sleep(0.01)

        # Let the tracking execute for 0.2 seconds
        time.sleep(0.2)

        # Send the new table
        self.test_program_track_command_load_new_table()

        azimuth = self.system.AZ
        elevation = self.system.EL

        while True:
            az_pos = False
            el_pos = False
            az_vel = False
            el_vel = False

            if azimuth.p_Ist == 181000000:
                az_pos = True
            if elevation.p_Ist == 89000000:
                el_pos = True
            if azimuth.v_Ist == 0:
                az_vel = True
            if elevation.v_Ist == 0:
                el_vel = True

            if self.system.PS.ptState == 2:
                if az_pos and el_pos and az_vel and el_vel:
                    break

            if time.time() - t0 >= 5:
                self.fail('Test is taking too long to complete.')
            time.sleep(0.01)

        # Make sure both axis stopped in the first position of the new sequence
        # and they are waiting to start tracking
        self.assertEqual(self.system.AZ.v_Ist, 0)
        self.assertEqual(self.system.EL.v_Ist, 0)
        self.assertEqual(self.system.AZ.p_Ist, 181000000)
        self.assertEqual(self.system.EL.p_Ist, 89000000)

        # Now wait for the tracking to start again
        while self.system.PS.ptState != 3:
            if time.time() - t0 >= 5:
                self.fail('Test is taking too long to complete.')
            time.sleep(0.01)

    def test_program_track_load_new_table_while_positioning(self):
        self.test_program_track_command_load_new_table()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(
            start_azimuth,
            start_elevation,
        )

        self._send(command.get())

        time.sleep(1.25)

        self.test_program_track_command_load_new_table()

        time.sleep(1.25)

        # Make sure both axis stopped in the program track first position
        self.assertEqual(self.system.AZ.p_Ist, 181000000)
        self.assertEqual(self.system.EL.p_Ist, 89000000)
        self.assertEqual(self.system.AZ.v_Ist, 0)
        self.assertEqual(self.system.EL.v_Ist, 0)

        time.sleep(1)

        # Make sure the tracking started
        self.assertNotEqual(self.system.AZ.p_Ist, 181000000)
        self.assertNotEqual(self.system.EL.p_Ist, 89000000)
        self.assertNotEqual(self.system.AZ.v_Ist, 0)
        self.assertNotEqual(self.system.EL.v_Ist, 0)

    def test_program_track_stop_positioning(self):
        self.test_program_track_command_load_new_table()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(
            start_azimuth,
            start_elevation,
        )

        self._send(command.get())

        time.sleep(0.5)

        self.test_mode_command_stop(activate=False)

        time.sleep(9.5)

        self.assertNotEqual(self.system.AZ.p_Ist, 183000000)
        self.assertNotEqual(self.system.EL.p_Ist, 87000000)

    def test_program_track_stop_tracking(self):
        self.test_program_track_command_load_new_table()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 0.5)
        start_elevation = ModeCommand(2, 8, None, 0.5)

        command = Command(
            start_azimuth,
            start_elevation,
        )

        self._send(command.get())

        time.sleep(5)

        self.test_mode_command_stop(activate=False)

        time.sleep(5)

        self.assertNotEqual(self.system.AZ.p_Ist, 183000000)
        self.assertNotEqual(self.system.EL.p_Ist, 87000000)

    def test_program_track_out_of_range_rate(self):
        self.test_program_track_command_load_new_table()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        start_azimuth = ModeCommand(1, 8, None, 1.5)
        start_elevation = ModeCommand(2, 8, None, 1.5)

        command = Command(
            start_azimuth,
            start_elevation
        )

        self._send(command.get())

        az_command_counter = command.get_counter(-2)
        el_command_counter = command.get_counter(-1)

        az_mcs = self.system.AZ.mcs
        el_mcs = self.system.EL.mcs

        # Make sure that command has been received with wrong parameters
        self.assertEqual(az_mcs.received.counter, az_command_counter)
        self.assertEqual(az_mcs.received.command, 8)
        self.assertEqual(az_mcs.received.answer, 5)

        # Make sure that command has been received with wrong parameters
        self.assertEqual(el_mcs.received.counter, el_command_counter)
        self.assertEqual(el_mcs.received.command, 8)
        self.assertEqual(el_mcs.received.answer, 5)

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

    def test_utils_macro_command_append(self):
        command = Command()
        command.append(ModeCommand(1, 1))

        with self.assertRaises(ValueError):
            command.append('dummy')

    def test_utils_get_command_counter(self):
        command = Command(ModeCommand(1, 1))
        command.get()
        command.get_counter()

        with self.assertRaises(ValueError):
            command.get_counter(5)

        with self.assertRaises(ValueError):
            command.get_counter(-5)


if __name__ == '__main__':
    unittest.main()
