from simulators import utils


class MotorStatus(object):
    def __init__(self):
        self.actual_position = 0  # REAL32, [rot]
        self.actual_velocity = 0  # REAL32, [rot/min]
        self.actual_torque = 0  # REAL32, [Nm]
        self.rate_of_utilization = 0  # REAL32, [+- 200 %]
        self.active = 0  # UINT8, 0: motor inactive, 1: motor active

        # speed_of_rotation, UINT8
        # 0: speed of rotation unequal 0
        # 1: speed of rotation equal 0
        self.speed_of_rotation = 0

        # speed_of_rotation_ok, UINT8
        # 0: speed of rotation failure
        # 1: speed of rotation ok
        self.speed_of_rotation_ok = 0

        # position, UINT8
        # 0: desired position not reached
        # 1: desired position reached
        self.position = 0

        self.bus = 0  # UINT8, 0: bus ok, 1: bus error
        self.servo = 0  # UINT8, 0: servo ok, 1: servo error
        self.sensor = 0  # UINT8, 0: sensor ok, 1: sensor error

        # motWarnCode, DWORD, in bit mode coded warning status of the motor
        self.wa_iQuad_t = 0
        self.wa_Temp_Amplifier = 0
        self.wa_Temp_Mot = 0
        self.wa_v_Max_Exceeded = 0
        self.wa_M_Max_Exceeded = 0
        self.wa_Mot_Overload = 0
        self.wa_Temp_Cooling = 0
        self.wa_Temp_Extern = 0
        self.wa_Temp_Pow_Supply = 0
        self.wa_Temp_ERM_Module = 0
        self.wa_U_Max = 0
        self.wa_U_Min = 0
        self.wa_Intermed_Circ_Voltage = 0
        self.wa_Wrong_Mode = 0
        self.wa_err_cmd_M = 0
        self.wa_err_sts_SBM = 0
        self.wa_err_sts_EF = 0
        self.wa_err_sts_RF = 0
        # bits 18:31 = 0, not used

    def _motor_warning_code(self):
        binary_string = (
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
            + '0' * 14
        )
        return utils.binary_to_bytes(binary_string)

    def get_status(self):
        response = (
            utils.real_to_bytes(self.actual_position, 1)
            + utils.real_to_bytes(self.actual_velocity, 1)
            + utils.real_to_bytes(self.actual_torque, 1)
            + utils.real_to_bytes(self.rate_of_utilization, 1)
            + utils.uint_to_bytes(self.active, 1)
            + utils.uint_to_bytes(self.speed_of_rotation, 1)
            + utils.uint_to_bytes(self.speed_of_rotation_ok, 1)
            + utils.uint_to_bytes(self.position, 1)
            + utils.uint_to_bytes(self.bus, 1)
            + utils.uint_to_bytes(self.servo, 1)
            + utils.uint_to_bytes(self.sensor, 1)
            + self._motor_warning_code()
        )
        return response

    def _inactive(self):
        pass

    def _active(self):
        pass

    def _preset_absolute(self, angle, rate):
        pass

    def _preset_relative(self, angle, rate):
        pass

    def _slew(self, percentage, rate):
        pass

    def _stop(self):
        pass

    def _program_track(self, rate):
        pass

    def _interlock(self):
        pass

    def _reset(self):
        pass

    def _stow(self):
        pass

    def _unstow(self):
        pass

    def _drive_to_stow(self, stow_position, rate):
        pass
