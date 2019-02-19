import time
from simulators import utils
from simulators.acu.motor_status import MotorStatus
from simulators.acu.command_status import (
    CommandStatus,
    ModeCommandStatus,
    ParameterCommandStatus
)


class SimpleAxisStatus(object):
    """
    :param n_motors: The number of motors that move the axis.
    """
    def __init__(self, n_motors=1):
        self.motor_status = []

        for __ in range(n_motors):
            self.motor_status.append(MotorStatus())

        self.status = bytearray(b'\x00' * 92)

        self.simulation = False
        self.axis_ready = True
        self.confOk = True
        self.initOk = True
        self.override = False
        self.low_power_mode = False

        # Warnings, DWORD, in bit mode coded warning indication
        self.Param_Fault = False
        self.Rate_Mode = False
        self.Safety_Chain = False
        self.Wrong_Sys_State = False
        self.Temp_Enc = False
        # bit 5 = 0, not used
        self.Power_Brakes = False
        self.Power_Servo = False
        self.Fan_Fault = False
        self.Servo_DC_Off = False
        self.Motor_Temp_Warn = False
        self.Servo_DC_Warn = False
        self.M_Max_Exceeded = False
        self.Pos_Enc_Fault = False
        # bit 14 = 0, not used
        self.Em_Limit_Dn = False
        self.Em_Limit_Up = False
        self.Degraded_Mode = False
        self.Override_Act = False
        self.Pre_Limit_Up = False
        self.Pre_Limit_Dn = False
        self.Fin_Limit_Up = False
        self.Fin_Limit_Dn = False
        self.Rate_Limit = False
        self.Stow_Fault = False
        self.Stowpins_Extracted = False
        self.Low_Power_Act = False
        # bits 27:28 = 0, not used
        self.LimDn_inconsist = False
        self.LimUp_inconsist = False
        # bit 31 = 0, not used

        # Errors, DWORD, in bit mode coded error indication
        self.Error_Active = False
        self.System_fault = False
        self.Em_Stop = False
        self.Em_Limit_Dn_Act = False
        self.Em_Limit_Up_Act = False
        # bit 5 = 0, not used
        self.Brake_Error = False
        self.Power_Error = False
        self.Servo_Error = False
        self.Servo_Timeout = False
        # bit 10 = 0, not used
        self.v_Motor_Exceed = False
        self.Servo_Overload = False
        self.Pos_Enc_Error = False
        self.Pos_Enc_Step = False
        self.p_Range_Exceed = False
        self.p_Dev_Exceed = False
        self.Servo_DC_Error = False
        self.Override_Error = False
        self.Cmd_Timeout = False
        # bits 20:21 = 0, not used
        self.Rate_Loop_Err = False
        self.v_Dev_Exceed = False
        self.Stow_Error = False
        self.Stow_Timeout = False
        self.Extern_Error = False
        self.Safety_Dev_Error = False
        # bit 28 = 0, not used
        self.Com_Error = False
        self.Pre_Limit_Err = False
        self.Fin_Limit_Err = False

        self.axis_state = 0
        self.axis_trajectory_state = 0
        self.p_Soll = 0
        self.p_Bahn = 0
        self.p_Ist = 0
        self.p_AbwFil = 0
        self.v_Soll = 0
        self.v_Bahn = 0
        self.v_Ist = 0
        self.a_Bahn = 0
        self.p_Offset = 0

        # SRT range: 0:8 for Azimuth, 0:4 for Elevation, 0:1 for Cable Wrap
        motor_selection = [False for __ in range(16)]
        for index in range(n_motors):
            motor_selection[index] = True
        self.motor_selection = motor_selection

        # SRT range: same as motor_selection
        self.brakes_open = [False for __ in range(16)]

        self.power_module_ok = self.motor_selection
        self.stowed = False
        self.stowPosOk = False
        self.stow_pin_in = [False for __ in range(16)]
        self.stow_pin_out = [False for __ in range(16)]
        self.stow_pin_selection = [False for __ in range(16)]

        # mode_command_status, refer to ModeCommandStatus class
        self.mcs = ModeCommandStatus()

        # parameter_command_status, refer to ParameterCommandStatus class
        self.pcs = ParameterCommandStatus()

    def get_axis_status(self):
        self.mode_command_status = self.mcs.get_status()
        self.parameter_command_status = self.pcs.get_status()
        return str(self.status)

    def get_motor_status(self):
        response = ''
        for motor_status in self.motor_status:
            response += motor_status.get_status()
        return response

    @property
    def simulation(self):
        return bool(self.status[0])

    @simulation.setter
    def simulation(self, value):
        # BOOL
        # False: axis simulation off
        # True: axis in simulation mode
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[0] = chr(int(value))

    @property
    def axis_ready(self):
        return bool(self.status[1])

    @axis_ready.setter
    def axis_ready(self, value):
        # BOOL
        # False: axis not ready for activating
        # True: axis ready for activating
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[1] = chr(int(value))

    @property
    def confOk(self):
        return bool(self.status[2])

    @confOk.setter
    def confOk(self, value):
        # BOOL
        # False: configuration file read error
        # True: configuration file is read successfully
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[2] = chr(int(value))

    @property
    def initOk(self):
        return bool(self.status[3])

    @initOk.setter
    def initOk(self, value):
        # BOOL
        # False: configuration data are faulty
        # True: initialization of axis completed
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[3] = chr(int(value))

    @property
    def override(self):
        return bool(self.status[4])

    @override.setter
    def override(self, value):
        # BOOL
        # False: override mode not active
        # True: axis is in override mode
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[4] = chr(int(value))

    @property
    def low_power_mode(self):
        return bool(self.status[5])

    @low_power_mode.setter
    def low_power_mode(self, value):
        # BOOL
        # False: low power mode is not active
        # True: low power mode is active
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[5] = chr(int(value))

    @property
    def warnings(self):
        return utils.bytes_to_binary(str(self.status[6:10]))[::-1]

    @property
    def Param_Fault(self):
        return bool(int(self.warnings[0]))

    @Param_Fault.setter
    def Param_Fault(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[0] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Rate_Mode(self):
        return bool(int(self.warnings[1]))

    @Rate_Mode.setter
    def Rate_Mode(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[1] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Safety_Chain(self):
        return bool(int(self.warnings[2]))

    @Safety_Chain.setter
    def Safety_Chain(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[2] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Wrong_Sys_State(self):
        return bool(int(self.warnings[3]))

    @Wrong_Sys_State.setter
    def Wrong_Sys_State(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[3] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Temp_Enc(self):
        return bool(int(self.warnings[4]))

    @Temp_Enc.setter
    def Temp_Enc(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[4] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Power_Brakes(self):
        return bool(int(self.warnings[6]))

    @Power_Brakes.setter
    def Power_Brakes(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[6] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Power_Servo(self):
        return bool(int(self.warnings[7]))

    @Power_Servo.setter
    def Power_Servo(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[7] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Fan_Fault(self):
        return bool(int(self.warnings[8]))

    @Fan_Fault.setter
    def Fan_Fault(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[8] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Servo_DC_Off(self):
        return bool(int(self.warnings[9]))

    @Servo_DC_Off.setter
    def Servo_DC_Off(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[9] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Motor_Temp_Warn(self):
        return bool(int(self.warnings[10]))

    @Motor_Temp_Warn.setter
    def Motor_Temp_Warn(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[10] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Servo_DC_Warn(self):
        return bool(int(self.warnings[11]))

    @Servo_DC_Warn.setter
    def Servo_DC_Warn(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[11] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def M_Max_Exceeded(self):
        return bool(int(self.warnings[12]))

    @M_Max_Exceeded.setter
    def M_Max_Exceeded(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[12] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Pos_Enc_Fault(self):
        return bool(int(self.warnings[13]))

    @Pos_Enc_Fault.setter
    def Pos_Enc_Fault(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[13] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Em_Limit_Dn(self):
        return bool(int(self.warnings[15]))

    @Em_Limit_Dn.setter
    def Em_Limit_Dn(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[15] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Em_Limit_Up(self):
        return bool(int(self.warnings[16]))

    @Em_Limit_Up.setter
    def Em_Limit_Up(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[16] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Degraded_Mode(self):
        return bool(int(self.warnings[17]))

    @Degraded_Mode.setter
    def Degraded_Mode(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[17] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Override_Act(self):
        return bool(int(self.warnings[18]))

    @Override_Act.setter
    def Override_Act(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[18] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Pre_Limit_Up(self):
        return bool(int(self.warnings[19]))

    @Pre_Limit_Up.setter
    def Pre_Limit_Up(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[19] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Pre_Limit_Dn(self):
        return bool(int(self.warnings[20]))

    @Pre_Limit_Dn.setter
    def Pre_Limit_Dn(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[20] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Fin_Limit_Up(self):
        return bool(int(self.warnings[21]))

    @Fin_Limit_Up.setter
    def Fin_Limit_Up(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[21] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Fin_Limit_Dn(self):
        return bool(int(self.warnings[22]))

    @Fin_Limit_Dn.setter
    def Fin_Limit_Dn(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[22] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Rate_Limit(self):
        return bool(int(self.warnings[23]))

    @Rate_Limit.setter
    def Rate_Limit(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[23] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Stow_Fault(self):
        return bool(int(self.warnings[24]))

    @Stow_Fault.setter
    def Stow_Fault(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[24] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Stowpins_Extracted(self):
        return bool(int(self.warnings[25]))

    @Stowpins_Extracted.setter
    def Stowpins_Extracted(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[25] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def Low_Power_Act(self):
        return bool(int(self.warnings[26]))

    @Low_Power_Act.setter
    def Low_Power_Act(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[26] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def LimDn_inconsist(self):
        return bool(int(self.warnings[29]))

    @LimDn_inconsist.setter
    def LimDn_inconsist(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[29] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def LimUp_inconsist(self):
        return bool(int(self.warnings[30]))

    @LimUp_inconsist.setter
    def LimUp_inconsist(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        warnings = bytearray(self.warnings)
        warnings[30] = str(int(value))
        self.status[6:10] = utils.binary_to_bytes(str(warnings)[::-1])

    @property
    def errors(self):
        return utils.bytes_to_binary(str(self.status[10:14]))[::-1]

    @property
    def Error_Active(self):
        return bool(int(self.errors[0]))

    @Error_Active.setter
    def Error_Active(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[0] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def System_fault(self):
        return bool(int(self.errors[1]))

    @System_fault.setter
    def System_fault(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[1] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Em_Stop(self):
        return bool(int(self.errors[2]))

    @Em_Stop.setter
    def Em_Stop(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[2] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Em_Limit_Dn_Act(self):
        return bool(int(self.errors[3]))

    @Em_Limit_Dn_Act.setter
    def Em_Limit_Dn_Act(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[3] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Em_Limit_Up_Act(self):
        return bool(int(self.errors[4]))

    @Em_Limit_Up_Act.setter
    def Em_Limit_Up_Act(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[4] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Brake_Error(self):
        return bool(int(self.errors[6]))

    @Brake_Error.setter
    def Brake_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[6] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Power_Error(self):
        return bool(int(self.errors[7]))

    @Power_Error.setter
    def Power_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[7] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Servo_Error(self):
        return bool(int(self.errors[8]))

    @Servo_Error.setter
    def Servo_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[8] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Servo_Timeout(self):
        return bool(int(self.errors[9]))

    @Servo_Timeout.setter
    def Servo_Timeout(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[9] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def v_Motor_Exceed(self):
        return bool(int(self.errors[11]))

    @v_Motor_Exceed.setter
    def v_Motor_Exceed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[11] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Servo_Overload(self):
        return bool(int(self.errors[12]))

    @Servo_Overload.setter
    def Servo_Overload(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[12] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Pos_Enc_Error(self):
        return bool(int(self.errors[13]))

    @Pos_Enc_Error.setter
    def Pos_Enc_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[13] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Pos_Enc_Step(self):
        return bool(int(self.errors[14]))

    @Pos_Enc_Step.setter
    def Pos_Enc_Step(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[14] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def p_Range_Exceed(self):
        return bool(int(self.errors[15]))

    @p_Range_Exceed.setter
    def p_Range_Exceed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[15] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def p_Dev_Exceed(self):
        return bool(int(self.errors[16]))

    @p_Dev_Exceed.setter
    def p_Dev_Exceed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[16] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Servo_DC_Error(self):
        return bool(int(self.errors[17]))

    @Servo_DC_Error.setter
    def Servo_DC_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[17] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Override_Error(self):
        return bool(int(self.errors[18]))

    @Override_Error.setter
    def Override_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[18] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Cmd_Timeout(self):
        return bool(int(self.errors[19]))

    @Cmd_Timeout.setter
    def Cmd_Timeout(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[19] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Rate_Loop_Err(self):
        return bool(int(self.errors[22]))

    @Rate_Loop_Err.setter
    def Rate_Loop_Err(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[22] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def v_Dev_Exceed(self):
        return bool(int(self.errors[23]))

    @v_Dev_Exceed.setter
    def v_Dev_Exceed(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[23] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Stow_Error(self):
        return bool(int(self.errors[24]))

    @Stow_Error.setter
    def Stow_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[24] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Stow_Timeout(self):
        return bool(int(self.errors[25]))

    @Stow_Timeout.setter
    def Stow_Timeout(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[25] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Extern_Error(self):
        return bool(int(self.errors[26]))

    @Extern_Error.setter
    def Extern_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[26] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Safety_Dev_Error(self):
        return bool(int(self.errors[27]))

    @Safety_Dev_Error.setter
    def Safety_Dev_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[27] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Com_Error(self):
        return bool(int(self.errors[29]))

    @Com_Error.setter
    def Com_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[29] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Pre_Limit_Err(self):
        return bool(int(self.errors[30]))

    @Pre_Limit_Err.setter
    def Pre_Limit_Err(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[30] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def Fin_Limit_Err(self):
        return bool(int(self.errors[31]))

    @Fin_Limit_Err.setter
    def Fin_Limit_Err(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        errors = bytearray(self.errors)
        errors[31] = str(int(value))
        self.status[10:14] = utils.binary_to_bytes(str(errors)[::-1])

    @property
    def axis_state(self):
        return utils.bytes_to_uint(str(self.status[14:16]))

    @axis_state.setter
    def axis_state(self, value):
        # UINT16
        # 0: inactive
        # 1: deactivating
        # 2: activating
        # 3: active
        if not isinstance(value, int) or value not in range(4):
            raise ValueError('Provide an integer beween 0 and 3!')
        self.status[14:16] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def axis_trajectory_state(self):
        return utils.bytes_to_uint(str(self.status[16:18]))

    @axis_trajectory_state.setter
    def axis_trajectory_state(self, value):
        # UINT16
        # 0: off
        # 1: holding
        # 2: emergency stop
        # 3: stop
        # 4: slewing velocity
        # 6: position
        # 7: tracking
        if not isinstance(value, int) or value not in range(5) + [6, 7]:
            raise ValueError(
                'Provide an integer beween [0, 1, 2, 3, 4, 6, 7]!'
            )
        self.status[16:18] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def p_Soll(self):
        return utils.bytes_to_int(str(self.status[18:22]))

    @p_Soll.setter
    def p_Soll(self, value):
        # INT32, Desired position [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[18:22] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def p_Bahn(self):
        return utils.bytes_to_int(str(self.status[22:26]))

    @p_Bahn.setter
    def p_Bahn(self, value):
        # INT32, Output position of the trajectory generator [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[22:26] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def p_Ist(self):
        return utils.bytes_to_int(str(self.status[26:30]))

    @p_Ist.setter
    def p_Ist(self, value):
        # INT32, Actual position [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[26:30] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def p_AbwFil(self):
        return utils.bytes_to_int(str(self.status[30:34]))

    @p_AbwFil.setter
    def p_AbwFil(self, value):
        # INT32, Filtered position deviation [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[30:34] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def v_Soll(self):
        return utils.bytes_to_int(str(self.status[34:38]))

    @v_Soll.setter
    def v_Soll(self, value):
        # INT32, Desired velocity [microdeg/s]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[34:38] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def v_Bahn(self):
        return utils.bytes_to_int(str(self.status[38:42]))

    @v_Bahn.setter
    def v_Bahn(self, value):
        # INT32, Output velocity of the trajectory generator [microdeg/s]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[38:42] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def v_Ist(self):
        return utils.bytes_to_int(str(self.status[42:46]))

    @v_Ist.setter
    def v_Ist(self, value):
        # INT32, Actual velocity [microdeg/s]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[42:46] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def a_Bahn(self):
        return utils.bytes_to_int(str(self.status[46:50]))

    @a_Bahn.setter
    def a_Bahn(self, value):
        # INT32, Output accel. of the trajectory generator [microdeg/s^2]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[46:50] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def p_Offset(self):
        return utils.bytes_to_int(str(self.status[50:54]))

    @p_Offset.setter
    def p_Offset(self, value):
        # INT32, Position offset for tracking mode [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[50:54] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def motor_selection(self):
        motor_selection = []
        for motor in utils.bytes_to_binary(str(self.status[54:56]))[::-1]:
            motor_selection.append(bool(int(motor)))
        return motor_selection

    @motor_selection.setter
    def motor_selection(self, value):
        # WORD: In bit mode coded indicator for the selected motors
        try:
            if not isinstance(value, (list, tuple)) or len(value) != 16:
                raise ValueError
            else:
                for motor in value:
                    if not isinstance(motor, bool):
                        raise ValueError
        except ValueError:
            raise ValueError(
                'Provide a list/tuple of booleans of length = 16!'
            )
        motor_selection = ''
        for motor in value:
            motor_selection += str(int(motor))
        self.status[54:56] = utils.binary_to_bytes(motor_selection[::-1])

    @property
    def brakes_open(self):
        brakes_open = []
        for brake in utils.bytes_to_binary(str(self.status[56:58]))[::-1]:
            brakes_open.append(bool(int(brake)))
        return brakes_open

    @brakes_open.setter
    def brakes_open(self, value):
        # WORD: In bit mode coded indicator for the brakes that are open
        try:
            if not isinstance(value, (list, tuple)) or len(value) != 16:
                raise ValueError
            else:
                for motor in value:
                    if not isinstance(motor, bool):
                        raise ValueError
        except ValueError:
            raise ValueError(
                'Provide a list/tuple of booleans of length = 16!'
            )
        brakes_open = ''
        for brake in value:
            brakes_open += str(int(brake))
        self.status[56:58] = utils.binary_to_bytes(brakes_open[::-1])

    @property
    def power_module_ok(self):
        power_module_ok = []
        power_modules = utils.bytes_to_binary(str(self.status[58:60]))[::-1]
        for power_module in power_modules:
            power_module_ok.append(bool(int(power_module)))
        return power_module_ok

    @power_module_ok.setter
    def power_module_ok(self, value):
        # WORD: In bit mode coded indicator for
        # the power module concerning each motor
        try:
            if not isinstance(value, (list, tuple)) or len(value) != 16:
                raise ValueError
            else:
                for motor in value:
                    if not isinstance(motor, bool):
                        raise ValueError
        except ValueError:
            raise ValueError(
                'Provide a list/tuple of booleans of length = 16!'
            )
        power_module_ok = ''
        for power_module in value:
            power_module_ok += str(int(power_module))
        self.status[58:60] = utils.binary_to_bytes(power_module_ok[::-1])

    @property
    def stowed(self):
        return bool(self.status[60])

    @stowed.setter
    def stowed(self, value):
        # BOOL
        # False: axis not stowed
        # True: axis stowed
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[60] = chr(int(value))

    @property
    def stowPosOk(self):
        return bool(self.status[61])

    @stowPosOk.setter
    def stowPosOk(self, value):
        # BOOL
        # False: actual position is no stow position
        # True: actual position is stow position
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[61] = chr(int(value))

    @property
    def stow_pin_in(self):
        stow_pin_in = []
        for stow_pin in utils.bytes_to_binary(str(self.status[62:64]))[::-1]:
            stow_pin_in.append(bool(int(stow_pin)))
        return stow_pin_in

    @stow_pin_in.setter
    def stow_pin_in(self, value):
        # WORD: In bit mode coded indicator if the stow pins are in
        try:
            if not isinstance(value, (list, tuple)) or len(value) != 16:
                raise ValueError
            else:
                for motor in value:
                    if not isinstance(motor, bool):
                        raise ValueError
        except ValueError:
            raise ValueError(
                'Provide a list/tuple of booleans of length = 16!'
            )
        stow_pin_in = ''
        for stow_pin in value:
            stow_pin_in += str(int(stow_pin))
        self.status[62:64] = utils.binary_to_bytes(stow_pin_in[::-1])

    @property
    def stow_pin_out(self):
        stow_pin_out = []
        for stow_pin in utils.bytes_to_binary(str(self.status[64:66]))[::-1]:
            stow_pin_out.append(bool(int(stow_pin)))
        return stow_pin_out

    @stow_pin_out.setter
    def stow_pin_out(self, value):
        # WORD: In bit mode coded indicator if the stow pins are out
        try:
            if not isinstance(value, (list, tuple)) or len(value) != 16:
                raise ValueError
            else:
                for motor in value:
                    if not isinstance(motor, bool):
                        raise ValueError
        except ValueError:
            raise ValueError(
                'Provide a list/tuple of booleans of length = 16!'
            )
        stow_pin_out = ''
        for stow_pin in value:
            stow_pin_out += str(int(stow_pin))
        self.status[64:66] = utils.binary_to_bytes(stow_pin_out[::-1])

    @property
    def stow_pin_selection(self):
        stow_pin_selection = []
        for stow_pin in utils.bytes_to_binary(str(self.status[66:68]))[::-1]:
            stow_pin_selection.append(bool(int(stow_pin)))
        return stow_pin_selection

    @stow_pin_selection.setter
    def stow_pin_selection(self, value):
        # WORD: In bit mode coded indicator for the number of stow pins
        try:
            if not isinstance(value, (list, tuple)) or len(value) != 16:
                raise ValueError
            else:
                for motor in value:
                    if not isinstance(motor, bool):
                        raise ValueError
        except ValueError:
            raise ValueError(
                'Provide a list/tuple of booleans of length = 16!'
            )
        stow_pin_selection = ''
        for stow_pin in value:
            stow_pin_selection += str(int(stow_pin))
        self.status[66:68] = utils.binary_to_bytes(stow_pin_selection[::-1])

    @property
    def mode_command_status(self):
        return str(self.status[68:84])[::-1]

    @mode_command_status.setter
    def mode_command_status(self, value):
        if not isinstance(value, (str, bytearray)) or len(value) != 16:
            raise ValueError('Provide a string/bytearray of length = 16!')
        self.status[68:84] = value

    @property
    def parameter_command_status(self):
        return str(self.status[84:92])[::-1]

    @parameter_command_status.setter
    def parameter_command_status(self, value):
        if not isinstance(value, (str, bytearray)) or len(value) != 8:
            raise ValueError('Provide a string/bytearray of length = 8!')
        self.status[84:92] = value


class MasterAxisStatus(SimpleAxisStatus):
    """
    :param n_motors: The number of motors that move the axis.
    :param max_rates: A tuple containing the maximum speed and
        the maximum accelation rates of the axis.
    :param op_range: A tuple containing the minimum and maximum values
        to which the axis can go. [degrees]
    :param start_pos: The starting position of the axis.
    :param stop_pos: A list of stow positions of the axis.
        Default value is None since an axis could not have a stow position.
    """
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
            stow_pin_selection = []
            stow_pin_selection += [
                True for __ in range(len(self.stow_pos))
            ]
            stow_pin_selection += [
                False for __ in range(16 - len(self.stow_pos))
            ]
            self.stow_pin_selection = stow_pin_selection

            if float(self.p_Ist) / 1000000 in self.stow_pos:
                self.stowed = True
                self.stowPosOk = True

        if self.stowed:
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = [False for __ in range(16)]
        else:
            self.stow_pin_out = [False for __ in range(16)]
            self.stow_pin_in = self.stow_pin_selection

    def _calc_position(self, delta_time, desired_pos, desired_rate):
        """This method calculates the current position of the axis
        from the given parameters.

        :param delta_time: the time elapsed since the previous iteration.
        :param desired_pos: the commanded (final) position.
        :param desired_rate: the speed rate of the rotation.
        """
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
        """This method performs a positioning loop by calling the method
        `_calc_position` every iteration.

        :param counter: the command counter of the positioning action.
            It is used to eventually stop the movement when a different
            command is received.
        :param desired_pos: the commanded (final) position.
        :param desired_rate: the speed rate of the rotation.
        :param pt_counter: the command counter of the eventual program track
            command. Similarly to the `counter` param, it is used to
            eventually stop the movement of the axis when a different
            program track command is received.
        """
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
        """This method is called to update some of the values before comparison
        or sending."""
        if self.stow_pos:
            self.stowPosOk = float(self.p_Ist) / 1000000 in self.stow_pos

        if (self.mcs.executed.counter == self.curr_mode_counter
                and self.mcs.executed.answer == 1):
            self.curr_mode_counter = None

        self._update_trajectory_values()

    def _update_trajectory_values(self):
        """This method retrieves the trajectory status and values from the
        pointing module of the ACU simulator."""
        data = self.pointing.get_trajectory_values(self)
        pt_status, pos, vel, acc = data
        self.p_Bahn = pos if pos is not None else self.p_Bahn
        self.v_Bahn = vel if vel is not None else self.v_Bahn
        self.a_Bahn = acc if acc is not None else self.a_Bahn
        return pt_status

    def get_axis_status(self):
        """This method overrides the one from `SimpleAxisStatus` class, from
        which the `MasterAxisStatus` class is inherited. Before calling the
        base `get_axis_status` method, it calls the `_update_status` method
        to update the necessary values to be sent to the caller."""
        self._update_status()

        return SimpleAxisStatus.get_axis_status(self)

    # -------------------- Mode Command --------------------

    def _mode_command(self, cmd):
        """This method parses and executes the received mode command.
        Before launching the command execution, this method calls the
        `_validate_mode_command` method and retrieves its return value.
        Depending on the retrieved value, the parsed command gets
        executed (valid command) or not (invalid command).

        :param cmd: the received mode command.
        """
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
        """This method performs a validation check on the received
        mode command. It is called from the `mode_command` method
        to check if a command must be executed or not.

        :param mode_id: the mode_id of the received command.
        :param parameter_1: the first parameter of the received command.
        :param parameter_2: the second parameter of the reveived command.
        """
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
            if not self.stowPosOk:
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
        """This method updates the last executed mode command
        (`mcs.executed`).

        :param counter: the last executed command counter.
        :param command: the last executed mode id.
        :param answer: the last executed command answer.
        """
        executed = CommandStatus()
        executed.counter = counter
        executed.command = command
        executed.answer = answer
        self.mcs.executed = executed

    # mode_id == 1
    def _inactive(self, counter, *_):
        """This method de-activate the axis and engage the motors brakes.

        :param counter: the current command counter.
        """
        self.axis_state = 0
        self.brakes_open = [False for __ in range(16)]
        self._executed_mode_command(counter, 1, 1)

    # mode_id == 2
    def _active(self, counter, *_):
        """This method activate the axis and disengage the motors brakes.

        :param counter: same as the `_inactive` method.
        """
        self.axis_state = 3

        brakes_open = []
        brakes_open += [
            True for __ in range(len(self.motor_status))
        ]
        brakes_open += [
            False for __ in range(16 - len(self.motor_status))
        ]
        self.brakes_open = brakes_open

        self._executed_mode_command(counter, 2, 1)

    # mode_id == 3
    def _preset_absolute(self, counter, angle, rate):
        """This method moves the axis to a given position,
        moving at a given rate.

        :param counter: same as the `_inactive` method.
        :param angle: the final absolute position of the axis.
        :param rate: the maximum rotation speed of the axis.
        """
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 6
        desired_pos = int(round(angle * 1000000))
        desired_rate = int(round(rate * 1000000))
        if self._move(counter, desired_pos, desired_rate):
            self._executed_mode_command(counter, 3, 1)

    # mode_id == 4
    def _preset_relative(self, counter, angle, rate):
        """This method moves the axis by a given offset,
        moving at a given rate.

        :param counter: same as the `_inactive` method.
        :param angle: the angle to be added to the current angle,
            to which the axis should move.
        :param rate: the maximum rotation speed of the axis.
        """
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 6
        desired_pos = self.p_Soll + int(round(angle * 1000000))
        desired_rate = int(round(rate * 1000000))
        if self._move(counter, desired_pos, desired_rate):
            self._executed_mode_command(counter, 4, 1)

    # mode_id == 5
    def _slew(self, counter, percentage, rate):
        """This method moves the axis at a given rate, multiplied by
        a given percentage.

        :param counter: same as the `_inactive` method.
        :param percentage: the percentage by which the rate is multiplied.
        :param rate: the desired rotation rate.
        """
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
        """This method stops the axis movement and therefore the execution
        of any positioning or tracking command.

        :param counter: same as the `_inactive` method.
        """
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 3
        self._executed_mode_command(counter, 7, 1)

    # mode_id == 8
    def _program_track(self, counter, _, rate):
        """This method starts the tracking with a pre-loaded trajectory.
        The trajectory is loaded sending a 'program_track_parameter_command'
        to the pointing subsystem of the ACU. Refer to the `PointingStatus`
        class for further documentation.

        :param counter: same as the `_inactive` method.
        :param rate: the maximum rotation rate while tracking.
        """
        self.curr_mode_counter = counter
        self._executed_mode_command(counter, 8, 1)

        self.axis_trajectory_state = 7  # 7: tracking

        t0 = time.time()
        next_pos = None
        while self.axis_trajectory_state == 7:
            t1 = time.time()
            delta_time = t1 - t0
            t0 = t1

            program_track_state = self._update_trajectory_values()
            next_p = self.pointing.get_next_position(self)
            if next_p:
                next_pos = next_p

            if next_pos:
                if program_track_state == 2:
                    if self.p_Ist != next_pos + self.p_Offset:
                        self._move(
                            counter,
                            next_pos,
                            int(round(rate * 1000000)),
                            self.pointing.pt_command_id
                        )

                if program_track_state == 4:
                    if self.p_Ist != next_pos + self.p_Offset:
                        self.p_Bahn = next_pos
                        program_track_state = 3

                if program_track_state == 3:
                    desired_pos = self.p_Bahn + self.p_Offset

                    calc_position = self._calc_position(
                        delta_time,
                        desired_pos,
                        int(round(self.max_velocity * 1000000)),
                    )

                    self.v_Ist = int(round(
                        (calc_position - self.p_Ist) / delta_time
                    ))

                    self.p_Ist = calc_position

            time.sleep(0.01)

    # mode_id == 14
    def _interlock(self, counter, *_):
        """This method should start an interlock. Currently, it does nothing.

        :param counter: same as the `_inactive` method.
        """
        self._executed_mode_command(counter, 14, 1)

    # mode_id == 15
    def _reset(self, counter, *_):
        """This method resets the errors of the axis to their default value.

        :param counter: same as the `_inactive` method.
        """
        self.Error_Active = False
        self.System_fault = False
        self.Em_Stop = False
        self.Em_Limit_Dn_Act = False
        self.Em_Limit_Up_Act = False
        self.Brake_Error = False
        self.Power_Error = False
        self.Servo_Error = False
        self.Servo_Timeout = False
        self.v_Motor_Exceed = False
        self.Servo_Overload = False
        self.Pos_Enc_Error = False
        self.Pos_Enc_Step = False
        self.p_Range_Exceed = False
        self.p_Dev_Exceed = False
        self.Servo_DC_Error = False
        self.Override_Error = False
        self.Cmd_Timeout = False
        self.Rate_Loop_Err = False
        self.v_Dev_Exceed = False
        self.Stow_Error = False
        self.Stow_Timeout = False
        self.Extern_Error = False
        self.Safety_Dev_Error = False
        self.Com_Error = False
        self.Pre_Limit_Err = False
        self.Fin_Limit_Err = False
        self._executed_mode_command(counter, 15, 1)

    # mode_id == 50
    def _stow(self, counter, *_):
        """This method stows the axis by extending its stow pins.

        :param counter: same as the `_inactive` method.
        """
        if self.stow_pos:
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = [False for __ in range(16)]
            self.stowed = True
        self._executed_mode_command(counter, 50, 1)

    # mode_id == 51
    def _unstow(self, counter, *_):
        """This method unstows the axis by retracting its stow pins.

        :param counter: same as the `_inactive` method.
        """
        if self.stow_pos:
            self.stow_pin_out = [False for __ in range(16)]
            self.stow_pin_in = self.stow_pin_selection
            self.stowed = False
        self._executed_mode_command(counter, 51, 1)

    # mode_id == 52
    def _drive_to_stow(self, counter, stow_pos, rate):
        """This method moves the axis to the given stow position
        at a given rate.

        :param counter: same as the `_inactive` method.
        :param stow_pos: the index of the desired stow position.
        :param rate: the desired rotation rate.
        """
        stow_pos = int(stow_pos)
        if self.stow_pos:
            desired_pos = int(round(self.stow_pos[int(stow_pos)] * 1000000))
            desired_rate = int(round(rate * 1000000))
            self.curr_mode_counter = counter
            if not self._move(counter, desired_pos, desired_rate):
                return
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = [False for __ in range(16)]
            self.stowed = True
        self._executed_mode_command(counter, 52, 1)

    # -------------------- Parameter Command --------------------

    def _parameter_command(self, cmd):
        """This method parses and executes the received parameter command.

        :param cmd: the received command.
        """
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
            brakes_open = []

            brakes_open += [
                True for __ in range(len(self.motor_status))
            ]
            brakes_open += [
                False for __ in range(16 - len(self.motor_status))
            ]
            self.brakes_open = brakes_open
        else:
            self.brakes_open = [False for __ in range(16)]

        return SimpleAxisStatus.get_axis_status(self)
