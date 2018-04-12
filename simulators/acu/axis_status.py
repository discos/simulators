import time
from simulators import utils
from simulators.acu.motor_status import MotorStatus
from simulators.acu.command_status import (
    CommandStatus,
    ModeCommandStatus,
    ParameterCommandStatus
)


class SimpleAxisStatus(object):

    def __init__(self, n_motors=1):
        self.motor_status = []

        for _ in range(n_motors):
            self.motor_status.append(MotorStatus())

        self.simulation = 0  # BOOL, 0: axis simulation off, 1: on
        self.axis_ready = 1  # BOOL, 0: axis not ready for activating, 1: ready
        self.conf_ok = 1  # BOOL, 0: conf. file read error, 1: read successful
        self.init_ok = 1  # BOOL, 0: faulty conf. data, 1: init. completed
        self.override = 0  # BOOL, 0: override mode not active, 1: active
        self.low_power = 0  # BOOL, 0: low power mode not active, 1: active

        # Warnings, DWORD, in bit mode coded warning indication
        self.Param_Fault = 0
        self.Rate_Mode = 0
        self.Safety_Chain = 0
        self.Wrong_Sys_State = 0
        self.Temp_Enc = 0
        # bit 5 = 0, not used
        self.Power_Brakes = 0
        self.Power_Servo = 0
        self.Fan_Fault = 0
        self.Servo_DC_Off = 0
        self.Motor_Temp_Warn = 0
        self.Servo_DC_Warn = 0
        self.M_Max_Exceeded = 0
        self.Pos_Enc_Fault = 0
        # bit 14 = 0, not used
        self.Em_Limit_Dn = 0
        self.Em_Limit_Up = 0
        self.Degraded_Mode = 0
        self.Override_Act = 0
        self.Pre_Limit_Up = 0
        self.Pre_Limit_Dn = 0
        self.Fin_Limit_Up = 0
        self.Fin_Limit_Dn = 0
        self.Rate_Limit = 0
        self.Stow_Fault = 0
        self.Stowpins_Extracted = 0
        self.Low_Power_Act = 0
        # bits 27:28 = 0, not used
        self.LimDn_inconsist = 0
        self.LimUp_inconsist = 0
        # bit 31 = 0, not used

        # Errors, DWORD, in bit mode coded error indication
        self.Error_Active = 0
        self.System_fault = 0
        self.Em_Stop = 0
        self.Em_Limit_Dn_Act = 0
        self.Em_Limit_Up_Act = 0
        # bit 5 = 0, not used
        self.Brake_Error = 0
        self.Power_Error = 0
        self.Servo_Error = 0
        self.Servo_Timeout = 0
        # bit 10 = 0, not used
        self.v_Motor_Exceed = 0
        self.Servo_Overload = 0
        self.Pos_Enc_Error = 0
        self.Pos_Enc_Step = 0
        self.p_Range_Exceed = 0
        self.p_Dev_Exceed = 0
        self.Servo_DC_Error = 0
        self.Override_Error = 0
        self.Cmd_Timeout = 0
        # bits 20:21 = 0, not used
        self.Rate_Loop_Err = 0
        self.v_Dev_Exceed = 0
        self.Stow_Error = 0
        self.Stow_Timeout = 0
        self.Extern_Error = 0
        self.Safety_Dev_Error = 0
        # bit 28 = 0, not used
        self.Com_Error = 0
        self.Pre_Limit_Err = 0
        self.Fin_Limit_Err = 0

        # axis_state, UINT16
        # 0: inactive
        # 1: deactivating
        # 2: activating
        # 3: active
        self.axis_state = 0

        # axis_trajectory_state, UINT16
        # 0: off
        # 1: holding
        # 2: emergency stop
        # 3: stop
        # 4: slewing velocity
        # 5: N/D
        # 6: position
        # 7: tracking
        self.axis_trajectory_state = 0

        # p_Soll, INT32, desired position [microdeg]
        self.p_Soll = 0

        # p_Bahn, INT32, output pos. of the trajectory generator [microdeg]
        self.p_Bahn = 0

        # p_Ist, INT32, actual pos. [microdeg]
        self.p_Ist = 0

        # p_AbwFil, INT32, filtered pos. deviation [microdeg]
        self.p_AbwFil = 0

        # v_Soll, INT32, desired vel. [microdeg/s]
        self.v_Soll = 0

        # v_Bahn, INT32, output vel. of the trajectory generator [microdeg/s]
        self.v_Bahn = 0

        # v_Ist, INT32, actual vel. [microdeg/s]
        self.v_Ist = 0

        # a_Bahn, INT32, output accel. of the trajectory generator
        # [microdeg/s^2]
        self.a_Bahn = 0

        # p_Offset, INT32, pos. offset for tracking mode [microdeg]
        self.p_Offset = 0

        # motor_selection, WORD
        # in bit mode coded indicator for the selected motors
        # 0: motor not selected, 1: motor selected
        # SRT range: 0:8 for Azimuth, 0:4 for Elevation, 0:1 for Cable Wrap
        self.motor_selection = '0' * (16 - n_motors) + '1' * n_motors

        # brakes_open, WORD
        # in bit mode coded indicator for the brakes that are open
        # 0: brake not open, 1: brake open
        # SRT range: same as motor_selection
        self.brakes_open = '0' * 16

        # power_module_ok, WORD
        # in bit mode coded indicator for the
        # power module concerning each motor
        self.power_module_ok = self.motor_selection

        self.stowed = 0  # BOOL, 0: axis not stowed, 1: axis stowed

        self.stow_pos_ok = 0  # BOOL, 0: is no stow pos., 1: is stow pos.

        # stow_pin_selection, WORD
        # in bit mode coded indicator for the number of stow pins
        # 0: stow pin not selected, 1: stow pin selected
        self.stow_pin_selection = '0' * 16

        # stow_pin_in, WORD
        # in bit mode coded indicator if the stow pins are in
        # 0: stow pin not in, 1: stow pin in
        self.stow_pin_in = self.stow_pin_selection

        # stow_pin_out, WORD
        # in bit mode coded indicator if the stow pins are out
        # 0: stow pin not out, 1: stow pin out
        self.stow_pin_out = utils.binary_complement(
            self.stow_pin_in,
            self.stow_pin_selection
        )

        # mode_command_status, refer to ModeCommandStatus class
        self.mcs = ModeCommandStatus()

        # parameter_command_status, refer to ParameterCommandStatus class
        self.pcs = ParameterCommandStatus()

    def _warnings(self):
        binary_string = (
            str(self.Param_Fault)
            + str(self.Rate_Mode)
            + str(self.Safety_Chain)
            + str(self.Wrong_Sys_State)
            + str(self.Temp_Enc)
            + '0'
            + str(self.Power_Brakes)
            + str(self.Power_Servo)
            + str(self.Fan_Fault)
            + str(self.Servo_DC_Off)
            + str(self.Motor_Temp_Warn)
            + str(self.Servo_DC_Warn)
            + str(self.M_Max_Exceeded)
            + str(self.Pos_Enc_Fault)
            + '0'
            + str(self.Em_Limit_Dn)
            + str(self.Em_Limit_Up)
            + str(self.Degraded_Mode)
            + str(self.Override_Act)
            + str(self.Pre_Limit_Up)
            + str(self.Pre_Limit_Dn)
            + str(self.Fin_Limit_Up)
            + str(self.Fin_Limit_Dn)
            + str(self.Rate_Limit)
            + str(self.Stow_Fault)
            + str(self.Stowpins_Extracted)
            + str(self.Low_Power_Act)
            + '0' * 2
            + str(self.LimDn_inconsist)
            + str(self.LimUp_inconsist)
            + '0'
        )
        return utils.binary_to_bytes(binary_string)

    def _errors(self):
        binary_string = (
            str(self.Error_Active)
            + str(self.System_fault)
            + str(self.Em_Stop)
            + str(self.Em_Limit_Dn_Act)
            + str(self.Em_Limit_Up_Act)
            + '0'
            + str(self.Brake_Error)
            + str(self.Power_Error)
            + str(self.Servo_Error)
            + str(self.Servo_Timeout)
            + '0'
            + str(self.v_Motor_Exceed)
            + str(self.Servo_Overload)
            + str(self.Pos_Enc_Error)
            + str(self.Pos_Enc_Step)
            + str(self.p_Range_Exceed)
            + str(self.p_Dev_Exceed)
            + str(self.Servo_DC_Error)
            + str(self.Override_Error)
            + str(self.Cmd_Timeout)
            + '0' * 2
            + str(self.Rate_Loop_Err)
            + str(self.v_Dev_Exceed)
            + str(self.Stow_Error)
            + str(self.Stow_Timeout)
            + str(self.Extern_Error)
            + str(self.Safety_Dev_Error)
            + '0'
            + str(self.Com_Error)
            + str(self.Pre_Limit_Err)
            + str(self.Fin_Limit_Err)
        )
        return utils.binary_to_bytes(binary_string)

    def get_axis_status(self):
        response = (
            chr(self.simulation)
            + chr(self.axis_ready)
            + chr(self.conf_ok)
            + chr(self.init_ok)
            + chr(self.override)
            + chr(self.low_power)
            + self._warnings()
            + self._errors()
            + utils.uint_to_bytes(self.axis_state, 2)
            + utils.uint_to_bytes(self.axis_trajectory_state, 2)
            + utils.int_to_bytes(self.p_Soll)
            + utils.int_to_bytes(self.p_Bahn)
            + utils.int_to_bytes(self.p_Ist)
            + utils.int_to_bytes(self.p_AbwFil)
            + utils.int_to_bytes(self.v_Soll)
            + utils.int_to_bytes(self.v_Bahn)
            + utils.int_to_bytes(self.v_Ist)
            + utils.int_to_bytes(self.a_Bahn)
            + utils.int_to_bytes(self.p_Offset)
            + utils.binary_to_bytes(self.motor_selection)
            + utils.binary_to_bytes(self.brakes_open)
            + utils.binary_to_bytes(self.power_module_ok)
            + chr(self.stowed)
            + chr(self.stow_pos_ok)
            + utils.binary_to_bytes(self.stow_pin_in)
            + utils.binary_to_bytes(self.stow_pin_out)
            + utils.binary_to_bytes(self.stow_pin_selection)
            + self.mcs.get_status()
            + self.pcs.get_status()
        )

        return response

    def get_motor_status(self):
        response = ''
        for motor_status in self.motor_status:
            response += motor_status.get_status()
        return response


