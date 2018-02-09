import time
from simulators import utils

start_flag = b'\x1D\xFC\xCF\x1A'
end_flag = b'\xA1\xFC\xCF\xD1'


class ModeCommand(object):

    def __init__(self,
            subsystem_id,
            mode_id,
            parameter_1=0.0,
            parameter_2=0.0):
        self.subsystem_id = subsystem_id
        self.mode_id = mode_id
        self.parameter_1 = parameter_1
        self.parameter_2 = parameter_2

    def get(self, command_counter):
        self.command_counter = command_counter
        return(
            utils.uint_to_bytes(1, 2)  # 1: mode command
            + utils.uint_to_bytes(self.subsystem_id, 2)
            + utils.uint_to_bytes(self.command_counter)
            + utils.uint_to_bytes(self.mode_id, 2)
            + utils.real_to_bytes(self.parameter_1, 2)
            + utils.real_to_bytes(self.parameter_2, 2)
        )


class ParameterCommand(object):

    def __init__(self,
            subsystem_id,
            parameter_id,
            parameter_1=0.0,
            parameter_2=0.0):
        self.subsystem_id = subsystem_id
        self.parameter_id = parameter_id
        self.parameter_1 = parameter_1
        self.parameter_2 = parameter_2

    def get(self, command_counter):
        self.command_counter = command_counter
        return(
            utils.uint_to_bytes(2, 2)  # 2: parameter command
            + utils.uint_to_bytes(self.subsystem_id, 2)
            + utils.uint_to_bytes(self.command_counter)
            + utils.uint_to_bytes(self.parameter_id, 2)
            + utils.real_to_bytes(self.parameter_1, 2)
            + utils.real_to_bytes(self.parameter_2, 2)
        )


class ProgramTrackEntry(object):

    def __init__(self, relative_time, azimuth_position, elevation_position):
        self.relative_time = relative_time
        self.azimuth_position = azimuth_position
        self.elevation_position = elevation_position

    def get(self):
        return(
            utils.int_to_bytes(self.relative_time)
            + utils.real_to_bytes(self.azimuth_position, 2)
            + utils.real_to_bytes(self.elevation_position, 2)
        )


class ProgramTrackCommand(object):

    def __init__(self,
            load_mode,
            start_time,
            axis_rates,
            sequence=None,
            subsystem_id=5):
        self.load_mode = load_mode
        self.start_time = start_time
        self.azimuth_rate = axis_rates[0]
        self.elevation_rate = axis_rates[1]
        self.sequence = [] if not sequence else sequence
        self.subsystem_id = subsystem_id

    def append_entry(self, entry):
        if not isinstance(entry, ProgramTrackEntry):
            raise ValueError('Not a ProgramTrackEntry object.')
        else:
            self.sequence.append(entry)

    def add_entry(self, relative_time, azimuth_position, elevation_position):
        pte = ProgramTrackEntry(
            relative_time,
            azimuth_position,
            elevation_position
        )
        self.sequence.append(pte)

    def get(self, command_counter):
        if not self.sequence:
            raise ValueError('Sequence must contain at least one entry.')

        self.command_counter = command_counter
        sequence_bytes = ''

        for entry in self.sequence:
            sequence_bytes += entry.get()

        return(
            utils.uint_to_bytes(4, 2)  # 4: program track parameter command
            # The only subsystem supported is 5, tracking, but it is possible
            # to be overridden to generate some specific errors
            + utils.uint_to_bytes(self.subsystem_id, 2)
            + utils.uint_to_bytes(self.command_counter)
            + utils.uint_to_bytes(61, 2)  # 61: load program track table
            + utils.uint_to_bytes(4, 2)  # 4: spline interpolation mode
            + utils.uint_to_bytes(1, 2)  # 1: coordinates in azimuth/elevation
            + utils.uint_to_bytes(self.load_mode, 2)
            + utils.uint_to_bytes(len(self.sequence), 2)
            + utils.real_to_bytes(self.start_time, 2)
            + utils.real_to_bytes(self.azimuth_rate, 2)
            + utils.real_to_bytes(self.elevation_rate, 2)
            + sequence_bytes
            + end_flag
        )


class Command(object):

    def __init__(self, *command_list):
        self.command_list = []
        for command in command_list:
            if not self._check_command(command):
                raise ValueError(
                    "Wrong command type: '%s'." % type(command)
                )
            else:
                self.command_list.append(command)

    @staticmethod
    def _check_command(command):
        if not isinstance(command, (ModeCommand,
                                    ParameterCommand,
                                    ProgramTrackCommand)):
            return False
        else:
            return True

    def append(self, command):
        if self._check_command(command):
            self.command_list.append(command)
        else:
            raise ValueError(
                "Wrong command type: '%s'." % type(command))

    def get(self):
        commands = b''
        command_counter = utils.day_milliseconds()

        for i in range(len(self.command_list)):
            commands += self.command_list[i].get(command_counter + i)

        time.sleep(0.001 * len(self.command_list))

        return(
            start_flag
            + utils.uint_to_bytes(20 + len(commands))
            + utils.uint_to_bytes(command_counter)
            + utils.uint_to_bytes(len(self.command_list))
            + commands
            + end_flag
        )
