from multiprocessing import Array
from ctypes import c_char
from simulators import utils


class GeneralStatus:
    """General status of the ACU. This status holds generic informations
    about the ACU, like its firmware version, the interlock statuses and
    human-machine interfaces status."""

    def __init__(self):
        self.status = Array(c_char, 25)

        self.version = (1, 0)
        self.master = 2
        self.status_HMI = [False, True, False, False, True, False]
        self.software_IO = False
        self.simulation = False
        self.control_system_on = False
        self.service = False

        # HW_interlock
        self.EStop_Device = False
        self.ES_SP = False
        self.ES_Drive_AZ1_2 = False
        self.ES_Drive_AZ3_4 = False
        self.ES_Drive_AZ5_6 = False
        self.ES_Drive_AZ7_8 = False
        self.ES_Drive_EL1_2 = False
        self.ES_Drive_EL3_4 = False
        self.ES_LCP = False
        self.ES_Cablewrap = False
        self.ES_AER1 = False
        self.ES_AER2 = False
        self.ES_HHP = False
        self.ES_PCP = False
        self.ES_EER = False
        self.ES_EER_Key = False
        self.ES_EER_Door = False
        self.ES_BOX_10 = False
        self.ES_SFR_1 = False
        self.ES_SFR_2 = False

        # SW_interlock
        self.Control_System_Off = False
        self.Power_Control_Sys = False
        self.Power_Drive_Cab = False
        self.Power_Supply_DC = False
        self.Fieldbus_Error = False
        self.Interlock_Cmd = False
        self.SaDev_ES_FbErr = False
        self.SaDev_ES_CommErr = False
        self.SaDev_ES_OutErr = False
        self.SaDev_MD_FbErr = False
        self.SaDev_MD_CommErr = False
        self.SaDev_MD_OutErr = False
        self.Emergency_Stop = False
        self.Power_UPS = False
        self.Power_UPS_Alarm = False
        self.ACU_DI_Power = False
        self.ECU_DI_Power = False
        self.Power_DO_Int = False
        self.Main_Power = False
        self.Overvoltage_Prot = False
        self.Temp_Error_Rack = False

        self.diag_signal = 0

    @property
    def version(self):
        return (
            utils.bytes_to_uint(self.status[1]),
            utils.bytes_to_uint(self.status[0])
        )

    @version.setter
    def version(self, value):
        # UINT16, ACU software version (10 -> v1.0)
        if not isinstance(value, tuple):
            raise ValueError('Provide a tuple containing (major, minor)!')
        major, minor = value
        self.status[0:2] = utils.binary_to_bytes(
            utils.int_to_twos(major, 1) + utils.int_to_twos(minor, 1)
        )

    @property
    def master(self):
        return utils.bytes_to_uint(self.status[2])

    @master.setter
    def master(self, value=2):
        # UINT8, Control of the ACU
        # 0: MT diagnosis
        # 1: Handheld panel active
        # 2: Host (remote) computer (automatic)
        # 3: Local control panel active
        # 4: Primary control panel active
        # 5: Secondary control panel active
        if not isinstance(value, int) or value not in range(6):
            raise ValueError('Provide an integer between 0 and 5!')
        self.status[2] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def status_HMI(self):
        status_HMI = []
        for value in utils.bytes_to_binary(self.status[3:5])[::-1]:
            status_HMI.append(bool(int(value)))
        return status_HMI

    @status_HMI.setter
    def status_HMI(self, value):
        # UINT16, In bit mode coded status of the human machine interfaces
        try:
            if not isinstance(value, (list, tuple)) or len(value) != 6:
                raise ValueError
            for v in value:
                if not isinstance(v, bool):
                    raise ValueError
        except ValueError as ex:
            raise ValueError(
                'Provide a list/tuple of booleans of length = 6!'
            ) from ex

        LCP_connected = int(value[0])
        remote_computer_connected = int(value[1])
        HBG_connected = int(value[2])
        # bit 3 not used
        LCP_initialization_OK = int(value[3])
        remote_initialization_OK = int(value[4])
        HBG_initialization_OK = int(value[5])
        # bits 7:15 not used

        binary_string = str(LCP_connected)
        binary_string += str(remote_computer_connected)
        binary_string += str(HBG_connected)
        binary_string += '0'
        binary_string += str(LCP_initialization_OK)
        binary_string += str(remote_initialization_OK)
        binary_string += str(HBG_initialization_OK)
        binary_string += '0' * 9

        self.status[3:5] = utils.binary_to_bytes(binary_string[::-1])

    @property
    def software_IO(self):
        return bool(utils.bytes_to_uint(self.status[5]))

    @software_IO.setter
    def software_IO(self, value):
        # BOOL, False: LCP inactive, True: active
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[5] = value

    @property
    def simulation(self):
        return bool(utils.bytes_to_uint(self.status[6]))

    @simulation.setter
    def simulation(self, value):
        # BOOL, False: simulation inactive, True: active
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[6] = value

    @property
    def control_system_on(self):
        return bool(utils.bytes_to_uint(self.status[7]))

    @control_system_on.setter
    def control_system_on(self, value):
        # BOOL, False: control system off, True: on
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[7] = value

    @property
    def service(self):
        return bool(utils.bytes_to_uint(self.status[8]))

    @service.setter
    def service(self, value):
        # BOOL, False: service mode off, True: on
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[8] = value

    @property
    def HW_interlock(self):
        return utils.bytes_to_binary(self.status[9:13][::-1])

    @property
    def EStop_Device(self):
        return bool(int(str(self.HW_interlock)[0]))

    @EStop_Device.setter
    def EStop_Device(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[0] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_SP(self):
        return bool(int(str(self.HW_interlock)[1]))

    @ES_SP.setter
    def ES_SP(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[1] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_Drive_AZ1_2(self):
        return bool(int(str(self.HW_interlock)[2]))

    @ES_Drive_AZ1_2.setter
    def ES_Drive_AZ1_2(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[2] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_Drive_AZ3_4(self):
        return bool(int(str(self.HW_interlock)[3]))

    @ES_Drive_AZ3_4.setter
    def ES_Drive_AZ3_4(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[3] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_Drive_AZ5_6(self):
        return bool(int(str(self.HW_interlock)[4]))

    @ES_Drive_AZ5_6.setter
    def ES_Drive_AZ5_6(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[4] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_Drive_AZ7_8(self):
        return bool(int(str(self.HW_interlock)[5]))

    @ES_Drive_AZ7_8.setter
    def ES_Drive_AZ7_8(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[5] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_Drive_EL1_2(self):
        return bool(int(str(self.HW_interlock)[6]))

    @ES_Drive_EL1_2.setter
    def ES_Drive_EL1_2(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[6] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_Drive_EL3_4(self):
        return bool(int(str(self.HW_interlock)[7]))

    @ES_Drive_EL3_4.setter
    def ES_Drive_EL3_4(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[7] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_LCP(self):
        return bool(int(str(self.HW_interlock)[8]))

    @ES_LCP.setter
    def ES_LCP(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[8] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_Cablewrap(self):
        return bool(int(str(self.HW_interlock)[9]))

    @ES_Cablewrap.setter
    def ES_Cablewrap(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[9] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_AER1(self):
        return bool(int(str(self.HW_interlock)[10]))

    @ES_AER1.setter
    def ES_AER1(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[10] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_AER2(self):
        return bool(int(str(self.HW_interlock)[11]))

    @ES_AER2.setter
    def ES_AER2(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[11] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_HHP(self):
        return bool(int(str(self.HW_interlock)[12]))

    @ES_HHP.setter
    def ES_HHP(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[12] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_PCP(self):
        return bool(int(str(self.HW_interlock)[13]))

    @ES_PCP.setter
    def ES_PCP(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[13] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_EER(self):
        return bool(int(str(self.HW_interlock)[14]))

    @ES_EER.setter
    def ES_EER(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[14] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_EER_Key(self):
        return bool(int(str(self.HW_interlock)[15]))

    @ES_EER_Key.setter
    def ES_EER_Key(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[15] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_EER_Door(self):
        return bool(int(str(self.HW_interlock)[16]))

    @ES_EER_Door.setter
    def ES_EER_Door(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[16] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_BOX_10(self):
        return bool(int(str(self.HW_interlock)[17]))

    @ES_BOX_10.setter
    def ES_BOX_10(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[17] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_SFR_1(self):
        return bool(int(str(self.HW_interlock)[18]))

    @ES_SFR_1.setter
    def ES_SFR_1(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[18] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def ES_SFR_2(self):
        return bool(int(str(self.HW_interlock)[19]))

    @ES_SFR_2.setter
    def ES_SFR_2(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        HW_interlock = list(self.HW_interlock)
        HW_interlock[19] = str(int(value))
        self.status[9:13] = utils.binary_to_bytes(''.join(HW_interlock)[::-1])

    @property
    def SW_interlock(self):
        return utils.bytes_to_binary(self.status[13:17][::-1])

    @property
    def Control_System_Off(self):
        return bool(int(str(self.SW_interlock)[0]))

    @Control_System_Off.setter
    def Control_System_Off(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[0] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Power_Control_Sys(self):
        return bool(int(str(self.SW_interlock)[1]))

    @Power_Control_Sys.setter
    def Power_Control_Sys(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[1] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Power_Drive_Cab(self):
        return bool(int(str(self.SW_interlock)[2]))

    @Power_Drive_Cab.setter
    def Power_Drive_Cab(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[2] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Power_Supply_DC(self):
        return bool(int(str(self.SW_interlock)[3]))

    @Power_Supply_DC.setter
    def Power_Supply_DC(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[3] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Fieldbus_Error(self):
        return bool(int(str(self.SW_interlock)[5]))

    @Fieldbus_Error.setter
    def Fieldbus_Error(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[5] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Interlock_Cmd(self):
        return bool(int(str(self.SW_interlock)[6]))

    @Interlock_Cmd.setter
    def Interlock_Cmd(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[6] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def SaDev_ES_FbErr(self):
        return bool(int(str(self.SW_interlock)[7]))

    @SaDev_ES_FbErr.setter
    def SaDev_ES_FbErr(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[7] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def SaDev_ES_CommErr(self):
        return bool(int(str(self.SW_interlock)[8]))

    @SaDev_ES_CommErr.setter
    def SaDev_ES_CommErr(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[8] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def SaDev_ES_OutErr(self):
        return bool(int(str(self.SW_interlock)[9]))

    @SaDev_ES_OutErr.setter
    def SaDev_ES_OutErr(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[9] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def SaDev_MD_FbErr(self):
        return bool(int(str(self.SW_interlock)[10]))

    @SaDev_MD_FbErr.setter
    def SaDev_MD_FbErr(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[10] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def SaDev_MD_CommErr(self):
        return bool(int(str(self.SW_interlock)[11]))

    @SaDev_MD_CommErr.setter
    def SaDev_MD_CommErr(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[11] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def SaDev_MD_OutErr(self):
        return bool(int(str(self.SW_interlock)[12]))

    @SaDev_MD_OutErr.setter
    def SaDev_MD_OutErr(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[12] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Emergency_Stop(self):
        return bool(int(str(self.SW_interlock)[13]))

    @Emergency_Stop.setter
    def Emergency_Stop(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[13] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Power_UPS(self):
        return bool(int(str(self.SW_interlock)[15]))

    @Power_UPS.setter
    def Power_UPS(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[15] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Power_UPS_Alarm(self):
        return bool(int(str(self.SW_interlock)[16]))

    @Power_UPS_Alarm.setter
    def Power_UPS_Alarm(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[16] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def ACU_DI_Power(self):
        return bool(int(str(self.SW_interlock)[17]))

    @ACU_DI_Power.setter
    def ACU_DI_Power(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[17] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def ECU_DI_Power(self):
        return bool(int(str(self.SW_interlock)[18]))

    @ECU_DI_Power.setter
    def ECU_DI_Power(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[18] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Power_DO_Int(self):
        return bool(int(str(self.SW_interlock)[19]))

    @Power_DO_Int.setter
    def Power_DO_Int(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[19] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Main_Power(self):
        return bool(int(str(self.SW_interlock)[20]))

    @Main_Power.setter
    def Main_Power(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[20] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Overvoltage_Prot(self):
        return bool(int(str(self.SW_interlock)[21]))

    @Overvoltage_Prot.setter
    def Overvoltage_Prot(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[21] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def Temp_Error_Rack(self):
        return bool(int(str(self.SW_interlock)[22]))

    @Temp_Error_Rack.setter
    def Temp_Error_Rack(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        SW_interlock = list(self.SW_interlock)
        SW_interlock[22] = str(int(value))
        self.status[13:17] = utils.binary_to_bytes(''.join(SW_interlock)[::-1])

    @property
    def diag_signal(self):
        return utils.bytes_to_real(self.status[17:25], precision=2)

    @diag_signal.setter
    def diag_signal(self, value):
        # REAL64, signal output of the function generator [deg]
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[17:25] = utils.real_to_bytes(value, precision=2)