class MasterAxisStatus(SimpleAxisStatus):

    mode_commands = {
        0: '_ignore',
        1: '_inactive',
        2: '_active',
        3: '_preset_absolute',
        4: '_preset_relative',
        5: '_slew',
        7: '_stop',
        8: '_program_track',
        14: '_interlock',
        15: '_reset',
        50: '_stow',
        51: '_unstow',
        52: '_drive_to_stow',
    }

    def __init__(self,
            n_motors,
            max_rates,
            op_range,
            start_pos,
            stow_pos=None):

        SimpleAxisStatus.__init__(self, n_motors)

        self.max_velocity, self.max_acceleration = max_rates
        self.min_pos, self.max_pos = op_range
        self.stow_pos = stow_pos

        self.pointing = None  # PointingStatus will update this attribute
        self.curr_mode_counter = None  # Current ModeCommand counter

        self.p_Ist = int(round(start_pos * 1000000))
        self.p_Soll = self.p_Ist
        self.p_Bahn = self.p_Ist

        if self.stow_pos:
            self.stow_pin_selection = (
                '0' * (16 - len(self.stow_pos))
                + '1' * len(self.stow_pos)
            )

            if float(self.p_Ist) / 1000000 in self.stow_pos:
                self.stowed = 1
                self.stow_pos_ok = 1

        if self.stowed == 1:
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = '0' * 16
        else:
            self.stow_pin_out = '0' * 16
            self.stow_pin_in = self.stow_pin_selection

    def _calc_position(self, delta_time, desired_pos, desired_rate):
        current_pos = self.p_Ist
        sign = utils.sign(desired_pos - current_pos)
        if sign != 0:
            current_pos += sign * int(round(abs(desired_rate) * delta_time))
            res_sign = utils.sign(desired_pos - current_pos)
            if res_sign != sign:
                current_pos = desired_pos
        current_pos = min(current_pos, int(round(self.max_pos * 1000000)))
        current_pos = max(current_pos, int(round(self.min_pos * 1000000)))
        return current_pos

    def _move(self, counter, desired_pos, desired_rate, pt_counter=None):

        self.p_Soll = desired_pos
        self.v_Soll = desired_rate

        if pt_counter:
            self.p_Soll += self.p_Offset

        t0 = time.time()

        # Additional check to time module, when the father thread exits, the
        # time module becomes 'None' and an exception is raised (it happens on
        # exit so this should not be an issue).
        while time is not None:
            t1 = time.time()
            delta_time = t1 - t0
            t0 = t1

            current_pos = self._calc_position(
                delta_time,
                desired_pos,
                desired_rate
            )
            if pt_counter:
                if pt_counter != self.pointing.pt_command_id:
                    # Program track related, if a new table is received we
                    # need to stop the movement of the axis, we set the
                    # `counter` variable to -1 since no counter can be
                    # negative
                    counter = -1
            if counter == self.curr_mode_counter:
                if self.axis_state == 3 and self.stowed == 0:
                    self.v_Ist = desired_rate
                    self.p_Ist = current_pos
                else:
                    self.v_Ist = 0

                if self.p_Ist == desired_pos:
                    self.v_Ist = 0
                    return True
            else:
                self.v_Ist = 0
                return False
            time.sleep(0.01)

    def _update_status(self):
        # This method is called to update some of the values before comparison
        # or sending.
        if self.stow_pos:
            if float(self.p_Ist) / 1000000 in self.stow_pos:
                self.stow_pos_ok = 1
            else:
                self.stow_pos_ok = 0

        if (self.mcs.executed.counter == self.curr_mode_counter
                and self.mcs.executed.answer == 1):
            self.curr_mode_counter = None

        self._update_trajectory_values()

    def _update_trajectory_values(self):
        data = self.pointing.get_trajectory_values(self)
        pt_status, self.p_Bahn, self.v_Bahn, self.a_Bahn = data
        return pt_status

    def get_axis_status(self):
        self._update_status()

        return SimpleAxisStatus.get_axis_status(self)

    # -------------------- Mode Command --------------------

    def mode_command(self, cmd):
        cmd_cnt = utils.bytes_to_int(cmd[4:8])
        mode_id = utils.bytes_to_int(cmd[8:10])
        par_1 = utils.bytes_to_real(cmd[10:18], 2)
        par_2 = utils.bytes_to_real(cmd[18:26], 2)

        received_command_status = CommandStatus()
        received_command_status.counter = cmd_cnt

        command = self.mode_commands.get(mode_id)

        if command is None or command == '_ignore':
            self.mcs.received = received_command_status
            return
        else:
            received_command_status.command = mode_id

        received_command_status.answer = self._validate_mode_command(
            mode_id,
            par_1,
            par_2
        )

        self.mcs.received = received_command_status

        if received_command_status.answer == 9:
            method = getattr(self, command)

            self._executed_mode_command(cmd_cnt, mode_id, 2)
            method(cmd_cnt, par_1, par_2)

    def _validate_mode_command(self, mode_id, parameter_1, parameter_2):
        received_command_answer = 9  # Command accepted

        self._update_status()
        axis_state = self.axis_state

        if mode_id == 2 and axis_state != 0:
            received_command_answer = 4
        elif mode_id in [3, 4, 5, 7, 8, 52] and axis_state != 3:
            received_command_answer = 4
        elif mode_id == 15 and axis_state not in [0, 1]:
            received_command_answer = 4
        elif mode_id == 50:
            if not self.stow_pos_ok:
                received_command_answer = 4

        if mode_id == 3:
            if parameter_1 < self.min_pos or parameter_1 > self.max_pos:
                received_command_answer = 5
            if abs(parameter_2) > self.max_velocity:
                received_command_answer = 5
        elif mode_id == 4:
            desired_pos = (self.p_Ist / 1000000) + parameter_1

            if desired_pos < self.min_pos or desired_pos > self.max_pos:
                received_command_answer = 5
            if abs(int(parameter_2)) > self.max_velocity:
                received_command_answer = 5
        elif mode_id == 5:
            if abs(parameter_1) > 1:
                received_command_answer = 5
            if abs(parameter_2) > self.max_velocity:
                received_command_answer = 5
        elif mode_id == 8:
            if abs(parameter_2) > self.max_velocity:
                received_command_answer = 5
        elif mode_id == 52:
            if self.stow_pos:
                if int(parameter_1) not in range(len(self.stow_pos)):
                    received_command_answer = 5
                if abs(parameter_2) > 0.5 * self.max_velocity:
                    received_command_answer = 5

        return received_command_answer

    def _executed_mode_command(self, counter, command, answer):
        executed = CommandStatus()
        executed.counter = counter
        executed.command = command
        executed.answer = answer
        self.mcs.executed = executed

    # mode_id == 1
    def _inactive(self, counter, *_):
        self.axis_state = 0
        self.brakes_open = '0' * 16
        self._executed_mode_command(counter, 1, 1)

    # mode_id == 2
    def _active(self, counter, *_):
        self.axis_state = 3
        self.brakes_open = (
            '0' * (16 - len(self.motor_status))
            + '1' * len(self.motor_status)
        )
        self._executed_mode_command(counter, 2, 1)

    # mode_id == 3
    def _preset_absolute(self, counter, angle, rate):
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 6
        desired_pos = int(round(angle * 1000000))
        desired_rate = int(round(rate * 1000000))
        if self._move(counter, desired_pos, desired_rate):
            self._executed_mode_command(counter, 3, 1)

    # mode_id == 4
    def _preset_relative(self, counter, angle, rate):
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 6
        desired_pos = self.p_Soll + int(round(angle * 1000000))
        desired_rate = int(round(rate * 1000000))
        if self._move(counter, desired_pos, desired_rate):
            self._executed_mode_command(counter, 4, 1)

    # mode_id == 5
    def _slew(self, counter, percentage, rate):
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 4
        desired_rate = int(round(rate * 1000000 * percentage))
        if utils.sign(desired_rate) > 0:
            desired_pos = int(round(self.max_pos * 1000000))
        elif utils.sign(desired_rate) < 0:
            desired_pos = int(round(self.min_pos * 1000000))
        else:
            desired_pos = self.p_Ist
        if self._move(counter, desired_pos, desired_rate):
            self._executed_mode_command(counter, 5, 1)

    # mode_id == 7
    def _stop(self, counter, *_):
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 3
        self._executed_mode_command(counter, 7, 1)

    # mode_id == 8
    def _program_track(self, counter, _, rate):
        self.curr_mode_counter = counter
        if self.pointing.ptState in [0, 1, 4]:
            self._executed_mode_command(counter, 8, 1)
            return

        self.axis_trajectory_state = 7  # 7: tracking

        next_pos = self.pointing.get_next_position(self)

        # We do not add the tracking offset to the desired position
        # because it is already been handled by the `_move` method
        desired_pos = next_pos
        desired_rate = int(round(rate * 1000000))

        pt_counter = self.pointing.pt_command_id

        if not self._move(counter, desired_pos, desired_rate, pt_counter):
            return

        t0 = time.time()
        while pt_counter == self.pointing.pt_command_id:
            t1 = time.time()
            delta_time = t1 - t0
            t0 = t1

            program_track_state = self._update_trajectory_values()

            next_p = self.pointing.get_next_position(self)
            if next_p:
                next_pos = next_p

            if program_track_state == 4:
                if self.p_Ist == next_pos + self.p_Offset:
                    self._executed_mode_command(counter, 8, 1)
                    break
                else:
                    program_track_state = 3

            if program_track_state == 3:
                desired_pos = self.p_Bahn + self.p_Offset

                if counter == self.curr_mode_counter:
                    self.p_Ist = self._calc_position(
                        delta_time,
                        desired_pos,
                        int(round(self.max_velocity * 1000000)),
                    )
                else:
                    break
            time.sleep(0.01)

    # mode_id == 14
    def _interlock(self, counter, *_):
        self._executed_mode_command(counter, 14, 1)

    # mode_id == 15
    def _reset(self, counter, *_):
        self.Error_Active = 0
        self.System_fault = 0
        self.Em_Stop = 0
        self.Em_Limit_Dn_Act = 0
        self.Em_Limit_Up_Act = 0
        self.Brake_Error = 0
        self.Power_Error = 0
        self.Servo_Error = 0
        self.Servo_Timeout = 0
        self.v_Motor_Exceed = 0
        self.Servo_Overload = 0
        self.Pos_Enc_Error = 0
        self.Pos_Enc_Step = 0
        self.p_Range_Exceed = 0
        self.p_Dev_Exceed = 0
        self.Servo_DC_Error = 0
        self.Override_Error = 0
        self.Cmd_Timeout = 0
        self.Rate_Loop_Err = 0
        self.v_Dev_Exceed = 0
        self.Stow_Error = 0
        self.Stow_Timeout = 0
        self.Extern_Error = 0
        self.Safety_Dev_Error = 0
        self.Com_Error = 0
        self.Pre_Limit_Err = 0
        self.Fin_Limit_Err = 0
        self._executed_mode_command(counter, 15, 1)

    # mode_id == 50
    def _stow(self, counter, *_):
        if self.stow_pos:
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = '0' * 16
            self.stowed = 1
        self._executed_mode_command(counter, 50, 1)

    # mode_id == 51
    def _unstow(self, counter, *_):
        if self.stow_pos:
            self.stow_pin_out = '0' * 16
            self.stow_pin_in = self.stow_pin_selection
            self.stowed = 0
        self._executed_mode_command(counter, 51, 1)

    # mode_id == 52
    def _drive_to_stow(self, counter, stow_pos, rate):
        stow_pos = int(stow_pos)
        if self.stow_pos:
            desired_pos = int(round(self.stow_pos[int(stow_pos)] * 1000000))
            desired_rate = int(round(rate * 1000000))
            self.curr_mode_counter = counter
            if not self._move(counter, desired_pos, desired_rate):
                return
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = '0' * 16
            self.stowed = 1
        self._executed_mode_command(counter, 52, 1)

    # -------------------- Parameter Command --------------------

    def parameter_command(self, cmd):
        cmd_cnt = utils.bytes_to_uint(cmd[4:8])
        parameter_id = utils.bytes_to_uint(cmd[8:10])
        parameter_1 = utils.bytes_to_real(cmd[10:18], 2)
        parameter_2 = utils.bytes_to_real(cmd[18:26], 2)

        pcs = ParameterCommandStatus()
        pcs.counter = cmd_cnt
        pcs.command = parameter_id

        if self.axis_state != 3:
            pcs.answer = 4
            self.pcs = pcs
            return

        if parameter_id == 11:
            pcs.answer = self._absolute_position_offset(
                parameter_1,
                parameter_2
            )
        elif parameter_id == 12:
            pcs.answer = self._relative_position_offset(
                parameter_1,
                parameter_2
            )
        else:
            pcs.answer = 5

        self.pcs = pcs

    def _absolute_position_offset(self, offset, _):
        # 2nd parameter should be ramp time but in the
        # current implementation it will be ignored
        self.p_Offset = int(round(offset * 1000000))
        return 1

    def _relative_position_offset(self, offset, _):
        # 2nd parameter should be ramp time but in the
        # current implementation it will be ignored
        self.p_Offset += int(round(offset * 1000000))
        return 1


class SlaveAxisStatus(SimpleAxisStatus):

    def __init__(self, n_motors, master):
        SimpleAxisStatus.__init__(self, n_motors)

        self.master = master

    def get_axis_status(self):
        self.p_Ist = self.master.p_Ist
        self.v_Ist = self.master.v_Ist

        if self.master.axis_state == 3:
            self.brakes_open = (
                '0' * (16 - len(self.motor_status))
                + '1' * len(self.motor_status)
            )
        else:
            self.brakes_open = '0' * 16

        return SimpleAxisStatus.get_axis_status(self)
