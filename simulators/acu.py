#!/usr/bin/python
import time
import thread
import Queue
from simulators.common import BaseSystem


class ModeCommandStatus(object):

    received_mode_command_counter = 0  # UINT32
    received_mode_command = 0  # UINT16
    received_command_answer = 0  # UINT16
    executed_mode_command_counter = 0  # UINT32
    executed_mode_command = 0  # UINT16
    executed_command_answer = 0  # UINT16

    def get_mode_command_status(self):
        response = (
            bin(self.received_mode_command_counter)[2:].zfill(32)
            + bin(self.received_mode_command)[2:].zfill(16)
            + bin(self.received_command_answer)[2:].zfill(16)
            + bin(self.executed_mode_command_counter)[2:].zfill(32)
            + bin(self.executed_mode_command)[2:].zfill(16)
            + bin(self.executed_command_answer)[2:].zfill(16)
        )
        return response


class ParameterCommandStatus(object):

    parameter_command_counter = 0  # UINT32, command serial number
    parameter_command = 0  # UINT16
    parameter_command_answer = 0  # UINT16

    def get_parameter_command_status(self):
        response = (
            bin(self.parameter_command_counter)[2:].zfill(32)
            + bin(self.parameter_command)[2:].zfill(16)
            + bin(self.parameter_command_answer)[2:].zfill(16)
        )
        return response


class GeneralStatus(object):

    version = (0x00 * 0x100) + 0x00  # UINT16
    master = 0  # UINT8
    status_HMI = 0  # UINT16
    software_IO = 0  # BOOL
    simulation = 0  # BOOL
    control_system = 0  # BOOL
    service = 0  # BOOL

    # HW_interlock

    EStop_Device = 0
    ES_SP = 0
    ES_Drive_AZ1_2 = 0
    ES_Drive_AZ3_4 = 0
    ES_Drive_AZ5_6 = 0
    ES_Drive_AZ7_8 = 0
    ES_Drive_EL1_2 = 0
    ES_Drive_EL3_4 = 0
    ES_LCP = 0
    ES_Cablewrap = 0
    ES_AER1 = 0  # Stairs
    ES_AER2 = 0  # Lift
    ES_HHP = 0
    ES_PCP = 0
    ES_EER = 0
    ES_EER_Key = 0
    ES_EER_Door = 0
    ES_BOX_10 = 0
    ES_SFR_1 = 0
    ES_SFR_2 = 0
    # bits 20:31 = 0, not used

    # SW_interlock

    Control_System_Off = 0
    Power_Control_Sys = 0
    Power_Drive_Cab = 0
    Power_Supply_DC = 0
    # bit 4 = 0, not used
    Fieldbus_Error = 0
    Interlock_Cmd = 0
    SaDev_ES_FbErr = 0
    SaDev_ES_CommErr = 0
    SaDev_ES_OutErr = 0
    SaDev_MD_FbErr = 0
    SaDev_MD_CommErr = 0
    SaDev_MD_OutErr = 0
    Emergency_Stop = 0
    # bit 14 = 0, not used
    Power_UPS = 0
    Power_UPS_Alarm = 0
    ACU_DI_Power = 0
    ECU_DI_Power = 0
    Power_DO_Int = 0
    Main_Power = 0
    Overvoltage_Prot = 0
    Temp_Error_Rack = 0
    # bits 23:31 = 0, not used

    diag_signal = 0  # REAL64

    def get_general_status(self):
        response = (
            bin(self.version)[2:].zfill(16)
            + bin(self.master)[2:].zfill(8)
            + bin(self.status_HMI)[2:].zfill(16)
            + bin(self.software_IO)[2:].zfill(8)
            + bin(self.simulation)[2:].zfill(8)
            + bin(self.control_system)[2:].zfill(8)
            + bin(self.service)[2:].zfill(8)
            + self.get_hw_interlock()
            + self.get_sw_interlock()
            + bin(self.diag_signal)[2:].zfill(64)
        )
        return response

    def get_hw_interlock(self):
        response = (
            str(self.EStop_Device)
            + str(self.ES_SP)
            + str(self.ES_Drive_AZ1_2)
            + str(self.ES_Drive_AZ3_4)
            + str(self.ES_Drive_AZ5_6)
            + str(self.ES_Drive_AZ7_8)
            + str(self.ES_Drive_EL1_2)
            + str(self.ES_Drive_EL3_4)
            + str(self.ES_LCP)
            + str(self.ES_Cablewrap)
            + str(self.ES_AER1)  # Stairs
            + str(self.ES_AER2)  # Lift
            + str(self.ES_HHP)
            + str(self.ES_PCP)
            + str(self.ES_EER)
            + str(self.ES_EER_Key)
            + str(self.ES_EER_Door)
            + str(self.ES_BOX_10)
            + str(self.ES_SFR_1)
            + str(self.ES_SFR_2)
            + '000000000000'
        )
        return response

    def get_sw_interlock(self):
        response = (
            str(self.Control_System_Off)
            + str(self.Power_Control_Sys)
            + str(self.Power_Drive_Cab)
            + str(self.Power_Supply_DC)
            + '0'
            + str(self.Fieldbus_Error)
            + str(self.Interlock_Cmd)
            + str(self.SaDev_ES_FbErr)
            + str(self.SaDev_ES_CommErr)
            + str(self.SaDev_ES_OutErr)
            + str(self.SaDev_MD_FbErr)
            + str(self.SaDev_MD_CommErr)
            + str(self.SaDev_MD_OutErr)
            + str(self.Emergency_Stop)
            + '0'
            + str(self.Power_UPS)
            + str(self.Power_UPS_Alarm)
            + str(self.ACU_DI_Power)
            + str(self.ECU_DI_Power)
            + str(self.Power_DO_Int)
            + str(self.Main_Power)
            + str(self.Overvoltage_Prot)
            + str(self.Temp_Error_Rack)
            + '000000000'
        )
        return response


