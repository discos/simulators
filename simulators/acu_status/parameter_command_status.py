from simulators import utils


class ParameterCommandStatus(object):

    parameter_command_counter = 0  # UINT32, command serial number

    # parameter_command, UINT16
    # 0: ignore
    # 11: absolute position offset
    # 12: relative position offset
    # 50: time source
    # 51: time offset
    # 60: program track time correction
    # 61: load program track table
    parameter_command = 0

    # parameter_command_answer, UINT16
    # 0: no command
    # 1: command executed
    # 4: command received in wrong mode
    # 5: command has invalid parameters
    parameter_command_answer = 0

    def get_status(self):
        return (utils.uint_to_bytes(self.parameter_command_counter)
                + utils.uint_to_bytes(self.parameter_command, 2)
                + utils.uint_to_bytes(self.parameter_command_answer, 2))
