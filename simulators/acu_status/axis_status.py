import time
import thread
from simulators.acu_status import motor_status as ms
from simulators.acu_status import parameter_command_status
from simulators.acu_status import mode_command_status
from simulators.acu_status.mode_command_status import mode_command_functions
from simulators import utils


class AxisStatus(object):
    def __init__(self,
            n_motors=1,
            max_vel=0,
            max_accel=0,
            op_range=(0, 0),
            stow_pos=None):

        self.max_velocity = max_vel
        self.max_acceleration = max_accel
        self.min_pos = op_range[0]
        self.max_pos = op_range[1]
        if stow_pos:
            self.stow_pos = stow_pos
        else:
            self.stow_pos = [0]
        self.motor_status = []
        self.current_time = 0

        for _ in range(n_motors):
            self.motor_status.append(ms.MotorStatus())

        self.simulation = 0  # BOOL, 0: axis simulation off, 1: on
        self.axis_ready = 0  # BOOL, 0: axis not ready for activating, 1: ready
        self.conf_ok = 0  # BOOL, 0: conf. file read error, 1: read successful
        self.init_ok = 0  # BOOL, 0: faulty conf. data, 1: init. completed
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
        self.p_Soll = int(round(self.stow_pos[0] * 1000000))

        # p_Bahn, INT32, output pos. of the trajectory generator [microdeg]
        self.p_Bahn = 0

        # p_Ist, INT32, actual pos. [microdeg]
        self.p_Ist = int(round(self.stow_pos[0] * 1000000))

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
        self.motor_selection = '1' * n_motors + '0' * (16 - n_motors)

        # brakes_open, WORD
        # in bit mode coded indicator for the brakes that are open
        # 0: brake not open, 1: brake open
        # SRT range: same as motor_selection
        self.brakes_open = '0' * 16

        # power_module_ok, WORD
        # in bit mode coded indicator for the
        # power module concerning each motor
        self.power_module_ok = '0' * 16

        self.stowed = 1  # BOOL, 0: axis not stowed, 1: axis stowed

        # self.stow_pos_ok, BOOL, 0: actual pos. is no stow pos., 1: stow pos.
        self.stow_pos_ok = 1

        # stow_pin_selection, WORD
        # in bit mode coded indicator for the number of stow pins
        # 0: stow pin not selected, 1: stow pin selected
        self.stow_pin_selection = '1' * 16

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
        self.mcs = mode_command_status.ModeCommandStatus()

        # parameter_command_status, refer to ParameterCommandStatus class
        self.pcs = parameter_command_status.ParameterCommandStatus()

        self.run = True
        thread.start_new_thread(self._move, ())

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

    def mode_command(self, cmd):
        cmd_cnt = utils.bytes_to_int(cmd[4:8])
        mode_id = utils.bytes_to_int(cmd[8:10])
        parameter_1 = utils.bytes_to_real(cmd[10:18], 2)
        parameter_2 = utils.bytes_to_real(cmd[18:26], 2)

        command = mode_command_functions.get(mode_id)

        if command is None or command == '_ignore':
            self.mcs.received_mode_command_counter = cmd_cnt
            self.mcs.received_mode_command = 0
            self.mcs.received_command_answer = 0
            return

        recvd_comm_ans = self._validate_mode_command(
            mode_id,
            parameter_1,
            parameter_2)

        self.mcs.received_mode_command_counter = cmd_cnt
        self.mcs.received_mode_command = mode_id
        self.mcs.received_command_answer = recvd_comm_ans

        if recvd_comm_ans == 9:
            # Update mode_command_status for executed command
            self.mcs.executed_mode_command_counter = cmd_cnt
            self.mcs.executed_mode_command = mode_id
            self.mcs.executed_command_answer = 2

            # Call the desired command
            method = getattr(self, command)
            method(parameter_1, parameter_2)

    def _validate_mode_command(self, mode_id, parameter_1, parameter_2):
        received_command_answer = 9  # Command accepted

        if mode_id == 2 and self.axis_state != 0:
            received_command_answer = 4
        elif mode_id in [3, 4, 5, 7, 8, 52] and self.axis_state != 3:
            received_command_answer = 4
        elif mode_id == 15 and self.axis_state not in [0, 1]:
            received_command_answer = 4
        elif mode_id == 50:
            current_pos = int(round(self.p_Ist / 1000000))
            if current_pos not in self.stow_pos or self.v_Ist:
                received_command_answer = 4

        if mode_id == 3:
            desired_pos = int(round(parameter_1))
            delta_pos = desired_pos - int(round((self.p_Ist / 1000000)))

            if utils.sign(delta_pos) != utils.sign(parameter_2):
                # Discordant direction of new position and rate
                received_command_answer = 5
            if desired_pos < self.min_pos or desired_pos > self.max_pos:
                received_command_answer = 5
            if abs(parameter_2) > self.max_velocity:
                received_command_answer = 5
        elif mode_id == 4:
            desired_pos = int(round((self.p_Ist / 1000000) + parameter_1))

            if utils.sign(parameter_1) != utils.sign(parameter_2):
                # Discordant direction of new position and rate
                received_command_answer = 5
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
            if abs(parameter_2) > 0.5 * self.max_velocity:
                received_command_answer = 5

        return received_command_answer

    def parameter_command(self, cmd):
        pass

    # mode_id == 1
    def _inactive(self, *_):
        self.axis_state = 0
        self.brakes_open = '0' * 16
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 2
    def _active(self, *_):
        self.axis_state = 3
        self.brakes_open = (
            '1' * len(self.motor_status)
            + '0' * (16 - len(self.motor_status))
        )
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 3
    def _preset_absolute(self, angle, rate):
        self.p_Soll = int(round(angle * 1000000))
        self.v_Soll = int(round(rate * 1000000))
        return True

    # mode_id == 4
    def _preset_relative(self, angle, rate):
        self.p_Soll += int(round(angle * 1000000))
        self.v_Soll = int(round(rate * 1000000))
        return True

    # mode_id == 5
    def _slew(self, percentage, rate):
        self.v_Soll = int(round(rate * 1000000 * percentage))
        if utils.sign(self.v_Soll) > 0:
            self.p_Soll = int(round(self.max_pos * 1000000))
        elif utils.sign(self.v_Soll) < 0:
            self.p_Soll = int(round(self.min_pos * 1000000))
        else:
            self.p_Soll = self.p_Ist
        return True

    # mode_id == 7
    def _stop(self, *_):
        self.p_Soll = self.p_Ist
        self.v_Soll = 0
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 8
    def _program_track(self, _, rate):
        self.v_Soll = int(round(rate * 1000000))
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 14
    def _interlock(self, *_):
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 15
    def _reset(self, *_):
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
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 50
    def _stow(self, *_):
        self.stow_pin_out = '0' * 16
        self.stow_pin_in = self.stow_pin_selection
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 51
    def _unstow(self, *_):
        self.stow_pin_in = '0' * 16
        self.stow_pin_out = self.stow_pin_selection
        self.mcs.executed_command_answer = 1
        return True

    # mode_id == 52
    def _drive_to_stow(self, stow_position, rate):
        self.p_Soll = int(round(self.stow_pos[int(stow_position)] * 1000000))
        self.v_Soll = int(round(rate * 1000000))
        return True

    def _move(self):
        while self.run:
            current_time = time.time()
            if self.current_time != 0:
                delta_time = current_time - self.current_time
            else:
                delta_time = 0
            self.current_time = current_time
            # delta_time unit is expressed in seconds

            if self.axis_state == 3:
                sign = utils.sign(self.p_Soll - self.p_Ist)
                if sign != 0:
                    current_pos = self.p_Ist
                    # using instantaneous accel. for first implementation
                    current_pos += self.v_Soll * delta_time
                    if self.p_Soll != current_pos:
                        res_sign = utils.sign(self.p_Soll - current_pos)
                        if res_sign != sign:
                            # overshoot, movement completed
                            self.p_Ist = self.p_Soll
                            self.mcs.executed_command_answer = 1
                        else:
                            self.p_Ist = current_pos
                else:
                    self.mcs.executed_command_answer = 1

    def stop(self):
        self.run = False