class AxisStatus(object):

    simulation = 0  # BOOL
    axis_ready = 0  # BOOL
    conf_ok = 0  # BOOL
    init_ok = 0  # BOOL
    override = 0  # BOOL
    low_power = 0  # BOOL

    # Warnings

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

    # Errors

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

    axis_state = 0  # UINT16
    axis_trajectory_state = 0  # UINT16
    p_Soll = 0  # INT32
    p_Bahn = 0  # INT32
    p_Ist = 0  # INT32
    p_AbwFil = 0  # INT32
    v_Soll = 0  # INT32
    v_Bahn = 0  # INT32
    v_Ist = 0  # INT32
    a_Bahn = 0  # INT32
    p_Offset = 0  # INT32
    motor_selection = 0  # WORD
    brakes_open = 0  # WORD
    power_module_ok = 0  # WORD
    stowed = 0  # BOOL
    stow_pos_ok = 0  # BOOL
    stow_pin_in = 0  # WORD
    stow_pin_out = 0  # WORD
    stow_pin_selection = 0  # WORD
    mode_command_status = ModeCommandStatus()
    parameter_command_status = ParameterCommandStatus()

    def get_axis_status(self):
        response = (
            bin(self.simulation)[2:].zfill(8)
            + bin(self.axis_ready)[2:].zfill(8)
            + bin(self.conf_ok)[2:].zfill(8)
            + bin(self.init_ok)[2:].zfill(8)
            + bin(self.override)[2:].zfill(8)
            + bin(self.low_power)[2:].zfill(8)
            + self.get_warnings()
            + self.get_errors()
            + bin(self.axis_state)[2:].zfill(16)
            + bin(self.axis_trajectory_state)[2:].zfill(16)
            + bin(self.p_Soll)[2:].zfill(32)
            + bin(self.p_Bahn)[2:].zfill(32)
            + bin(self.p_Ist)[2:].zfill(32)
            + bin(self.p_AbwFil)[2:].zfill(32)
            + bin(self.v_Soll)[2:].zfill(32)
            + bin(self.v_Bahn)[2:].zfill(32)
            + bin(self.v_Ist)[2:].zfill(32)
            + bin(self.a_Bahn)[2:].zfill(32)
            + bin(self.p_Offset)[2:].zfill(32)
            + bin(self.motor_selection)[2:].zfill(16)
            + bin(self.brakes_open)[2:].zfill(16)
            + bin(self.power_module_ok)[2:].zfill(16)
            + bin(self.stowed)[2:].zfill(8)
            + bin(self.stow_pos_ok)[2:].zfill(8)
            + bin(self.stow_pin_in)[2:].zfill(16)
            + bin(self.stow_pin_out)[2:].zfill(16)
            + bin(self.stow_pin_selection)[2:].zfill(16)
            + self.mode_command_status.get_mode_command_status()
            + self.parameter_command_status.get_parameter_command_status()
        )
        return response

    def get_warnings(self):
        response = (
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
            + '00'
            + str(self.LimDn_inconsist)
            + str(self.LimUp_inconsist)
            + '0'
        )
        return response

    def get_errors(self):
        response = (
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
            + '00'
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
        return response


class MotorStatus(object):

    Actual_Position = 0  # REAL32
    Actual_Velocity = 0  # REAL32
    Actual_Torque = 0  # REAL32
    Rate_Of_Utilization = 0  # REAL32
    Active = 0  # UINT8
    Speed_Of_Rotation = 0  # UINT8
    Speed_Of_Rotation_Ok = 0  # UINT8
    Position = 0  # UINT8
    Bus = 0  # UINT8
    Servo = 0  # UINT8
    Sensor = 0  # UINT8

    # Motor Warning Codes

    wa_iQuad_t = 0
    wa_Temp_Amplifier = 0
    wa_Temp_Mot = 0
    wa_v_Max_Exceeded = 0
    wa_M_Max_Exceeded = 0
    wa_Mot_Overload = 0
    wa_Temp_Cooling = 0
    wa_Temp_Extern = 0
    wa_Temp_Pow_Supply = 0
    wa_Temp_ERM_Module = 0
    wa_U_Max = 0
    wa_U_Min = 0
    wa_Intermed_Circ_Voltage = 0
    wa_Wrong_Mode = 0
    wa_err_cmd_M = 0
    wa_err_sts_SBM = 0
    wa_err_sts_EF = 0
    wa_err_sts_RF = 0
    # bits 18:31 = 0, not used

    def get_motor_status(self):
        response = (
            bin(self.Actual_Position)[2:].zfill(32)
            + bin(self.Actual_Velocity)[2:].zfill(32)
            + bin(self.Actual_Torque)[2:].zfill(32)
            + bin(self.Rate_Of_Utilization)[2:].zfill(32)
            + bin(self.Active)[2:].zfill(8)
            + bin(self.Speed_Of_Rotation)[2:].zfill(8)
            + bin(self.Speed_Of_Rotation_Ok)[2:].zfill(8)
            + bin(self.Position)[2:].zfill(8)
            + bin(self.Bus)[2:].zfill(8)
            + bin(self.Servo)[2:].zfill(8)
            + bin(self.Sensor)[2:].zfill(8)
            + self.get_warnings()
        )
        return response

    def get_warnings(self):
        response = (
            str(self.wa_iQuad_t)
            + str(self.wa_Temp_Amplifier)
            + str(self.wa_Temp_Mot)
            + str(self.wa_v_Max_Exceeded)
            + str(self.wa_M_Max_Exceeded)
            + str(self.wa_Mot_Overload)
            + str(self.wa_Temp_Cooling)
            + str(self.wa_Temp_Extern)
            + str(self.wa_Temp_Pow_Supply)
            + str(self.wa_Temp_ERM_Module)
            + str(self.wa_U_Max)
            + str(self.wa_U_Min)
            + str(self.wa_Intermed_Circ_Voltage)
            + str(self.wa_Wrong_Mode)
            + str(self.wa_err_cmd_M)
            + str(self.wa_err_sts_SBM)
            + str(self.wa_err_sts_EF)
            + str(self.wa_err_sts_RF)
            + '00000000000000'
        )
        return response


class PointingStatus(object):

    confVersion = 0  # REAL64
    confOk = 0  # BOOL
    posEncAz = 0  # INT32
    pointOffsetAz = 0  # INT32
    posCalibChartAz = 0  # INT32
    posCorrTableAz_F_plst_El = 0  # INT32
    posCorrTableAzOn = 0  # BOOL
    encAzFault = 0  # BOOL
    sectorSwitchAz = 0  # BOOL
    posEncEl = 0  # INT32
    pointOffsetEl = 0  # INT32
    posCalibChartEl = 0  # INT32
    posCorrTableEl_F_plst_Az = 0  # INT32
    posCorrTableElOn = 0  # BOOL
    encElFault = 0  # UINT8
    posEncCw = 0  # INT32
    posCalibChartCw = 0  # INT32
    encCwFault = 0  # UINT8
    timeSource = 0  # UINT16
    actTime = 0  # REAL64
    actTimeOffset = 0  # REAL64
    clockOnline = 0  # UINT8
    clockOK = 0  # UINT8
    year = 0  # UINT16
    month = 0  # UINT16
    day = 0  # UINT16
    hour = 0  # UINT16
    minute = 0  # UINT16
    second = 0  # UINT16
    actPtPos_Azimuth = 0  # INT32
    actPtPos_Elevation = 0  # INT32
    ptState = 0  # UINT16

    # Errors

    Data_Overflow = 0
    Time_Distance_Fault = 0
    No_Data_Available = 0
    # bits 3:5 = 0, reserved
    # bits 6:15 = 0, not used

    actTimeOffset = 0  # INT32
    ptInterpolMode = 0  # UINT16
    ptTrackingType = 0  # UINT16
    ptTrackingMode = 0  # UINT16
    ptActTableIndex = 0  # UINT32
    ptEndTableIndex = 0  # UINT32
    ptTableLength = 0  # UINT32
    parameter_command_status = ParameterCommandStatus()

    def get_pointing_status(self):
        response = (
            bin(self.confVersion)[2:].zfill(64)
            + bin(self.confOk)[2:].zfill(8)
            + bin(self.posEncAz)[2:].zfill(32)
            + bin(self.pointOffsetAz)[2:].zfill(32)
            + bin(self.posCalibChartAz)[2:].zfill(32)
            + bin(self.posCorrTableAz_F_plst_El)[2:].zfill(32)
            + bin(self.posCorrTableAzOn)[2:].zfill(8)
            + bin(self.encAzFault)[2:].zfill(8)
            + bin(self.sectorSwitchAz)[2:].zfill(8)
            + bin(self.posEncEl)[2:].zfill(32)
            + bin(self.pointOffsetEl)[2:].zfill(32)
            + bin(self.posCalibChartEl)[2:].zfill(32)
            + bin(self.posCorrTableEl_F_plst_Az)[2:].zfill(32)
            + bin(self.posCorrTableElOn)[2:].zfill(8)
            + bin(self.encElFault)[2:].zfill(8)
            + bin(self.posEncCw)[2:].zfill(32)
            + bin(self.posCalibChartCw)[2:].zfill(32)
            + bin(self.encCwFault)[2:].zfill(8)
            + bin(self.timeSource)[2:].zfill(16)
            + bin(self.actTime)[2:].zfill(64)
            + bin(self.actTimeOffset)[2:].zfill(64)
            + bin(self.clockOnline)[2:].zfill(8)
            + bin(self.clockOK)[2:].zfill(8)
            + bin(self.year)[2:].zfill(16)
            + bin(self.month)[2:].zfill(16)
            + bin(self.day)[2:].zfill(16)
            + bin(self.hour)[2:].zfill(16)
            + bin(self.minute)[2:].zfill(16)
            + bin(self.second)[2:].zfill(16)
            + bin(self.actPtPos_Azimuth)[2:].zfill(32)
            + bin(self.actPtPos_Elevation)[2:].zfill(32)
            + bin(self.ptState)[2:].zfill(16)
            + self.get_errors()
            + bin(self.actTimeOffset)[2:].zfill(32)
            + bin(self.ptInterpolMode)[2:].zfill(16)
            + bin(self.ptTrackingType)[2:].zfill(16)
            + bin(self.ptTrackingMode)[2:].zfill(16)
            + bin(self.ptActTableIndex)[2:].zfill(32)
            + bin(self.ptEndTableIndex)[2:].zfill(32)
            + bin(self.ptTableLength)[2:].zfill(32)
            + self.parameter_command_status.get_parameter_command_status()
        )
        return response

    def get_errors(self):
        response = (
            str(self.Data_Overflow)
            + str(self.Time_Distance_Fault)
            + str(self.No_Data_Available)
            + '000'  # reserved
            + '0000000000'  # not used
        )
        return response


class FacilityStatus(object):

    voltagePhToPh = 0  # REAL64
    currentPhToPh = 0  # REAL64

    def get_facility_status(self):
        response = (
            bin(self.voltagePhToPh)[2:].zfill(64)
            + bin(self.currentPhToPh)[2:].zfill(64)
        )
        return response


class ACUStatus(object):

    def __init__(self):
        self.GS = GeneralStatus()
        self.AzAS = AxisStatus()
        self.ElAS = AxisStatus()
        self.AzCWAS = AxisStatus()
        self.AzMS = MotorStatus()
        self.ElMS = MotorStatus()
        self.AzCWMS = MotorStatus()
        self.PS = PointingStatus()
        self.FS = FacilityStatus()

    def get_status(self):
        response_string = (
            self.GS.get_general_status()
            + self.AzAS.get_axis_status()
            + self.ElAS.get_axis_status()
            + self.AzCWAS.get_axis_status()
            + self.AzMS.get_motor_status()
            + self.ElMS.get_motor_status()
            + self.AzCWMS.get_motor_status()
            + self.PS.get_pointing_status()
            + self.FS.get_facility_status()
        )

        response = b''

        for i in range(0, len(response_string), 8):
            response += chr(int(response_string[i:i + 8], 2))

        return response


class System(BaseSystem):

    start_flag = b'\x1D\xFC\xCF\x1A'  #: Message header
    end_flag = b'\xA1\xFC\xCF\xD1'  #: Message tail

    def __init__(self, queue_sampling_time=0.2, n=None):
        """
        param queue_sampling_time: seconds between the sending of consecutive
        status messages
        param n: maximum number of status messages to put in the queue
        """
        self.status = ACUStatus()
        self.status_counter = 0  #: Number of total status messages sent
        self._set_default()
        self.msg_queue = Queue.Queue()
        self.start_status_thread(queue_sampling_time, n)

    def start_status_thread(self, queue_sampling_time, n):
        thread.start_new_thread(
            self._enqueue_status_msg,
            (queue_sampling_time, n,)
        )

    def _set_default(self):
        self.msg = b''
        self.msg_length = 0
        self.cmd_counter = 0
        self.cmds_counter = 0

    def parse(self, byte):
        self.msg += byte

        while self.msg and len(self.msg) <= 4:
            if self.msg != self.start_flag[:len(self.msg)]:
                self.msg = self.msg[1:]
            else:
                break

        if not self.msg:
            return False

        if len(self.msg) == 8:
            self.msg_length = (
                ord(self.msg[-4]) * 0x1000000
                + ord(self.msg[-3]) * 0x10000
                + ord(self.msg[-2]) * 0x100
                + ord(self.msg[-1])
            )

        if len(self.msg) == 12:
            self.cmd_counter = (
                ord(self.msg[-4]) * 0x1000000
                + ord(self.msg[-3]) * 0x10000
                + ord(self.msg[-2]) * 0x100
                + ord(self.msg[-1])
            )

        if len(self.msg) == 16:
            self.cmds_counter = (
                ord(self.msg[-4]) * 0x1000000
                + ord(self.msg[-3]) * 0x10000
                + ord(self.msg[-2]) * 0x100
                + ord(self.msg[-1])
            )

        if len(self.msg) > 16 and len(self.msg) == self.msg_length:
            msg = self.msg
            self._set_default()
            if msg[-4:] == self.end_flag:
                return self._parser(msg)
            else:
                raise ValueError(
                    "Wrong end flag: got %s, expected %s."
                    % (msg[-4:], self.end_flag)
                )

        return True

    def _parser(self, msg):
        return [hex(ord(x)) for x in msg]

    def _enqueue_status_msg(self, queue_sampling_time, n):
        """
        param n: maximum number of status messages to put in the queue
        """
        while n is not None:
            self.msg_queue.put(self.get_status())
            if self.status_counter == n:
                break
            time.sleep(queue_sampling_time)

    def get_status(self):
        status = self.status.get_status()
        msg_length = bin(len(status) + 12)[2:].zfill(32)
        msg_counter = bin(self.status_counter)[2:].zfill(32)
        self.status_counter += 1

        message = self.start_flag

        for i in range(0, len(msg_length), 8):
            message += chr(int(msg_length[i:i + 8], 2))

        for i in range(0, len(msg_counter), 8):
            message += chr(int(msg_counter[i:i + 8], 2))

        message += status + self.end_flag
        return message

    def message_queue(self):
        queue = []
        while not self.msg_queue.empty():
            queue.append(self.msg_queue.get_nowait())
        return queue
