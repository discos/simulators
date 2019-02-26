from multiprocessing import Array
from ctypes import c_char
from simulators import utils


class MotorStatus(object):
    """This class holds the status of a generic axis motor."""

    def __init__(self):
        self.status = Array(c_char, 27)

        self.actual_position = 0
        self.actual_velocity = 0
        self.actual_torque = 0
        self.rate_of_utilization = 0
        self.active = 1
        self.speed_of_rotation = 0
        self.speed_of_rotation_OK = 1
        self.position = 0
        self.bus = 0
        self.servo = 0
        self.sensor = 0

        # motWarnCode, DWORD, in bit mode coded warning status of the motor
        self.wa_iQuad_t = False
        self.wa_Temp_Amplifier = False
        self.wa_Temp_Mot = False
        self.wa_v_Max_Exceeded = False
        self.wa_M_Max_Exceeded = False
        self.wa_Mot_Overload = False
        self.wa_Temp_Cooling = False
        self.wa_Temp_Extern = False
        self.wa_Temp_Pow_Supply = False
        self.wa_Temp_ERM_Module = False
        self.wa_U_Max = False
        self.wa_U_Min = False
        self.wa_Intermed_Circ_Voltage = False
        self.wa_Wrong_Mode = False
        self.wa_err_cmd_M = False
        self.wa_err_sts_SBM = False
        self.wa_err_sts_EF = False
        self.wa_err_sts_RF = False
        # bits 18:31 = 0, not used

    @property
    def actual_position(self):
        return utils.bytes_to_real(self.status[0:4], precision=1)

    @actual_position.setter
    def actual_position(self, value):
        # REAL32, actual position [rot]
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[0:4] = utils.real_to_bytes(value, precision=1)

    @property
    def actual_velocity(self):
        return utils.bytes_to_real(self.status[4:8], precision=1)

    @actual_velocity.setter
    def actual_velocity(self, value):
        # REAL32, actual velocity [rot/min]
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[4:8] = utils.real_to_bytes(value, precision=1)

    @property
    def actual_torque(self):
        return utils.bytes_to_real(self.status[8:12], precision=1)

    @actual_torque.setter
    def actual_torque(self, value):
        # REAL32, actual torque [Nm]
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[8:12] = utils.real_to_bytes(value, precision=1)

    @property
    def rate_of_utilization(self):
        return utils.bytes_to_real(self.status[12:16], precision=1)

    @rate_of_utilization.setter
    def rate_of_utilization(self, value):
        # REAL32, rate of utilization [+/- 200%]
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[12:16] = utils.real_to_bytes(value, precision=1)

    @property
    def active(self):
        return utils.bytes_to_uint(str(self.status[16]))

    @active.setter
    def active(self, value):
        # UINT8, 0: motor inactive, 1: motor active
        if not isinstance(value, int) or value not in range(2):
            raise ValueError('Provide an integer between 0 and 1!')
        self.status[16] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def speed_of_rotation(self):
        return utils.bytes_to_uint(str(self.status[17]))

    @speed_of_rotation.setter
    def speed_of_rotation(self, value):
        # UINT8, 0: speed of rotation unequal 0, 1: speed of rotation equal 0
        if not isinstance(value, int) or value not in range(2):
            raise ValueError('Provide an integer between 0 and 1!')
        self.status[17] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def speed_of_rotation_OK(self):
        return utils.bytes_to_uint(str(self.status[18]))

    @speed_of_rotation_OK.setter
    def speed_of_rotation_OK(self, value):
        # UINT8, 0: speed of rotation failure, 1: speed of rotation ok
        if not isinstance(value, int) or value not in range(2):
            raise ValueError('Provide an integer between 0 and 1!')
        self.status[18] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def position(self):
        return utils.bytes_to_uint(str(self.status[19]))

    @position.setter
    def position(self, value):
        # UINT8, 0: desired position not reached, 1: desired position reached
        if not isinstance(value, int) or value not in range(2):
            raise ValueError('Provide an integer between 0 and 1!')
        self.status[19] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def bus(self):
        return utils.bytes_to_uint(str(self.status[20]))

    @bus.setter
    def bus(self, value):
        # UINT8, 0: bus ok, 1: bus error
        if not isinstance(value, int) or value not in range(2):
            raise ValueError('Provide an integer between 0 and 1!')
        self.status[20] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def servo(self):
        return utils.bytes_to_uint(str(self.status[21]))

    @servo.setter
    def servo(self, value):
        # UINT8, 0: servo ok, 1: servo error
        if not isinstance(value, int) or value not in range(2):
            raise ValueError('Provide an integer between 0 and 1!')
        self.status[21] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def sensor(self):
        return utils.bytes_to_uint(str(self.status[22]))

    @sensor.setter
    def sensor(self, value):
        # UINT8, 0: sensor ok, 1: sensor error
        if not isinstance(value, int) or value not in range(2):
            raise ValueError('Provide an integer between 0 and 1!')
        self.status[22] = utils.uint_to_bytes(value, n_bytes=1)

    @property
    def motWarnCode(self):
        return utils.bytes_to_binary(str(self.status[23:27]))[::-1]

    @property
    def wa_iQuad_t(self):
        return bool(int(self.motWarnCode[0]))

    @wa_iQuad_t.setter
    def wa_iQuad_t(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[0] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Temp_Amplifier(self):
        return bool(int(self.motWarnCode[1]))

    @wa_Temp_Amplifier.setter
    def wa_Temp_Amplifier(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[1] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Temp_Mot(self):
        return bool(int(self.motWarnCode[2]))

    @wa_Temp_Mot.setter
    def wa_Temp_Mot(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[2] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_v_Max_Exceeded(self):
        return bool(int(self.motWarnCode[3]))

    @wa_v_Max_Exceeded.setter
    def wa_v_Max_Exceeded(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[3] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_M_Max_Exceeded(self):
        return bool(int(self.motWarnCode[4]))

    @wa_M_Max_Exceeded.setter
    def wa_M_Max_Exceeded(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[4] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Mot_Overload(self):
        return bool(int(self.motWarnCode[5]))

    @wa_Mot_Overload.setter
    def wa_Mot_Overload(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[5] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Temp_Cooling(self):
        return bool(int(self.motWarnCode[6]))

    @wa_Temp_Cooling.setter
    def wa_Temp_Cooling(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[6] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Temp_Extern(self):
        return bool(int(self.motWarnCode[7]))

    @wa_Temp_Extern.setter
    def wa_Temp_Extern(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[7] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Temp_Pow_Supply(self):
        return bool(int(self.motWarnCode[8]))

    @wa_Temp_Pow_Supply.setter
    def wa_Temp_Pow_Supply(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[8] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Temp_ERM_Module(self):
        return bool(int(self.motWarnCode[9]))

    @wa_Temp_ERM_Module.setter
    def wa_Temp_ERM_Module(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[9] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_U_Max(self):
        return bool(int(self.motWarnCode[10]))

    @wa_U_Max.setter
    def wa_U_Max(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[10] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_U_Min(self):
        return bool(int(self.motWarnCode[11]))

    @wa_U_Min.setter
    def wa_U_Min(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[11] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Intermed_Circ_Voltage(self):
        return bool(int(self.motWarnCode[12]))

    @wa_Intermed_Circ_Voltage.setter
    def wa_Intermed_Circ_Voltage(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[12] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_Wrong_Mode(self):
        return bool(int(self.motWarnCode[13]))

    @wa_Wrong_Mode.setter
    def wa_Wrong_Mode(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[13] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_err_cmd_M(self):
        return bool(int(self.motWarnCode[14]))

    @wa_err_cmd_M.setter
    def wa_err_cmd_M(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[14] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_err_sts_SBM(self):
        return bool(int(self.motWarnCode[15]))

    @wa_err_sts_SBM.setter
    def wa_err_sts_SBM(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[15] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_err_sts_EF(self):
        return bool(int(self.motWarnCode[16]))

    @wa_err_sts_EF.setter
    def wa_err_sts_EF(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[16] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])

    @property
    def wa_err_sts_RF(self):
        return bool(int(self.motWarnCode[17]))

    @wa_err_sts_RF.setter
    def wa_err_sts_RF(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        motWarnCode = bytearray(self.motWarnCode)
        motWarnCode[17] = str(int(value))
        self.status[23:27] = utils.binary_to_bytes(str(motWarnCode)[::-1])
