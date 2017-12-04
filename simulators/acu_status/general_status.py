from simulators import utils


class GeneralStatus(object):

    # Version, UINT16, ACU software version (10 -> v1.0)
    major_version = 1
    minor_version = 0

    def _version(self):
        binary_version = (
            utils.int_to_twos(self.major_version, 1)
            + utils.int_to_twos(self.minor_version, 1)
        )
        return utils.binary_to_bytes(binary_version)

    # master, UINT8, Control of the ACU
    # 0: MT diagnosis
    # 1: Handheld panel active
    # 2: Host (remote) computer (automatic)
    # 3: Local control panel active
    # 4: Primary control panel active
    # 5: Secondary control panel active
    master = 0

    # Status HMI, UINT16
    # In bit mode coded status of the human machine interfaces
    LCP_connected = 0               # bit 0
    remote_computer_connected = 0   # bit 1
    HBG_connected = 0               # bit 2
    #                               # bit 3 not used
    LCP_initialization_OK = 0       # bit 4
    remote_initialization_OK = 0    # bit 5
    HBG_initialization_OK = 0       # bit 6
    #                               # bits 7:15 not used

    def _status_hmi(self):
        binary_string = (
            str(self.LCP_connected)
            + str(self.remote_computer_connected)
            + str(self.HBG_connected)
            + '0'
            + str(self.LCP_initialization_OK)
            + str(self.remote_initialization_OK)
            + str(self.HBG_initialization_OK)
            + '0' * 9
        )
        return utils.binary_to_bytes(binary_string)

    software_IO = 0  # BOOL, 0: LCP inactive, 1: active
    simulation = 0  # BOOL, 0: simulation inactive, 1: active
    control_system = 0  # BOOL, 0: control system off, 1: on
    service = 0  # BOOL, 0: service mode off, 1: on

    # HW_interlock, DWORD, in bit mode coded HW interlock
    EStop_Device = 0
    ES_SP = 0  # Box 40
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

    def _hardware_interlock(self):
        binary_string = (
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
            + '0' * 12
        )
        return utils.binary_to_bytes(binary_string)

    # SW_interlock, DWORD, in bit mode coded SW interlock
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

    def _software_interlock(self):
        binary_string = (
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
            + '0' * 9
        )
        return utils.binary_to_bytes(binary_string)

    diag_signal = 0  # REAL64, signal output of the function generator [deg]

    def get_status(self):
        return (self._version()
                + utils.uint_to_bytes(self.master, 1)
                + self._status_hmi()
                + chr(self.software_IO)
                + chr(self.simulation)
                + chr(self.control_system)
                + chr(self.service)
                + self._hardware_interlock()
                + self._software_interlock()
                + utils.real_to_bytes(self.diag_signal, 2))
