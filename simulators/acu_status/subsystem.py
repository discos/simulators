from simulators import utils
from simulators.acu_status import axis_status, motor_status


class Subsystem(object):
    mode_command_functions = {
        1: "inactive",
        2: "active",
        3: "preset_absolute",
        4: "preset_relative",
        5: "slew",
        7: "stop",
        8: "program_track",
        14: "interlock",
        15: "reset",
        50: "stow",
        51: "unstow",
        52: "drive_to_stow",
    }

    def __init__(self):
        self.axis = axis_status.AxisStatus()
        self.motor = motor_status.MotorStatus()

    def get_axis_status(self):
        return self.axis.get_status()

    def get_motor_status(self):
        return self.motor.get_status()

    def mode_command(self, cmd):
        cmd_cnt = utils.bytes_to_int(cmd[4:8])
        mode_id = utils.bytes_to_int(cmd[8:10])
        parameter_1 = utils.bytes_to_real(cmd[10:18], 2)
        parameter_2 = utils.bytes_to_real(cmd[18:26], 2)

        command = self.mode_command_functions.get(mode_id)
        if command is not None:
            method = getattr(self.axis, command)
            method(command, parameter_1, parameter_2)
        else:
            raise ValueError("Unknown mode id %d." % (mode_id))

        self.axis.mode_command_status.received_mode_command_counter = cmd_cnt
        self.axis.mode_command_status.received_mode_command = mode_id
        # self.mode_command_status.received_command_answer = 0  # UINT16
        # self.mode_command_status.executed_mode_command_counter = 0  # UINT32
        # self.mode_command_status.executed_mode_command = 0  # UINT16
        # self.mode_command_status.executed_command_answer = 0  # UINT16

    def parameter_command(self, command):
        # print("Received parameter command.")
        pass
