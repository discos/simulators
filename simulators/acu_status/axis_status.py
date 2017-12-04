from simulators.acu_status import parameter_command_status as pcs
from simulators.acu_status import mode_command_status as mcs
from simulators import utils


class AxisStatus(object):

    simulation = 0  # BOOL, 0: axis simulation off, 1: on
    axis_ready = 0  # BOOL, 0: axis not ready for attivating, 1: ready
    conf_ok = 0  # BOOL, 0: configuration file read error, 1: read successful
    init_ok = 0  # BOOL, 0: faulty configuration data, 1: init. completed
    override = 0  # BOOL, 0: override mode not active, 1: active
    low_power = 0  # BOOL, 0: low power mode not active, 1: active

    # Warnings, DWORD, in bit mode coded warning indication
    Param_Fault = 0
    Rate_Mode = 0
    Safety_Chain = 0
    Wrong_Sys_State = 0
    Temp_Enc = 0
    # bit 5 = 0, not used
    Power_Brakes = 0
    Power_Servo = 0
    Fan_Fault = 0
    Servo_DC_Off = 0
    Motor_Temp_Warn = 0
    Servo_DC_Warn = 0
    M_Max_Exceeded = 0
    Pos_Enc_Fault = 0
    # bit 14 = 0, not used
    Em_Limit_Dn = 0
    Em_Limit_Up = 0
    Degraded_Mode = 0
    Override_Act = 0
    Pre_Limit_Up = 0
    Pre_Limit_Dn = 0
    Fin_Limit_Up = 0
    Fin_Limit_Dn = 0
    Rate_Limit = 0
    Stow_Fault = 0
    Stowpins_Extracted = 0
    Low_Power_Act = 0
    # bits 27:28 = 0, not used
    LimDn_inconsist = 0
    LimUp_inconsist = 0
    # bit 31 = 0, not used

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

    # Errors, DWORD, in bit mode coded error indication
    Error_Active = 0
    System_fault = 0
    Em_Stop = 0
    Em_Limit_Dn_Act = 0
    Em_Limit_Up_Act = 0
    # bit 5 = 0, not used
    Brake_Error = 0
    Power_Error = 0
    Servo_Error = 0
    Servo_Timeout = 0
    # bit 10 = 0, not used
    v_Motor_Exceed = 0
    Servo_Overload = 0
    Pos_Enc_Error = 0
    Pos_Enc_Step = 0
    p_Range_Exceed = 0
    p_Dev_Exceed = 0
    Servo_DC_Error = 0
    Override_Error = 0
    Cmd_Timeout = 0
    # bits 20:21 = 0, not used
    Rate_Loop_Err = 0
    v_Dev_Exceed = 0
    Stow_Error = 0
    Stow_Timeout = 0
    Extern_Error = 0
    Safety_Dev_Error = 0
    # bit 28 = 0, not used
    Com_Error = 0
    Pre_Limit_Err = 0
    Fin_Limit_Err = 0

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

    # axis_state, UINT16
    # 0: inactive
    # 1: deactivating
    # 2: activating
    # 3: active
    axis_state = 0

    # axis_trajectory_state, UINT16
    # 0: off
    # 1: holding
    # 2: emergency stop
    # 3: stop
    # 4: slewing velocity
    # 5: N/D
    # 6: position
    # 7: tracking
    axis_trajectory_state = 0

    # p_Soll, INT32, desired position [microdeg]
    p_Soll = 0

    # p_Bahn, INT32, output position of the trajectory generator [microdeg]
    p_Bahn = 0

    # p_Ist, INT32, actual position [microdeg]
    p_Ist = 0

    # p_AbwFil, INT32, filtered position deviation [microdeg]
    p_AbwFil = 0

    # v_Soll, INT32, desired velocity [microdeg/s]
    v_Soll = 0

    # v_Bahn, INT32, output velocity of the trajectory generator [microdeg/s]
    v_Bahn = 0

    # v_Ist, INT32, actual velocity [microdeg/s]
    v_Ist = 0

    # a_Bahn, INT32, output acceleration of the trajectory generator
    # [microdeg/s^2]
    a_Bahn = 0

    # p_Offset, INT32, position offset for tracking mode [microdeg]
    p_Offset = 0

    # motor_selection, WORD
    # in bit mode coded indicator for the selected motors
    motor_selection = '0' * 16

    # brakes_open, WORD
    # in bit mode coded indicator for the brakes that are open
    brakes_open = '0' * 16

    # power_module_ok, WORD
    # in bit mode coded indicator for the power module concerning each motor
    power_module_ok = '0' * 16

    stowed = 0  # BOOL, 0: axis not stowed, 1: axis stowed
    stow_pos_ok = 0  # BOOL, 0: actual position is no stow pos., 1: stow pos.

    # stow_pin_in, WORD
    # in bit mode coded indicator if the stow pins are in
    stow_pin_in = '0' * 16

    # stow_pin_out, WORD
    # in bit mode coded indicator if the stow pins are out
    stow_pin_out = '0' * 16

    # stow_pin_selection, WORD
    # in bit mode coded indicator for the number of stow pins
    stow_pin_selection = '0' * 16

    # mode_command_status, refer to ModeCommandStatus class
    mode_command_status = mcs.ModeCommandStatus()

    # parameter_command_status, refer to ParameterCommandStatus class
    parameter_command_status = pcs.ParameterCommandStatus()  # Refer to

    def get_status(self):
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
            + self.mode_command_status.get_mode_command_status()
            + self.parameter_command_status.get_status()
        )
        return response

    def inactive(self, *_):
        pass

    def active(self, *_):
        pass

    def preset_absolute(self, angle, rate):
        pass

    def preset_relative(self, angle, rate):
        pass

    def slew(self, percentage, rate):
        pass

    def stop(self, *_):
        pass

    def program_track(self, _, rate):
        pass

    def interlock(self, *_):
        pass

    def reset(self, *_):
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

    def stow(self, *_):
        pass

    def unstow(self, *_):
        pass

    def drive_to_stow(self, stow_position, rate):
        pass
