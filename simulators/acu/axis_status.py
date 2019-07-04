import time
from multiprocessing import Array
from ctypes import c_char
from simulators import utils
from simulators.acu.motor_status import MotorStatus


class SimpleAxisStatus(object):
    """
    :param n_motors: The number of motors that move the axis.
    """
    def __init__(self, n_motors=1):
        self.motor_status = []

        for __ in range(n_motors):
            self.motor_status.append(MotorStatus())

        self.status = Array(c_char, 92)

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

        self.ptState = 0

    @property
    def simulation(self):
        return bool(utils.bytes_to_uint(self.status[0]))

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
        return bool(utils.bytes_to_uint(self.status[1]))

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
        return bool(utils.bytes_to_uint(self.status[2]))

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
        return bool(utils.bytes_to_uint(self.status[3]))

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
        return bool(utils.bytes_to_uint(self.status[4]))

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
        return bool(utils.bytes_to_uint(self.status[5]))

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
        return bool(utils.bytes_to_uint(self.status[60]))

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
        return bool(utils.bytes_to_uint(self.status[61]))

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
        return str(self.status[68:84])

    @property
    def received_mode_command_status(self):
        return str(self.status[68:76])

    @property
    def received_mode_command_counter(self):
        return utils.bytes_to_uint(str(self.status[68:72]))

    @received_mode_command_counter.setter
    def received_mode_command_counter(self, value):
        # UINT32
        if not isinstance(value, int):
            raise ValueError('Provide an unsigned integer!')
        self.status[68:72] = utils.uint_to_bytes(value, n_bytes=4)

    @property
    def received_mode_command(self):
        return utils.bytes_to_uint(str(self.status[72:74]))

    @received_mode_command.setter
    def received_mode_command(self, value):
        # UINT16
        # 0: ignore
        # 1: inactive
        # 2: active
        # 3: preset_absolute
        # 4: preset_relative
        # 5: slew
        # 7: stop
        # 8: program_track
        # 14: interlock
        # 15: reset
        # 50: stow
        # 51: unstow
        # 52: drive_to_stow
        if not isinstance(value, int):
            raise ValueError('Provide an unsigned integer!')
        self.status[72:74] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def received_mode_command_answer(self):
        return utils.bytes_to_uint(str(self.status[74:76]))

    @received_mode_command_answer.setter
    def received_mode_command_answer(self, value):
        # UINT16
        # 0: no command
        # 4: command received in wrong mode
        # 5: command has invalid parameters
        # 9: command accepted
        accepted = [0, 4, 5, 9]
        if not isinstance(value, int) or value not in accepted:
            raise ValueError('Provide an accepted integer!')
        self.status[74:76] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def executed_mode_command_status(self):
        return str(self.status[76:84])

    @property
    def executed_mode_command_counter(self):
        return utils.bytes_to_uint(str(self.status[76:80]))

    @executed_mode_command_counter.setter
    def executed_mode_command_counter(self, value):
        # UINT32
        if not isinstance(value, int):
            raise ValueError('Provide an unsigned integer!')
        self.status[76:80] = utils.uint_to_bytes(value, n_bytes=4)

    @property
    def executed_mode_command(self):
        return utils.bytes_to_uint(str(self.status[80:82]))

    @executed_mode_command.setter
    def executed_mode_command(self, value):
        # UINT16
        # 0: ignore
        # 1: inactive
        # 2: active
        # 3: preset_absolute
        # 4: preset_relative
        # 5: slew
        # 7: stop
        # 8: program_track
        # 14: interlock
        # 15: reset
        # 50: stow
        # 51: unstow
        # 52: drive_to_stow
        if not isinstance(value, int):
            raise ValueError('Provide an unsigned integer!')
        self.status[80:82] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def executed_mode_command_answer(self):
        return utils.bytes_to_uint(str(self.status[82:84]))

    @executed_mode_command_answer.setter
    def executed_mode_command_answer(self, value):
        # UINT16
        # 0: no command
        # 1: command executed
        # 2: command active
        # 3: command error during execution
        accepted = [0, 1, 2, 3]
        if not isinstance(value, int) or value not in accepted:
            raise ValueError('Provide an accepted integer!')
        self.status[82:84] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def parameter_command_status(self):
        return str(self.status[84:92])

    @property
    def parameter_command_counter(self):
        return utils.bytes_to_uint(str(self.status[84:88]))

    @parameter_command_counter.setter
    def parameter_command_counter(self, value):
        # UINT32
        if not isinstance(value, int):
            raise ValueError('Provide an unsigned integer!')
        self.status[84:88] = utils.uint_to_bytes(value, n_bytes=4)

    @property
    def parameter_command(self):
        return utils.bytes_to_uint(str(self.status[88:90]))

    @parameter_command.setter
    def parameter_command(self, value):
        # UINT16
        # 0: ignore
        # 11: absolute position offset
        # 12: relative position offset
        # 50: time source
        # 51: time offset
        # 60: program track time correction
        # 61: load program track table
        if not isinstance(value, int):
            raise ValueError('Provide an accepted integer!')
        self.status[88:90] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def parameter_command_answer(self):
        return utils.bytes_to_uint(str(self.status[90:92]))

    @parameter_command_answer.setter
    def parameter_command_answer(self, value):
        # UINT16
        # 0: no command
        # 1: command executed
        # 4: command received in wrong mode
        # 5: command has invalid parameters
        accepted = [0, 1, 4, 5]
        if not isinstance(value, int) or value not in accepted:
            raise ValueError('Provide an accepted integer!')
        self.status[90:92] = utils.uint_to_bytes(value, n_bytes=2)


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

        self.next_pos = None

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
            self.Stowpins_Extracted = True
        else:
            self.stow_pin_out = [False for __ in range(16)]
            self.stow_pin_in = self.stow_pin_selection
            self.Stowpins_Extracted = False

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

    def _move(self, counter, desired_pos, desired_rate, stop):
        """This method performs a positioning loop by calling the method
        `_calc_position` every iteration.

        :param counter: the command counter of the positioning action.
            It is used to eventually stop the movement when a different
            command is received.
        :param desired_pos: the commanded (final) position.
        :param desired_rate: the speed rate of the rotation.
        """
        self.p_Soll = desired_pos
        self.v_Soll = desired_rate

        t0 = time.time()
        while not stop.value:
            t1 = time.time()
            delta_time = t1 - t0
            t0 = t1

            current_pos = self._calc_position(
                delta_time,
                desired_pos,
                desired_rate
            )
            if counter == self.curr_mode_counter:
                if self.axis_state == 3 and not self.stowed:
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

    def update_status(self):
        """This method is called to update some of the values before comparison
        or sending."""
        if self.stow_pos:
            self.stowPosOk = float(self.p_Ist) / 1000000 in self.stow_pos
        if self.p_Ist == int(round(self.min_pos * 1000000)):
            self.Pre_Limit_Dn = True
            self.Fin_Limit_Dn = False
        elif self.p_Ist < int(round(self.min_pos * 1000000)):
            self.Pre_Limit_Dn = True
            self.Fin_Limit_Dn = True
        else:
            self.Pre_Limit_Dn = False
            self.Fin_Limit_Dn = False
        if self.p_Ist == int(round(self.max_pos * 1000000)):
            self.Pre_Limit_Up = True
            self.Fin_Limit_Up = False
        elif self.p_Ist > int(round(self.max_pos * 1000000)):
            self.Pre_Limit_Up = True
            self.Fin_Limit_Up = True
        else:
            self.Pre_Limit_Up = False
            self.Fin_Limit_Up = False
        if abs(self.v_Ist) > int(round(self.max_velocity * 1000000)):
            self.Rate_Limit = True
        else:
            self.Rate_Limit = False

    # -------------------- Mode Command --------------------

    def _mode_command(self, cmd, stop):
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

        command = self.mode_commands.get(mode_id)

        if command is None or command == '_ignore':
            self.received_mode_command_counter = cmd_cnt
            self.received_mode_command = 0
            self.received_mode_command_answer = 0
            return

        received_command_answer = self._validate_mode_command(
            mode_id,
            par_1,
            par_2
        )

        self.received_mode_command_counter = cmd_cnt
        self.received_mode_command = mode_id
        self.received_mode_command_answer = received_command_answer

        if received_command_answer == 9:
            method = getattr(self, command)

            self.executed_mode_command_counter = cmd_cnt
            self.executed_mode_command = mode_id
            self.executed_mode_command_answer = 2
            method(cmd_cnt, par_1, par_2, stop)

    def _validate_mode_command(self, mode_id, parameter_1, parameter_2):
        """This method performs a validation check on the received
        mode command. It is called from the `mode_command` method
        to check if a command must be executed or not.

        :param mode_id: the mode_id of the received command.
        :param parameter_1: the first parameter of the received command.
        :param parameter_2: the second parameter of the reveived command.
        """
        received_command_answer = 9  # Command accepted

        axis_state = self.axis_state

        if mode_id == 2 and axis_state != 0:
            received_command_answer = 4
        elif mode_id in [3, 4, 5, 7, 8, 52] and axis_state != 3:
            received_command_answer = 4
        elif mode_id == 15 and axis_state not in [0, 1]:
            received_command_answer = 4  # pragma: no cover
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

    # mode_id == 1
    def _inactive(self, counter, *_):
        """This method de-activate the axis and engage the motors brakes.

        :param counter: the current command counter.
        """
        self.axis_state = 0
        self.brakes_open = [False for __ in range(16)]
        self.v_Ist = 0
        self.v_Soll = 0
        self.executed_mode_command_counter = counter
        self.executed_mode_command = 1
        self.executed_mode_command_answer = 1

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

        self.executed_mode_command_counter = counter
        self.executed_mode_command = 2
        self.executed_mode_command_answer = 1

    # mode_id == 3
    def _preset_absolute(self, counter, angle, rate, stop):
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
        if self._move(counter, desired_pos, desired_rate, stop):
            self.executed_mode_command_counter = counter
            self.executed_mode_command = 3
            self.executed_mode_command_answer = 1

    # mode_id == 4
    def _preset_relative(self, counter, angle, rate, stop):
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
        if self._move(counter, desired_pos, desired_rate, stop):
            self.executed_mode_command_counter = counter
            self.executed_mode_command = 4
            self.executed_mode_command_answer = 1

    # mode_id == 5
    def _slew(self, counter, percentage, rate, stop):
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
        if self._move(counter, desired_pos, desired_rate, stop):
            self.executed_mode_command_counter = counter
            self.executed_mode_command = 5
            self.executed_mode_command_answer = 1

    # mode_id == 7
    def _stop(self, counter, *_):
        """This method stops the axis movement and therefore the execution
        of any positioning or tracking command.

        :param counter: same as the `_inactive` method.
        """
        self.curr_mode_counter = counter
        self.axis_trajectory_state = 3

        self.executed_mode_command_counter = counter
        self.executed_mode_command = 7
        self.executed_mode_command_answer = 1

    # mode_id == 8
    def _program_track(self, counter, _, rate, stop):
        """This method starts the tracking with a pre-loaded trajectory.
        The trajectory is loaded sending a 'program_track_parameter_command'
        to the pointing subsystem of the ACU. Refer to the `PointingStatus`
        class for further documentation.

        :param counter: same as the `_inactive` method.
        :param rate: the maximum rotation rate while tracking.
        """
        self.curr_mode_counter = counter
        self.executed_mode_command_counter = counter
        self.executed_mode_command = 8
        self.executed_mode_command_answer = 1

        self.axis_trajectory_state = 7  # 7: tracking

        t0 = time.time()
        next_pos = None
        final_pos = None
        while (not stop.value
                and self.axis_trajectory_state == 7
                and counter == self.curr_mode_counter):
            t1 = time.time()
            delta_time = t1 - t0
            t0 = t1

            next_pos = self.next_pos

            if next_pos:
                final_pos = next_pos
            elif self.ptState == 4 and self.p_Ist != final_pos and final_pos:
                next_pos = final_pos

            p_Ist = self.p_Ist
            v_Ist = self.v_Ist

            if next_pos and self.axis_state == 3 and not self.stowed:

                if self.ptState == 2:
                    self.p_Soll = self.next_pos + self.p_Offset
                    self.v_Soll = int(round(rate * 1000000))

                    if p_Ist != self.p_Soll:
                        current_pos = self._calc_position(
                            delta_time,
                            self.p_Soll,
                            self.v_Soll
                        )

                        v_Ist = self.v_Soll
                        p_Ist = current_pos

                        if p_Ist == self.p_Soll:
                            v_Ist = 0

                go_on = False
                if self.ptState == 4:
                    self.p_Soll = next_pos + self.p_Offset
                    if self.p_Ist != self.p_Soll:
                        p_Ist = self.p_Ist
                        go_on = True

                if self.ptState == 3 or go_on:
                    self.p_Soll = self.p_Bahn + self.p_Offset

                    calc_position = self._calc_position(
                        delta_time,
                        self.p_Soll,
                        int(round(self.max_velocity * 1000000)),
                    )

                    v_Ist = int(round(
                        (calc_position - p_Ist) / delta_time
                    ))

                    p_Ist = calc_position

            else:
                v_Ist = 0

            self.p_Ist = p_Ist
            v_Ist = max(v_Ist, int(round(-self.max_velocity * 1000000)))
            v_Ist = min(v_Ist, int(round(self.max_velocity * 1000000)))
            self.v_Ist = v_Ist
            self.v_Soll = self.v_Ist

            time.sleep(0.01)

        self.v_Ist = 0

    # mode_id == 14
    def _interlock(self, counter, *_):
        """This method should start an interlock. Currently, it does nothing.

        :param counter: same as the `_inactive` method.
        """
        self.executed_mode_command_counter = counter
        self.executed_mode_command = 14
        self.executed_mode_command_answer = 1

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

        self.executed_mode_command_counter = counter
        self.executed_mode_command = 15
        self.executed_mode_command_answer = 1

    # mode_id == 50
    def _stow(self, counter, *_):
        """This method stows the axis by extending its stow pins.

        :param counter: same as the `_inactive` method.
        """
        if self.stow_pos:
            self.curr_mode_counter = counter
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = [False for __ in range(16)]
            self.Stowpins_Extracted = True
            self.stowed = True
            self.v_Ist = 0
            self.v_Soll = 0

        self.executed_mode_command_counter = counter
        self.executed_mode_command = 50
        self.executed_mode_command_answer = 1

    # mode_id == 51
    def _unstow(self, counter, *_):
        """This method unstows the axis by retracting its stow pins.

        :param counter: same as the `_inactive` method.
        """
        if self.stow_pos:
            self.curr_mode_counter = counter
            self.stow_pin_out = [False for __ in range(16)]
            self.stow_pin_in = self.stow_pin_selection
            self.Stowpins_Extracted = False
            self.stowed = False

        self.executed_mode_command_counter = counter
        self.executed_mode_command = 51
        self.executed_mode_command_answer = 1

    # mode_id == 52
    def _drive_to_stow(self, counter, stow_pos, rate, stop):
        """This method moves the axis to the given stow position
        at a given rate.

        :param counter: same as the `_inactive` method.
        :param stow_pos: the index of the desired stow position.
        :param rate: the desired rotation rate.
        """
        stow_pos = int(stow_pos)
        if self.stow_pos:
            self.curr_mode_counter = counter
            desired_pos = int(round(self.stow_pos[int(stow_pos)] * 1000000))
            desired_rate = int(round(rate * 1000000))
            if not self._move(counter, desired_pos, desired_rate, stop):
                return
            self.stow_pin_out = self.stow_pin_selection
            self.stow_pin_in = [False for __ in range(16)]
            self.Stowpins_Extracted = True
            self.stowed = True
            self.v_Ist = 0
            self.v_Soll = 0

        self.executed_mode_command_counter = counter
        self.executed_mode_command = 52
        self.executed_mode_command_answer = 1

    # -------------------- Parameter Command --------------------

    def _parameter_command(self, cmd, _):
        """This method parses and executes the received parameter command.

        :param cmd: the received command.
        """
        self.parameter_command_counter = utils.bytes_to_uint(cmd[4:8])

        parameter_id = utils.bytes_to_uint(cmd[8:10])
        parameter_1 = utils.bytes_to_real(cmd[10:18], 2)
        parameter_2 = utils.bytes_to_real(cmd[18:26], 2)

        self.parameter_command = parameter_id

        if self.axis_state != 3:
            self.parameter_command_answer = 4
            return

        if parameter_id == 11:
            self.parameter_command_answer = self._absolute_position_offset(
                parameter_1,
                parameter_2
            )
        elif parameter_id == 12:
            self.parameter_command_answer = self._relative_position_offset(
                parameter_1,
                parameter_2
            )
        else:
            self.parameter_command_answer = 5

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

    def update_status(self):
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
