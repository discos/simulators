from simulators import utils

mode_command_functions = {
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


class ModeCommandStatus(object):

    def __init__(self):
        self.received_mode_command_counter = 0  # UINT32, command serial number

        # received_mode_command, UINT16
        # 0: ignore
        # 1: inactive
        # 2: active
        # 3: preset absolute
        # 4: preset relative
        # 5: slew
        # 7: stop
        # 8: program track
        # 15: reset
        # 50: stow
        # 51: un-stow
        # 52: drive to stow position
        self.received_mode_command = 0

        # received_command_answer, UINT16
        # 0: no command
        # 4: command received in wrong mode
        # 5: command has invalid parameters
        # 9: command accepted
        self.received_command_answer = 0

        self.executed_mode_command_counter = 0  # UINT32, command serial number

        # executed_mode_command, UINT16, same as 'received_mode_command'
        self.executed_mode_command = 0

        # executed_command_answer, UINT16
        # 0: no command
        # 1: command executed
        # 2: command active
        # 3: command error during execution
        self.executed_command_answer = 0

    def get_status(self):
        response = (
            utils.uint_to_bytes(self.received_mode_command_counter)
            + utils.uint_to_bytes(self.received_mode_command, 2)
            + utils.uint_to_bytes(self.received_command_answer, 2)
            + utils.uint_to_bytes(self.executed_mode_command_counter)
            + utils.uint_to_bytes(self.executed_mode_command, 2)
            + utils.uint_to_bytes(self.executed_command_answer, 2)
        )
        return response
