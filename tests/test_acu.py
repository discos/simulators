import unittest
import time
import socket
from datetime import datetime, timedelta, timezone
from simulators import acu
from simulators import utils
from simulators.acu.acu_utils import (
    Command,
    ModeCommand,
    ParameterCommand,
    ProgramTrackCommand,
    ProgramTrackEntry
)
from simulators.server import Simulator


class TestACUUtils(unittest.TestCase):

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


class TestACU(unittest.TestCase):

    def setUp(self):
        self.system = acu.System()

    def tearDown(self):
        del self.system

    def _send(self, message):
        for byte in message:
            self.assertTrue(self.system.parse(byte))
        # Wait for command to start its execution
        time.sleep(0.01)

    def test_status_message_length(self):
        status = bytes(self.system.status)
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

        # Check if the command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, 0)  # 0: _ignore
        self.assertEqual(self.system.AZ.received_mode_command_answer, 0)

        # Make sure the command has not been executed
        self.assertEqual(self.system.AZ.executed_mode_command_counter, 0)
        self.assertEqual(self.system.AZ.executed_mode_command, 0)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 0)

    def test_mode_command_inactive(self):
        mode_id = 1  # 1: inactive
        az = ModeCommand(1, mode_id)  # 1: azimuth subsystem
        el = ModeCommand(2, mode_id)  # 2: elevation subsystem
        command = Command(az, el)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, mode_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

    def test_mode_command_active(self):
        mode_id = 2  # 2: active
        az = ModeCommand(1, mode_id)
        el = ModeCommand(2, mode_id)
        command = Command(az, el)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, mode_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

    def test_mode_command_wrong_state_active(self):
        self.test_mode_command_active()

        mode_id = 2  # 2: active
        az = ModeCommand(1, mode_id)
        el = ModeCommand(2, mode_id)
        command = Command(az, el)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 4)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 4)

    def test_mode_command_without_activate(self):
        stop_id = 7  # Cannot stop a non-active axis
        az_stop = ModeCommand(1, stop_id)
        el_stop = ModeCommand(2, stop_id)

        command = Command(az_stop, el_stop)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, stop_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 4)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, stop_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 4)

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
        el_command_counter = command.get_counter(-1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, preset_abs_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, preset_abs_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Should be both in position in ~1 seconds but we give it 2 to be sure
        time.sleep(2)

        az_res_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        self.assertEqual(az_res_pos, az_des_pos)
        el_res_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)
        self.assertEqual(el_res_pos, el_des_pos)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, preset_abs_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, preset_abs_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

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
        el_command_counter = command.get_counter(-1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, preset_abs_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, preset_abs_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

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
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, preset_abs_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, preset_abs_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

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
        el_command_counter = command.get_counter(-1)

        # Check if the azimuth command has been received with wrong params
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, preset_abs_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 5)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, preset_abs_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 5)

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
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, pres_rel_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, pres_rel_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Check if azimuth command has started the execution
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, pres_rel_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 2)

        # Check if elevation command has started the execution
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, pres_rel_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 2)

        # Should be in position in ~1 seconds but we give it 2 to be sure
        time.sleep(2)

        az_res_pos = round(float(self.system.AZ.p_Ist) / 1000000, 2)
        self.assertEqual(az_res_pos, az_start_pos + az_des_delta)

        el_res_pos = round(float(self.system.EL.p_Ist) / 1000000, 2)
        self.assertEqual(el_res_pos, el_start_pos + el_des_delta)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, pres_rel_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, pres_rel_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

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
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received with wrong params
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, pres_rel_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 5)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, pres_rel_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 5)

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
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, slew_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, slew_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Check if azimuth command has started the execution
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, slew_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 2)

        # Check if elevation command has started the execution
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, slew_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 2)

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
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, slew_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, slew_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, slew_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, slew_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

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
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received with wrong params
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, slew_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 5)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, slew_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 5)

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
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, stop_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, stop_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, stop_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, stop_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

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
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(
            self.system.AZ.received_mode_command, program_track_id
        )
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(
            self.system.EL.received_mode_command, program_track_id
        )
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(
            self.system.AZ.executed_mode_command, program_track_id
        )
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(
            self.system.EL.executed_mode_command, program_track_id
        )
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

    def test_mode_command_interlock(self):
        mode_id = 14  # 14: interlock
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, mode_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

    def test_mode_command_reset(self):
        mode_id = 15  # 15: reset
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, mode_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

    def test_mode_command_stow(self):
        mode_id = 50  # 50: stow
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received in wrong mode
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 4)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

    def test_mode_command_stow_wrong_position(self):
        self.test_mode_command_preset_absolute()

        mode_id = 50  # 50: stow
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received in wrong mode
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 4)

        # Check if the elevation command has been received in wrong mode
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 4)

    def test_mode_command_unstow(self):
        mode_id = 51  # 51: unstow
        command = Command(ModeCommand(1, mode_id), ModeCommand(2, mode_id))
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, mode_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

        # Make sure both axis are now unstowed
        self.assertFalse(self.system.AZ.stowed)
        self.assertFalse(self.system.EL.stowed)

    def test_mode_command_drive_to_stow(self):
        self.test_mode_command_preset_absolute()

        mode_id = 52  # 52: drive_to_stow
        az_drive_to_stow = ModeCommand(1, mode_id, None, 0.42)
        el_drive_to_stow = ModeCommand(2, mode_id, None, 0.25)

        command = Command(az_drive_to_stow, el_drive_to_stow)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed (no stow pos)
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, mode_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Check if elevation command has started the execution
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 2)

        time.sleep(2)

        # Make sure the elevation command has been executed
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 1)

    def test_mode_command_drive_to_stow_stop(self):
        self.test_mode_command_preset_absolute()

        mode_id = 52  # 52: drive_to_stow
        az_drive_to_stow = ModeCommand(1, mode_id, None, 0.42)
        el_drive_to_stow = ModeCommand(2, mode_id, None, 0.25)

        command = Command(az_drive_to_stow, el_drive_to_stow)
        self._send(command.get())

        az_command_counter = command.get_counter(0)
        el_command_counter = command.get_counter(1)

        # Check if the azimuth command has been received
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 9)

        # Make sure the azimuth command has been executed (no stow pos)
        self.assertEqual(
            self.system.AZ.executed_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.executed_mode_command, mode_id)
        self.assertEqual(self.system.AZ.executed_mode_command_answer, 1)

        # Check if elevation command has started the execution
        self.assertEqual(
            self.system.EL.executed_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.executed_mode_command, mode_id)
        self.assertEqual(self.system.EL.executed_mode_command_answer, 2)

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

        # Check if the azimuth command has been received (no stow_pos)
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, mode_id)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 9)

        # Check if the elevation command has been received with wrong params
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, mode_id)
        self.assertEqual(self.system.EL.received_mode_command_answer, 5)

    def test_parameter_command_absolute_position_offset(self):
        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        command = Command(
            ParameterCommand(1, 11, 5, 0),
            ParameterCommand(2, 11, -5, 0)
        )
        self._send(command.get())

        self.assertEqual(
            self.system.AZ.parameter_command_counter, command.get_counter(0)
        )
        self.assertEqual(self.system.AZ.parameter_command, 11)
        self.assertEqual(self.system.AZ.parameter_command_answer, 1)

        self.assertEqual(
            self.system.EL.parameter_command_counter, command.get_counter(1)
        )
        self.assertEqual(self.system.EL.parameter_command, 11)
        self.assertEqual(self.system.EL.parameter_command_answer, 1)

        self.assertEqual(self.system.AZ.p_Offset, 5000000)
        self.assertEqual(self.system.EL.p_Offset, -5000000)

    def test_parameter_command_relative_position_offset(self):
        self.test_parameter_command_absolute_position_offset()

        command = Command(
            ParameterCommand(1, 12, 5, 0),
            ParameterCommand(2, 12, -5, 0)
        )
        self._send(command.get())

        self.assertEqual(
            self.system.AZ.parameter_command_counter, command.get_counter(0)
        )
        self.assertEqual(self.system.AZ.parameter_command, 12)
        self.assertEqual(self.system.AZ.parameter_command_answer, 1)

        self.assertEqual(
            self.system.EL.parameter_command_counter, command.get_counter(1)
        )
        self.assertEqual(self.system.EL.parameter_command, 12)
        self.assertEqual(self.system.EL.parameter_command_answer, 1)

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

        self.assertEqual(
            self.system.AZ.parameter_command_counter, command.get_counter(0)
        )
        self.assertEqual(self.system.AZ.parameter_command, 100)
        self.assertEqual(self.system.AZ.parameter_command_answer, 5)

        self.assertEqual(
            self.system.EL.parameter_command_counter, command.get_counter(1)
        )
        self.assertEqual(self.system.EL.parameter_command, 100)
        self.assertEqual(self.system.EL.parameter_command_answer, 5)

    def test_parameter_command_axis_not_active(self):
        command = Command(
            ParameterCommand(1, 11),
            ParameterCommand(2, 11)
        )
        self._send(command.get())

        self.assertEqual(
            self.system.AZ.parameter_command_counter, command.get_counter(0)
        )
        self.assertEqual(self.system.AZ.parameter_command, 11)
        self.assertEqual(self.system.AZ.parameter_command_answer, 4)

        self.assertEqual(
            self.system.EL.parameter_command_counter, command.get_counter(1)
        )
        self.assertEqual(self.system.EL.parameter_command, 11)
        self.assertEqual(self.system.EL.parameter_command_answer, 4)

    def test_parameter_command_time_source_acu_time(self):
        acu_time_mode = 1
        acu_time = Command(ParameterCommand(5, 50, acu_time_mode))

        self._send(acu_time.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, acu_time.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 50)
        self.assertEqual(ps.parameter_command_answer, 1)

        self.assertEqual(self.system.PS.timeSource, acu_time_mode)

        now_min = datetime.now(timezone.utc) - timedelta(milliseconds=50)
        now_max = datetime.now(timezone.utc) + timedelta(milliseconds=50)

        ps_time = self.system.PS.actual_time()

        self.assertTrue(
            now_min <= ps_time <= now_max
        )

    def test_parameter_command_time_source_clock_time(self):
        clock_time_mode = 2
        clock_time = Command(ParameterCommand(5, 50, clock_time_mode))

        self._send(clock_time.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, clock_time.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 50)
        self.assertEqual(ps.parameter_command_answer, 1)

        self.assertEqual(self.system.PS.timeSource, clock_time_mode)

    def test_parameter_command_time_source_external(self):
        offset = timedelta(days=1)
        new_time = datetime.now(timezone.utc) + offset
        external_time_mode = 3

        external_time = Command(
            ParameterCommand(5, 50, external_time_mode, utils.mjd(new_time))
        )

        self._send(external_time.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, external_time.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 50)
        self.assertEqual(ps.parameter_command_answer, 1)

        self.assertEqual(self.system.PS.timeSource, external_time_mode)

        now_min = \
            datetime.now(timezone.utc) + offset - timedelta(milliseconds=25)
        now_max = \
            datetime.now(timezone.utc) + offset + timedelta(milliseconds=25)

        ps_time = self.system.PS.actual_time()

        self.assertTrue(
            now_min <= ps_time <= now_max
        )

    def test_parameter_command_time_source_unknown(self):
        unknown_time_source = Command(
            ParameterCommand(5, 50, 100)  # 100: unknown time source
        )

        self._send(unknown_time_source.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, unknown_time_source.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 50)
        self.assertEqual(ps.parameter_command_answer, 5)
        # 5: command has invalid parameters

    def test_parameter_command_time_offset_add_second(self):
        add_second = Command(ParameterCommand(5, 51, 1))

        self._send(add_second.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, add_second.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 51)
        self.assertEqual(ps.parameter_command_answer, 1)

        self.assertEqual(self.system.PS.actTimeOffset, 1.1574074074074073e-05)

    def test_parameter_command_time_offset_subtract_second(self):
        subtract_second = Command(ParameterCommand(5, 51, 2))

        self._send(subtract_second.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, subtract_second.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 51)
        self.assertEqual(ps.parameter_command_answer, 1)

        self.assertEqual(self.system.PS.actTimeOffset, -1.1574074074074073e-05)

    def test_parameter_command_time_offset_absolute(self):
        absolute_offset = Command(
            ParameterCommand(5, 51, 3, 100)
        )

        self._send(absolute_offset.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, absolute_offset.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 51)
        self.assertEqual(ps.parameter_command_answer, 1)

    def test_parameter_command_time_offset_relative(self):
        self.test_parameter_command_time_offset_absolute()

        relative_offset = Command(
            ParameterCommand(5, 51, 4, 100)
        )

        self._send(relative_offset.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, relative_offset.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 51)
        self.assertEqual(ps.parameter_command_answer, 1)

    def test_parameter_command_time_offset_out_of_range(self):
        out_of_range_offset = Command(
            ParameterCommand(5, 51, 3, 100000000)  # Max offset: 86400000
        )

        self._send(out_of_range_offset.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, out_of_range_offset.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 51)
        self.assertEqual(ps.parameter_command_answer, 5)
        # 5: command has invalid parameters

    def test_parameter_command_time_offset_unknown(self):
        unknown_time_offset = Command(
            ParameterCommand(5, 50, 100)  # 100: unknown time offset
        )

        self._send(unknown_time_offset.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, unknown_time_offset.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 50)
        self.assertEqual(ps.parameter_command_answer, 5)
        # 5: command has invalid parameters

    def test_parameter_command_pt_time_correction(self):
        # Load a new program track table
        self.test_program_track_command_load_new_table()

        # Correct program track start time by adding 5 seconds
        seconds = 5
        time_correction = Command(ParameterCommand(5, 60, seconds))

        self._send(time_correction.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, time_correction.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 60)
        self.assertEqual(ps.parameter_command_answer, 1)

        self.assertEqual(self.system.PS.actPtTimeOffset, seconds * 1000)

    def test_parameter_command_pt_time_correction_out_of_range_offset(self):
        # Load a new program track table
        self.test_program_track_command_load_new_table()

        # Maximum correction absolute value: 86400000
        time_correction = Command(ParameterCommand(5, 60, 100000000))

        self._send(time_correction.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, time_correction.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 60)
        self.assertEqual(ps.parameter_command_answer, 5)
        # 5: command has invalid parameters

    def test_parameter_command_pointing_unknown_parameter_id(self):
        unknown_par_id = Command(ParameterCommand(5, 100))  # 100: unknown id

        self._send(unknown_par_id.get())

        ps = self.system.PS
        self.assertEqual(
            ps.parameter_command_counter, unknown_par_id.get_counter(0)
        )
        self.assertEqual(ps.parameter_command, 100)
        self.assertEqual(ps.parameter_command_answer, 5)
        # 5: command has invalid parameters

    def test_parameter_command_unknown_subsystem(self):
        with self.assertRaises(ValueError):
            self._send(Command(ParameterCommand(3, 1)).get())

    def test_program_track_command_load_new_table(self, start_time=None):
        if not start_time:
            start_time = datetime.now(timezone.utc) + timedelta(seconds=2)

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
        ps = self.system.PS

        # Check if the command has been correctly received
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 1)

    def test_program_track_command_add_entries(self):
        start_time = datetime.now(timezone.utc) + timedelta(seconds=1)

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
        ps = self.system.PS

        # Check if the command has been correctly received and executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 1)

    def test_program_track_command_add_entries_during_execution(self):
        start_time = datetime.now(timezone.utc) + timedelta(seconds=1)

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
        ps = self.system.PS

        # Check if the command has been correctly received and executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 1)

        # Wait for execution to complete
        time.sleep(10)

        self.assertEqual(self.system.AZ.p_Ist, 184000000)
        self.assertEqual(self.system.EL.p_Ist, 88000000)

    def test_program_track_command_add_entries_wrong_start_time(self):
        start_time = datetime.now(timezone.utc) + timedelta(seconds=1)

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
        ps = self.system.PS

        # Check if the command has been received and not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 0)
        self.assertEqual(ps.parameter_command_answer, 0)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
        ps = self.system.PS

        # Make sure that command has been received but not executed
        self.assertEqual(ps.parameter_command_counter, command_counter)
        self.assertEqual(ps.parameter_command, 61)
        self.assertEqual(ps.parameter_command_answer, 5)

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
            + utils.uint_to_string(5, 2)
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
            + utils.uint_to_string(10, 2)
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
            + utils.uint_to_string(8, 2)
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

    def test_program_track_execution_repeated(self):
        self.test_program_track_command_load_new_table()

        # Axis needs to be unstowed and activated before sending this command
        self.test_mode_command_unstow()
        self.test_mode_command_active()

        for _ in range(2):
            start_azimuth = ModeCommand(1, 8, None, 0.5)
            start_elevation = ModeCommand(2, 8, None, 0.5)
            command = Command(
                start_azimuth,
                start_elevation,
            )
            self._send(command.get())
            time.sleep(5)

        time.sleep(1)

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

        azimuth = self.system.AZ
        elevation = self.system.EL

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

        # Make sure that command has been received with wrong parameters
        self.assertEqual(
            self.system.AZ.received_mode_command_counter, az_command_counter
        )
        self.assertEqual(self.system.AZ.received_mode_command, 8)
        self.assertEqual(self.system.AZ.received_mode_command_answer, 5)

        # Make sure that command has been received with wrong parameters
        self.assertEqual(
            self.system.EL.received_mode_command_counter, el_command_counter
        )
        self.assertEqual(self.system.EL.received_mode_command, 8)
        self.assertEqual(self.system.EL.received_mode_command_answer, 5)

    def test_multiple_commands_wrong_count(self):
        command_1 = ModeCommand(1, 1)
        command_2 = ParameterCommand(2, 2)

        command_string = Command(command_1, command_2).get()

        command_string = (
            command_string[:12]
            + utils.uint_to_string(3)
            + command_string[16:]
        )

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_unknown_command(self):
        command_string = Command(ModeCommand(1, 1)).get()

        # Change the command id with an unknown one
        command_string = (
            command_string[:16]
            + utils.uint_to_string(3, 2)
            + command_string[18:]
        )

        with self.assertRaises(ValueError):
            self._send(command_string)

    def test_pre_limits_down(self):
        self.system.AZ.p_Ist = int(round(self.system.AZ.min_pos * 1000000))
        self.system.EL.p_Ist = int(round(self.system.EL.min_pos * 1000000))
        time.sleep(0.1)
        self.assertTrue(self.system.AZ.Pre_Limit_Dn)
        self.assertTrue(self.system.EL.Pre_Limit_Dn)
        self.assertFalse(self.system.AZ.Fin_Limit_Dn)
        self.assertFalse(self.system.EL.Fin_Limit_Dn)

    def test_pre_limits_up(self):
        self.system.AZ.p_Ist = int(round(self.system.AZ.max_pos * 1000000))
        self.system.EL.p_Ist = int(round(self.system.EL.max_pos * 1000000))
        time.sleep(0.1)
        self.assertTrue(self.system.AZ.Pre_Limit_Up)
        self.assertTrue(self.system.EL.Pre_Limit_Up)
        self.assertFalse(self.system.AZ.Fin_Limit_Up)
        self.assertFalse(self.system.EL.Fin_Limit_Up)

    def test_final_limits_down(self):
        self.system.AZ.p_Ist = int(round(self.system.AZ.min_pos * 1000000)) - 1
        self.system.EL.p_Ist = int(round(self.system.EL.min_pos * 1000000)) - 1
        time.sleep(0.1)
        self.assertTrue(self.system.AZ.Pre_Limit_Dn)
        self.assertTrue(self.system.EL.Pre_Limit_Dn)
        self.assertTrue(self.system.AZ.Fin_Limit_Dn)
        self.assertTrue(self.system.EL.Fin_Limit_Dn)

    def test_final_limits_up(self):
        self.system.AZ.p_Ist = int(round(self.system.AZ.max_pos * 1000000)) + 1
        self.system.EL.p_Ist = int(round(self.system.EL.max_pos * 1000000)) + 1
        time.sleep(0.1)
        self.assertTrue(self.system.AZ.Pre_Limit_Up)
        self.assertTrue(self.system.EL.Pre_Limit_Up)
        self.assertTrue(self.system.AZ.Fin_Limit_Up)
        self.assertTrue(self.system.EL.Fin_Limit_Up)

    def test_exceeded_rate(self):
        self.system.AZ.v_Ist = \
            int(round(self.system.AZ.max_velocity * 1000000)) + 1
        self.system.EL.v_Ist = \
            int(round(self.system.EL.max_velocity * 1000000)) + 1
        time.sleep(0.1)
        self.assertTrue(self.system.AZ.Rate_Limit)
        self.assertTrue(self.system.EL.Rate_Limit)


class TestACUSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start_flag = b'\x1A\xCF\xFC\x1D'
        cls.end_flag = b'\xD1\xCF\xFC\xA1'
        cls.simulator = Simulator('acu')
        cls.simulator.start(daemon=True)

    @classmethod
    def tearDownClass(cls):
        cls.simulator.stop()

    def test_different_statuses(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 13001))
        prev = ''
        for _ in range(5):
            status = s.recv(1024)
            self.assertEqual(len(status), 813)
            self.assertEqual(status[0:4], self.start_flag)
            self.assertEqual(status[-4:], self.end_flag)
            self.assertNotEqual(prev, status)
            prev = status
            time.sleep(acu.System.default_sampling_time)
        s.close()

    def test_multiple_clients(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect(('127.0.0.1', 13001))
        s2.connect(('127.0.0.1', 13001))

        status1 = s1.recv(1024)
        status2 = s2.recv(1024)
        self.assertEqual(status1, status2)

        s1.close()
        time.sleep(0.5)
        s2.close()


class TestACUValues(unittest.TestCase):

    def setUp(self):
        system = acu.System()
        self.GS = system.GS
        self.AS = system.AZ
        self.MS = system.AZ.motor_status[0]
        self.PS = system.PS
        self.FS = system.FS

    def test_gs_values(self):
        self.assertIsInstance(self.GS.version, tuple)
        self.assertIsInstance(self.GS.master, int)
        self.assertIsInstance(self.GS.status_HMI, list)
        self.assertIsInstance(self.GS.software_IO, bool)
        self.assertIsInstance(self.GS.simulation, bool)
        self.assertIsInstance(self.GS.control_system_on, bool)
        self.assertIsInstance(self.GS.service, bool)

        self.assertIsInstance(self.GS.HW_interlock, str)
        self.assertIsInstance(self.GS.EStop_Device, bool)
        self.assertIsInstance(self.GS.ES_SP, bool)
        self.assertIsInstance(self.GS.ES_Drive_AZ1_2, bool)
        self.assertIsInstance(self.GS.ES_Drive_AZ3_4, bool)
        self.assertIsInstance(self.GS.ES_Drive_AZ5_6, bool)
        self.assertIsInstance(self.GS.ES_Drive_AZ7_8, bool)
        self.assertIsInstance(self.GS.ES_Drive_EL1_2, bool)
        self.assertIsInstance(self.GS.ES_Drive_EL3_4, bool)
        self.assertIsInstance(self.GS.ES_LCP, bool)
        self.assertIsInstance(self.GS.ES_Cablewrap, bool)
        self.assertIsInstance(self.GS.ES_AER1, bool)
        self.assertIsInstance(self.GS.ES_AER2, bool)
        self.assertIsInstance(self.GS.ES_HHP, bool)
        self.assertIsInstance(self.GS.ES_PCP, bool)
        self.assertIsInstance(self.GS.ES_EER, bool)
        self.assertIsInstance(self.GS.ES_EER_Key, bool)
        self.assertIsInstance(self.GS.ES_EER_Door, bool)
        self.assertIsInstance(self.GS.ES_BOX_10, bool)
        self.assertIsInstance(self.GS.ES_SFR_1, bool)
        self.assertIsInstance(self.GS.ES_SFR_2, bool)

        self.assertIsInstance(self.GS.SW_interlock, str)
        self.assertIsInstance(self.GS.Control_System_Off, bool)
        self.assertIsInstance(self.GS.Power_Control_Sys, bool)
        self.assertIsInstance(self.GS.Power_Drive_Cab, bool)
        self.assertIsInstance(self.GS.Power_Supply_DC, bool)
        self.assertIsInstance(self.GS.Fieldbus_Error, bool)
        self.assertIsInstance(self.GS.Interlock_Cmd, bool)
        self.assertIsInstance(self.GS.SaDev_ES_FbErr, bool)
        self.assertIsInstance(self.GS.SaDev_ES_CommErr, bool)
        self.assertIsInstance(self.GS.SaDev_ES_OutErr, bool)
        self.assertIsInstance(self.GS.SaDev_MD_FbErr, bool)
        self.assertIsInstance(self.GS.SaDev_MD_CommErr, bool)
        self.assertIsInstance(self.GS.SaDev_MD_OutErr, bool)
        self.assertIsInstance(self.GS.Emergency_Stop, bool)
        self.assertIsInstance(self.GS.Power_UPS, bool)
        self.assertIsInstance(self.GS.Power_UPS_Alarm, bool)
        self.assertIsInstance(self.GS.ACU_DI_Power, bool)
        self.assertIsInstance(self.GS.ECU_DI_Power, bool)
        self.assertIsInstance(self.GS.Power_DO_Int, bool)
        self.assertIsInstance(self.GS.Main_Power, bool)
        self.assertIsInstance(self.GS.Overvoltage_Prot, bool)
        self.assertIsInstance(self.GS.Temp_Error_Rack, bool)

        self.assertIsInstance(self.GS.diag_signal, float)

    def test_gs_wrong_values(self):
        with self.assertRaises(ValueError):
            self.GS.version = None
        with self.assertRaises(ValueError):
            self.GS.master = None
        with self.assertRaises(ValueError):
            self.GS.status_HMI = None
        with self.assertRaises(ValueError):
            self.GS.status_HMI = ['0' for _ in range(6)]
        with self.assertRaises(ValueError):
            self.GS.software_IO = None
        with self.assertRaises(ValueError):
            self.GS.simulation = None
        with self.assertRaises(ValueError):
            self.GS.control_system_on = None
        with self.assertRaises(ValueError):
            self.GS.service = None

        with self.assertRaises(AttributeError):
            self.GS.HW_interlock = None
        with self.assertRaises(ValueError):
            self.GS.EStop_Device = None
        with self.assertRaises(ValueError):
            self.GS.ES_SP = None
        with self.assertRaises(ValueError):
            self.GS.ES_Drive_AZ1_2 = None
        with self.assertRaises(ValueError):
            self.GS.ES_Drive_AZ3_4 = None
        with self.assertRaises(ValueError):
            self.GS.ES_Drive_AZ5_6 = None
        with self.assertRaises(ValueError):
            self.GS.ES_Drive_AZ7_8 = None
        with self.assertRaises(ValueError):
            self.GS.ES_Drive_EL1_2 = None
        with self.assertRaises(ValueError):
            self.GS.ES_Drive_EL3_4 = None
        with self.assertRaises(ValueError):
            self.GS.ES_LCP = None
        with self.assertRaises(ValueError):
            self.GS.ES_Cablewrap = None
        with self.assertRaises(ValueError):
            self.GS.ES_AER1 = None
        with self.assertRaises(ValueError):
            self.GS.ES_AER2 = None
        with self.assertRaises(ValueError):
            self.GS.ES_HHP = None
        with self.assertRaises(ValueError):
            self.GS.ES_PCP = None
        with self.assertRaises(ValueError):
            self.GS.ES_EER = None
        with self.assertRaises(ValueError):
            self.GS.ES_EER_Key = None
        with self.assertRaises(ValueError):
            self.GS.ES_EER_Door = None
        with self.assertRaises(ValueError):
            self.GS.ES_BOX_10 = None
        with self.assertRaises(ValueError):
            self.GS.ES_SFR_1 = None
        with self.assertRaises(ValueError):
            self.GS.ES_SFR_2 = None

        with self.assertRaises(AttributeError):
            self.GS.SW_interlock = None
        with self.assertRaises(ValueError):
            self.GS.Control_System_Off = None
        with self.assertRaises(ValueError):
            self.GS.Power_Control_Sys = None
        with self.assertRaises(ValueError):
            self.GS.Power_Drive_Cab = None
        with self.assertRaises(ValueError):
            self.GS.Power_Supply_DC = None
        with self.assertRaises(ValueError):
            self.GS.Fieldbus_Error = None
        with self.assertRaises(ValueError):
            self.GS.Interlock_Cmd = None
        with self.assertRaises(ValueError):
            self.GS.SaDev_ES_FbErr = None
        with self.assertRaises(ValueError):
            self.GS.SaDev_ES_CommErr = None
        with self.assertRaises(ValueError):
            self.GS.SaDev_ES_OutErr = None
        with self.assertRaises(ValueError):
            self.GS.SaDev_MD_FbErr = None
        with self.assertRaises(ValueError):
            self.GS.SaDev_MD_CommErr = None
        with self.assertRaises(ValueError):
            self.GS.SaDev_MD_OutErr = None
        with self.assertRaises(ValueError):
            self.GS.Emergency_Stop = None
        with self.assertRaises(ValueError):
            self.GS.Power_UPS = None
        with self.assertRaises(ValueError):
            self.GS.Power_UPS_Alarm = None
        with self.assertRaises(ValueError):
            self.GS.ACU_DI_Power = None
        with self.assertRaises(ValueError):
            self.GS.ECU_DI_Power = None
        with self.assertRaises(ValueError):
            self.GS.Power_DO_Int = None
        with self.assertRaises(ValueError):
            self.GS.Main_Power = None
        with self.assertRaises(ValueError):
            self.GS.Overvoltage_Prot = None
        with self.assertRaises(ValueError):
            self.GS.Temp_Error_Rack = None

        with self.assertRaises(ValueError):
            self.GS.diag_signal = None

    def test_as_values(self):
        self.assertIsInstance(self.AS.simulation, bool)
        self.assertIsInstance(self.AS.axis_ready, bool)
        self.assertIsInstance(self.AS.confOk, bool)
        self.assertIsInstance(self.AS.initOk, bool)
        self.assertIsInstance(self.AS.override, bool)
        self.assertIsInstance(self.AS.low_power_mode, bool)

        self.assertIsInstance(self.AS.warnings, str)
        self.assertIsInstance(self.AS.Param_Fault, bool)
        self.assertIsInstance(self.AS.Rate_Mode, bool)
        self.assertIsInstance(self.AS.Safety_Chain, bool)
        self.assertIsInstance(self.AS.Wrong_Sys_State, bool)
        self.assertIsInstance(self.AS.Temp_Enc, bool)
        self.assertIsInstance(self.AS.Power_Brakes, bool)
        self.assertIsInstance(self.AS.Power_Servo, bool)
        self.assertIsInstance(self.AS.Fan_Fault, bool)
        self.assertIsInstance(self.AS.Servo_DC_Off, bool)
        self.assertIsInstance(self.AS.Motor_Temp_Warn, bool)
        self.assertIsInstance(self.AS.Servo_DC_Warn, bool)
        self.assertIsInstance(self.AS.M_Max_Exceeded, bool)
        self.assertIsInstance(self.AS.Pos_Enc_Fault, bool)
        self.assertIsInstance(self.AS.Em_Limit_Dn, bool)
        self.assertIsInstance(self.AS.Em_Limit_Up, bool)
        self.assertIsInstance(self.AS.Degraded_Mode, bool)
        self.assertIsInstance(self.AS.Override_Act, bool)
        self.assertIsInstance(self.AS.Pre_Limit_Up, bool)
        self.assertIsInstance(self.AS.Pre_Limit_Dn, bool)
        self.assertIsInstance(self.AS.Fin_Limit_Up, bool)
        self.assertIsInstance(self.AS.Fin_Limit_Dn, bool)
        self.assertIsInstance(self.AS.Rate_Limit, bool)
        self.assertIsInstance(self.AS.Stow_Fault, bool)
        self.assertIsInstance(self.AS.Stowpins_Extracted, bool)
        self.assertIsInstance(self.AS.Low_Power_Act, bool)
        self.assertIsInstance(self.AS.LimDn_inconsist, bool)
        self.assertIsInstance(self.AS.LimUp_inconsist, bool)

        self.assertIsInstance(self.AS.errors, str)
        self.assertIsInstance(self.AS.Error_Active, bool)
        self.assertIsInstance(self.AS.System_fault, bool)
        self.assertIsInstance(self.AS.Em_Stop, bool)
        self.assertIsInstance(self.AS.Em_Limit_Dn_Act, bool)
        self.assertIsInstance(self.AS.Em_Limit_Up_Act, bool)
        self.assertIsInstance(self.AS.Brake_Error, bool)
        self.assertIsInstance(self.AS.Power_Error, bool)
        self.assertIsInstance(self.AS.Servo_Error, bool)
        self.assertIsInstance(self.AS.Servo_Timeout, bool)
        self.assertIsInstance(self.AS.v_Motor_Exceed, bool)
        self.assertIsInstance(self.AS.Servo_Overload, bool)
        self.assertIsInstance(self.AS.Pos_Enc_Error, bool)
        self.assertIsInstance(self.AS.Pos_Enc_Step, bool)
        self.assertIsInstance(self.AS.p_Range_Exceed, bool)
        self.assertIsInstance(self.AS.p_Dev_Exceed, bool)
        self.assertIsInstance(self.AS.Servo_DC_Error, bool)
        self.assertIsInstance(self.AS.Override_Error, bool)
        self.assertIsInstance(self.AS.Cmd_Timeout, bool)
        self.assertIsInstance(self.AS.Rate_Loop_Err, bool)
        self.assertIsInstance(self.AS.v_Dev_Exceed, bool)
        self.assertIsInstance(self.AS.Stow_Error, bool)
        self.assertIsInstance(self.AS.Stow_Timeout, bool)
        self.assertIsInstance(self.AS.Extern_Error, bool)
        self.assertIsInstance(self.AS.Safety_Dev_Error, bool)
        self.assertIsInstance(self.AS.Com_Error, bool)
        self.assertIsInstance(self.AS.Pre_Limit_Err, bool)
        self.assertIsInstance(self.AS.Fin_Limit_Err, bool)

        self.assertIsInstance(self.AS.axis_state, int)
        self.assertIsInstance(self.AS.axis_trajectory_state, int)
        self.assertIsInstance(self.AS.p_Soll, int)
        self.assertIsInstance(self.AS.p_Bahn, int)
        self.assertIsInstance(self.AS.p_Ist, int)
        self.assertIsInstance(self.AS.p_AbwFil, int)
        self.assertIsInstance(self.AS.v_Soll, int)
        self.assertIsInstance(self.AS.v_Bahn, int)
        self.assertIsInstance(self.AS.v_Ist, int)
        self.assertIsInstance(self.AS.a_Bahn, int)
        self.assertIsInstance(self.AS.p_Offset, int)
        self.assertIsInstance(self.AS.motor_selection, list)
        self.assertIsInstance(self.AS.brakes_open, list)
        self.assertIsInstance(self.AS.power_module_ok, list)
        self.assertIsInstance(self.AS.stowed, bool)
        self.assertIsInstance(self.AS.stowPosOk, bool)
        self.assertIsInstance(self.AS.stow_pin_selection, list)
        self.assertIsInstance(self.AS.stow_pin_in, list)
        self.assertIsInstance(self.AS.stow_pin_out, list)
        self.assertIsInstance(self.AS.mode_command_status, bytearray)
        self.assertIsInstance(self.AS.received_mode_command_status, bytearray)
        self.assertIsInstance(self.AS.received_mode_command_counter, int)
        self.assertIsInstance(self.AS.received_mode_command, int)
        self.assertIsInstance(self.AS.received_mode_command_answer, int)
        self.assertIsInstance(self.AS.executed_mode_command_status, bytearray)
        self.assertIsInstance(self.AS.executed_mode_command_counter, int)
        self.assertIsInstance(self.AS.executed_mode_command, int)
        self.assertIsInstance(self.AS.executed_mode_command_answer, int)
        self.assertIsInstance(self.AS.parameter_command_status, bytearray)
        self.assertIsInstance(self.AS.parameter_command_counter, int)
        self.assertIsInstance(self.AS.parameter_command, int)
        self.assertIsInstance(self.AS.parameter_command_answer, int)

    def test_as_wrong_values(self):
        with self.assertRaises(ValueError):
            self.AS.simulation = None
        with self.assertRaises(ValueError):
            self.AS.axis_ready = None
        with self.assertRaises(ValueError):
            self.AS.confOk = None
        with self.assertRaises(ValueError):
            self.AS.initOk = None
        with self.assertRaises(ValueError):
            self.AS.override = None
        with self.assertRaises(ValueError):
            self.AS.low_power_mode = None

        with self.assertRaises(AttributeError):
            self.AS.warnings = None
        with self.assertRaises(ValueError):
            self.AS.Param_Fault = None
        with self.assertRaises(ValueError):
            self.AS.Rate_Mode = None
        with self.assertRaises(ValueError):
            self.AS.Safety_Chain = None
        with self.assertRaises(ValueError):
            self.AS.Wrong_Sys_State = None
        with self.assertRaises(ValueError):
            self.AS.Temp_Enc = None
        with self.assertRaises(ValueError):
            self.AS.Power_Brakes = None
        with self.assertRaises(ValueError):
            self.AS.Power_Servo = None
        with self.assertRaises(ValueError):
            self.AS.Fan_Fault = None
        with self.assertRaises(ValueError):
            self.AS.Servo_DC_Off = None
        with self.assertRaises(ValueError):
            self.AS.Motor_Temp_Warn = None
        with self.assertRaises(ValueError):
            self.AS.Servo_DC_Warn = None
        with self.assertRaises(ValueError):
            self.AS.M_Max_Exceeded = None
        with self.assertRaises(ValueError):
            self.AS.Pos_Enc_Fault = None
        with self.assertRaises(ValueError):
            self.AS.Em_Limit_Dn = None
        with self.assertRaises(ValueError):
            self.AS.Em_Limit_Up = None
        with self.assertRaises(ValueError):
            self.AS.Degraded_Mode = None
        with self.assertRaises(ValueError):
            self.AS.Override_Act = None
        with self.assertRaises(ValueError):
            self.AS.Pre_Limit_Up = None
        with self.assertRaises(ValueError):
            self.AS.Pre_Limit_Dn = None
        with self.assertRaises(ValueError):
            self.AS.Fin_Limit_Up = None
        with self.assertRaises(ValueError):
            self.AS.Fin_Limit_Dn = None
        with self.assertRaises(ValueError):
            self.AS.Rate_Limit = None
        with self.assertRaises(ValueError):
            self.AS.Stow_Fault = None
        with self.assertRaises(ValueError):
            self.AS.Stowpins_Extracted = None
        with self.assertRaises(ValueError):
            self.AS.Low_Power_Act = None
        with self.assertRaises(ValueError):
            self.AS.LimDn_inconsist = None
        with self.assertRaises(ValueError):
            self.AS.LimUp_inconsist = None

        with self.assertRaises(AttributeError):
            self.AS.errors = None
        with self.assertRaises(ValueError):
            self.AS.Error_Active = None
        with self.assertRaises(ValueError):
            self.AS.System_fault = None
        with self.assertRaises(ValueError):
            self.AS.Em_Stop = None
        with self.assertRaises(ValueError):
            self.AS.Em_Limit_Dn_Act = None
        with self.assertRaises(ValueError):
            self.AS.Em_Limit_Up_Act = None
        with self.assertRaises(ValueError):
            self.AS.Brake_Error = None
        with self.assertRaises(ValueError):
            self.AS.Power_Error = None
        with self.assertRaises(ValueError):
            self.AS.Servo_Error = None
        with self.assertRaises(ValueError):
            self.AS.Servo_Timeout = None
        with self.assertRaises(ValueError):
            self.AS.v_Motor_Exceed = None
        with self.assertRaises(ValueError):
            self.AS.Servo_Overload = None
        with self.assertRaises(ValueError):
            self.AS.Pos_Enc_Error = None
        with self.assertRaises(ValueError):
            self.AS.Pos_Enc_Step = None
        with self.assertRaises(ValueError):
            self.AS.p_Range_Exceed = None
        with self.assertRaises(ValueError):
            self.AS.p_Dev_Exceed = None
        with self.assertRaises(ValueError):
            self.AS.Servo_DC_Error = None
        with self.assertRaises(ValueError):
            self.AS.Override_Error = None
        with self.assertRaises(ValueError):
            self.AS.Cmd_Timeout = None
        with self.assertRaises(ValueError):
            self.AS.Rate_Loop_Err = None
        with self.assertRaises(ValueError):
            self.AS.v_Dev_Exceed = None
        with self.assertRaises(ValueError):
            self.AS.Stow_Error = None
        with self.assertRaises(ValueError):
            self.AS.Stow_Timeout = None
        with self.assertRaises(ValueError):
            self.AS.Extern_Error = None
        with self.assertRaises(ValueError):
            self.AS.Safety_Dev_Error = None
        with self.assertRaises(ValueError):
            self.AS.Com_Error = None
        with self.assertRaises(ValueError):
            self.AS.Pre_Limit_Err = None
        with self.assertRaises(ValueError):
            self.AS.Fin_Limit_Err = None

        with self.assertRaises(ValueError):
            self.AS.axis_state = None
        with self.assertRaises(ValueError):
            self.AS.axis_trajectory_state = None
        with self.assertRaises(ValueError):
            self.AS.p_Soll = None
        with self.assertRaises(ValueError):
            self.AS.p_Bahn = None
        with self.assertRaises(ValueError):
            self.AS.p_Ist = None
        with self.assertRaises(ValueError):
            self.AS.p_AbwFil = None
        with self.assertRaises(ValueError):
            self.AS.v_Soll = None
        with self.assertRaises(ValueError):
            self.AS.v_Bahn = None
        with self.assertRaises(ValueError):
            self.AS.v_Ist = None
        with self.assertRaises(ValueError):
            self.AS.a_Bahn = None
        with self.assertRaises(ValueError):
            self.AS.p_Offset = None
        with self.assertRaises(ValueError):
            self.AS.motor_selection = None
        with self.assertRaises(ValueError):
            self.AS.motor_selection = ['0' for _ in range(16)]
        with self.assertRaises(ValueError):
            self.AS.brakes_open = None
        with self.assertRaises(ValueError):
            self.AS.brakes_open = ['0' for _ in range(16)]
        with self.assertRaises(ValueError):
            self.AS.power_module_ok = None
        with self.assertRaises(ValueError):
            self.AS.power_module_ok = ['0' for _ in range(16)]
        with self.assertRaises(ValueError):
            self.AS.stowed = None
        with self.assertRaises(ValueError):
            self.AS.stowPosOk = None
        with self.assertRaises(ValueError):
            self.AS.stow_pin_selection = None
        with self.assertRaises(ValueError):
            self.AS.stow_pin_selection = ['0' for _ in range(16)]
        with self.assertRaises(ValueError):
            self.AS.stow_pin_in = None
        with self.assertRaises(ValueError):
            self.AS.stow_pin_in = ['0' for _ in range(16)]
        with self.assertRaises(ValueError):
            self.AS.stow_pin_out = None
        with self.assertRaises(ValueError):
            self.AS.stow_pin_out = ['0' for _ in range(16)]
        with self.assertRaises(ValueError):
            self.AS.received_mode_command_counter = None
        with self.assertRaises(ValueError):
            self.AS.received_mode_command = None
        with self.assertRaises(ValueError):
            self.AS.received_mode_command_answer = None
        with self.assertRaises(ValueError):
            self.AS.executed_mode_command_counter = None
        with self.assertRaises(ValueError):
            self.AS.executed_mode_command = None
        with self.assertRaises(ValueError):
            self.AS.executed_mode_command_answer = None
        with self.assertRaises(ValueError):
            self.AS.parameter_command_counter = None
        with self.assertRaises(ValueError):
            self.AS.parameter_command = None
        with self.assertRaises(ValueError):
            self.AS.parameter_command_answer = None

    def test_ms_values(self):
        self.assertIsInstance(self.MS.actual_position, float)
        self.assertIsInstance(self.MS.actual_velocity, float)
        self.assertIsInstance(self.MS.actual_torque, float)
        self.assertIsInstance(self.MS.rate_of_utilization, float)
        self.assertIsInstance(self.MS.active, int)
        self.assertIsInstance(self.MS.speed_of_rotation, int)
        self.assertIsInstance(self.MS.speed_of_rotation_OK, int)
        self.assertIsInstance(self.MS.position, int)
        self.assertIsInstance(self.MS.bus, int)
        self.assertIsInstance(self.MS.servo, int)
        self.assertIsInstance(self.MS.sensor, int)
        self.assertIsInstance(self.MS.motWarnCode, str)
        self.assertIsInstance(self.MS.wa_iQuad_t, bool)
        self.assertIsInstance(self.MS.wa_Temp_Amplifier, bool)
        self.assertIsInstance(self.MS.wa_Temp_Mot, bool)
        self.assertIsInstance(self.MS.wa_v_Max_Exceeded, bool)
        self.assertIsInstance(self.MS.wa_M_Max_Exceeded, bool)
        self.assertIsInstance(self.MS.wa_Mot_Overload, bool)
        self.assertIsInstance(self.MS.wa_Temp_Cooling, bool)
        self.assertIsInstance(self.MS.wa_Temp_Extern, bool)
        self.assertIsInstance(self.MS.wa_Temp_Pow_Supply, bool)
        self.assertIsInstance(self.MS.wa_Temp_ERM_Module, bool)
        self.assertIsInstance(self.MS.wa_U_Max, bool)
        self.assertIsInstance(self.MS.wa_U_Min, bool)
        self.assertIsInstance(self.MS.wa_Intermed_Circ_Voltage, bool)
        self.assertIsInstance(self.MS.wa_Wrong_Mode, bool)
        self.assertIsInstance(self.MS.wa_err_cmd_M, bool)
        self.assertIsInstance(self.MS.wa_err_sts_SBM, bool)
        self.assertIsInstance(self.MS.wa_err_sts_EF, bool)
        self.assertIsInstance(self.MS.wa_err_sts_RF, bool)

    def test_ms_wrong_values(self):
        with self.assertRaises(ValueError):
            self.MS.actual_position = None
        with self.assertRaises(ValueError):
            self.MS.actual_velocity = None
        with self.assertRaises(ValueError):
            self.MS.actual_torque = None
        with self.assertRaises(ValueError):
            self.MS.rate_of_utilization = None
        with self.assertRaises(ValueError):
            self.MS.active = None
        with self.assertRaises(ValueError):
            self.MS.speed_of_rotation = None
        with self.assertRaises(ValueError):
            self.MS.speed_of_rotation_OK = None
        with self.assertRaises(ValueError):
            self.MS.position = None
        with self.assertRaises(ValueError):
            self.MS.bus = None
        with self.assertRaises(ValueError):
            self.MS.servo = None
        with self.assertRaises(ValueError):
            self.MS.sensor = None
        with self.assertRaises(AttributeError):
            self.MS.motWarnCode = None
        with self.assertRaises(ValueError):
            self.MS.wa_iQuad_t = None
        with self.assertRaises(ValueError):
            self.MS.wa_Temp_Amplifier = None
        with self.assertRaises(ValueError):
            self.MS.wa_Temp_Mot = None
        with self.assertRaises(ValueError):
            self.MS.wa_v_Max_Exceeded = None
        with self.assertRaises(ValueError):
            self.MS.wa_M_Max_Exceeded = None
        with self.assertRaises(ValueError):
            self.MS.wa_Mot_Overload = None
        with self.assertRaises(ValueError):
            self.MS.wa_Temp_Cooling = None
        with self.assertRaises(ValueError):
            self.MS.wa_Temp_Extern = None
        with self.assertRaises(ValueError):
            self.MS.wa_Temp_Pow_Supply = None
        with self.assertRaises(ValueError):
            self.MS.wa_Temp_ERM_Module = None
        with self.assertRaises(ValueError):
            self.MS.wa_U_Max = None
        with self.assertRaises(ValueError):
            self.MS.wa_U_Min = None
        with self.assertRaises(ValueError):
            self.MS.wa_Intermed_Circ_Voltage = None
        with self.assertRaises(ValueError):
            self.MS.wa_Wrong_Mode = None
        with self.assertRaises(ValueError):
            self.MS.wa_err_cmd_M = None
        with self.assertRaises(ValueError):
            self.MS.wa_err_sts_SBM = None
        with self.assertRaises(ValueError):
            self.MS.wa_err_sts_EF = None
        with self.assertRaises(ValueError):
            self.MS.wa_err_sts_RF = None

    def test_ps_values(self):
        self.assertIsInstance(self.PS.confVersion, float)
        self.assertIsInstance(self.PS.confOk, bool)
        self.assertIsInstance(self.PS.posEncAz, int)
        self.assertIsInstance(self.PS.pointOffsetAz, int)
        self.assertIsInstance(self.PS.posCalibChartAz, int)
        self.assertIsInstance(self.PS.posCorrTableAz_F_plst_El, int)
        self.assertIsInstance(self.PS.posCorrTableAzOn, bool)
        self.assertIsInstance(self.PS.encAzFault, bool)
        self.assertIsInstance(self.PS.sectorSwitchAz, bool)
        self.assertIsInstance(self.PS.posEncEl, int)
        self.assertIsInstance(self.PS.pointOffsetEl, int)
        self.assertIsInstance(self.PS.posCalibChartEl, int)
        self.assertIsInstance(self.PS.posCorrTableEl_F_plst_Az, int)
        self.assertIsInstance(self.PS.posCorrTableElOn, bool)
        self.assertIsInstance(self.PS.encElFault, int)
        self.assertIsInstance(self.PS.posEncCw, int)
        self.assertIsInstance(self.PS.posCalibChartCw, int)
        self.assertIsInstance(self.PS.encCwFault, int)
        self.assertIsInstance(self.PS.timeSource, int)
        self.assertIsInstance(self.PS.actTime, float)
        self.assertIsInstance(self.PS.actTimeOffset, float)
        self.assertIsInstance(self.PS.clockOnline, int)
        self.assertIsInstance(self.PS.clockOK, int)
        self.assertIsInstance(self.PS.year, int)
        self.assertIsInstance(self.PS.month, int)
        self.assertIsInstance(self.PS.day, int)
        self.assertIsInstance(self.PS.hour, int)
        self.assertIsInstance(self.PS.minute, int)
        self.assertIsInstance(self.PS.second, int)
        self.assertIsInstance(self.PS.actPtPos_Azimuth, int)
        self.assertIsInstance(self.PS.actPtPos_Elevation, int)
        self.assertIsInstance(self.PS.ptState, int)
        self.assertIsInstance(self.PS.ptError, str)
        self.assertIsInstance(self.PS.Data_Overflow, bool)
        self.assertIsInstance(self.PS.Time_Distance_Fault, bool)
        self.assertIsInstance(self.PS.No_Data_Available, bool)
        self.assertIsInstance(self.PS.actPtTimeOffset, int)
        self.assertIsInstance(self.PS.ptInterpolMode, int)
        self.assertIsInstance(self.PS.ptTrackingType, int)
        self.assertIsInstance(self.PS.ptTrackingMode, int)
        self.assertIsInstance(self.PS.ptActTableIndex, int)
        self.assertIsInstance(self.PS.ptEndTableIndex, int)
        self.assertIsInstance(self.PS.ptTableLength, int)
        self.assertIsInstance(self.PS.parameter_command_counter, int)
        self.assertIsInstance(self.PS.parameter_command, int)
        self.assertIsInstance(self.PS.parameter_command_answer, int)

    def test_ps_wrong_values(self):
        with self.assertRaises(ValueError):
            self.PS.confVersion = None
        with self.assertRaises(ValueError):
            self.PS.confOk = None
        with self.assertRaises(ValueError):
            self.PS.posEncAz = None
        with self.assertRaises(ValueError):
            self.PS.pointOffsetAz = None
        with self.assertRaises(ValueError):
            self.PS.posCalibChartAz = None
        with self.assertRaises(ValueError):
            self.PS.posCorrTableAz_F_plst_El = None
        with self.assertRaises(ValueError):
            self.PS.posCorrTableAzOn = None
        with self.assertRaises(ValueError):
            self.PS.encAzFault = None
        with self.assertRaises(ValueError):
            self.PS.sectorSwitchAz = None
        with self.assertRaises(ValueError):
            self.PS.posEncEl = None
        with self.assertRaises(ValueError):
            self.PS.pointOffsetEl = None
        with self.assertRaises(ValueError):
            self.PS.posCalibChartEl = None
        with self.assertRaises(ValueError):
            self.PS.posCorrTableEl_F_plst_Az = None
        with self.assertRaises(ValueError):
            self.PS.posCorrTableElOn = None
        with self.assertRaises(ValueError):
            self.PS.encElFault = None
        with self.assertRaises(ValueError):
            self.PS.posEncCw = None
        with self.assertRaises(ValueError):
            self.PS.posCalibChartCw = None
        with self.assertRaises(ValueError):
            self.PS.encCwFault = None
        with self.assertRaises(ValueError):
            self.PS.timeSource = None
        with self.assertRaises(ValueError):
            self.PS.actTime = None
        with self.assertRaises(ValueError):
            self.PS.actTimeOffset = None
        with self.assertRaises(ValueError):
            self.PS.clockOnline = None
        with self.assertRaises(ValueError):
            self.PS.clockOK = None
        with self.assertRaises(ValueError):
            self.PS.year = None
        with self.assertRaises(ValueError):
            self.PS.month = None
        with self.assertRaises(ValueError):
            self.PS.day = None
        with self.assertRaises(ValueError):
            self.PS.hour = None
        with self.assertRaises(ValueError):
            self.PS.minute = None
        with self.assertRaises(ValueError):
            self.PS.second = None
        with self.assertRaises(ValueError):
            self.PS.actPtPos_Azimuth = None
        with self.assertRaises(ValueError):
            self.PS.actPtPos_Elevation = None
        with self.assertRaises(ValueError):
            self.PS.ptState = None
        with self.assertRaises(AttributeError):
            self.PS.ptError = None
        with self.assertRaises(ValueError):
            self.PS.Data_Overflow = None
        with self.assertRaises(ValueError):
            self.PS.Time_Distance_Fault = None
        with self.assertRaises(ValueError):
            self.PS.No_Data_Available = None
        with self.assertRaises(ValueError):
            self.PS.actPtTimeOffset = None
        with self.assertRaises(ValueError):
            self.PS.ptInterpolMode = None
        with self.assertRaises(ValueError):
            self.PS.ptTrackingType = None
        with self.assertRaises(ValueError):
            self.PS.ptTrackingMode = None
        with self.assertRaises(ValueError):
            self.PS.ptActTableIndex = None
        with self.assertRaises(ValueError):
            self.PS.ptEndTableIndex = None
        with self.assertRaises(ValueError):
            self.PS.ptTableLength = None
        with self.assertRaises(ValueError):
            self.PS.parameter_command_counter = None
        with self.assertRaises(ValueError):
            self.PS.parameter_command = None
        with self.assertRaises(ValueError):
            self.PS.parameter_command_answer = None

    def test_fs_values(self):
        self.assertIsInstance(self.FS.voltagePhToPh, float)
        self.assertIsInstance(self.FS.currentPhToPh, float)

    def test_fs_wrong_values(self):
        with self.assertRaises(ValueError):
            self.FS.voltagePhToPh = None
        with self.assertRaises(ValueError):
            self.FS.currentPhToPh = None


if __name__ == '__main__':
    unittest.main()
