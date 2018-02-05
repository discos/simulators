from simulators import utils

parameter_command_functions = {
    0: '_ignore',
    11: '_absolute_position_offset',
    12: '_relative_position_offset',
    50: '_time_source',
    51: '_time_offset',
    60: '_program_track_time_correction',
    61: '_load_program_track_table',
}


class ParameterCommandStatus(object):

    def __init__(self):
        self.parameter_command_counter = 0  # UINT32, command serial number

        # parameter_command, UINT16
        # 0: ignore
        # 11: absolute position offset
        # 12: relative position offset
        # 50: time source
        # 51: time offset
        # 60: program track time correction
        # 61: load program track table
        self.parameter_command = 0

        # parameter_command_answer, UINT16
        # 0: no command
        # 1: command executed
        # 4: command received in wrong mode
        # 5: command has invalid parameters
        self.parameter_command_answer = 0

    def get_status(self):
        return (utils.uint_to_bytes(self.parameter_command_counter)
                + utils.uint_to_bytes(self.parameter_command, 2)
                + utils.uint_to_bytes(self.parameter_command_answer, 2))
