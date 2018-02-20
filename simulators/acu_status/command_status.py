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


class CommandStatus(object):

    def __init__(self):
        self.counter = 0  # UINT32, command serial number
        self.command = 0  # UINT16, command id
        self.answer = 0   # UINT16, command answer


class ModeCommandStatus(object):

    def __init__(self):
        self.received = CommandStatus()
        # command ids, UINT16
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

        # command answers, UINT16
        # 0: no command
        # 4: command received in wrong mode
        # 5: command has invalid parameters
        # 9: command accepted

        self.executed = CommandStatus()

        # command ids, UINT16, same as 'received command ids'

        # command answer, UINT16
        # 0: no command
        # 1: command executed
        # 2: command active
        # 3: command error during execution

    def get_status(self):
        response = (
            utils.uint_to_bytes(self.received.counter)
            + utils.uint_to_bytes(self.received.command, 2)
            + utils.uint_to_bytes(self.received.answer, 2)
            + utils.uint_to_bytes(self.executed.counter)
            + utils.uint_to_bytes(self.executed.command, 2)
            + utils.uint_to_bytes(self.executed.answer, 2)
        )
        return response


class ParameterCommandStatus(CommandStatus):

    def __init__(self):
        CommandStatus.__init__(self)
        # command ids, UINT16
        # 0: ignore
        # 11: absolute position offset
        # 12: relative position offset
        # 50: time source
        # 51: time offset
        # 60: program track time correction
        # 61: load program track table

        # command answers, UINT16
        # 0: no command
        # 1: command executed
        # 4: command received in wrong mode
        # 5: command has invalid parameters

    def get_status(self):
        response = (
            utils.uint_to_bytes(self.counter)
            + utils.uint_to_bytes(self.command, 2)
            + utils.uint_to_bytes(self.answer, 2)
        )
        return response
