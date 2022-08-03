import time
from simulators import utils

start_flag = '\x1A\xCF\xFC\x1D'
end_flag = '\xD1\xCF\xFC\xA1'


class ModeCommand:

    def __init__(self,
            subsystem_id,
            mode_id,
            parameter_1=None,
            parameter_2=None):
        self.subsystem_id = subsystem_id
        self.mode_id = mode_id

        if not parameter_1:
            parameter_1 = 0.0
        self.parameter_1 = parameter_1

        if not parameter_2:
            parameter_2 = 0.0
        self.parameter_2 = parameter_2

        self.command_counter = None

    def get(self, command_counter):
        self.command_counter = command_counter
        return(
            utils.uint_to_string(1, 2)  # 1: mode command
            + utils.uint_to_string(self.subsystem_id, 2)
            + utils.uint_to_string(self.command_counter)
            + utils.uint_to_string(self.mode_id, 2)
            + utils.real_to_string(self.parameter_1, 2)
            + utils.real_to_string(self.parameter_2, 2)
        )


class ParameterCommand:

    def __init__(self,
            subsystem_id,
            parameter_id,
            parameter_1=0.0,
            parameter_2=0.0):
        self.subsystem_id = subsystem_id
        self.parameter_id = parameter_id
        self.parameter_1 = parameter_1
        self.parameter_2 = parameter_2
        self.command_counter = None

    def get(self, command_counter):
        self.command_counter = command_counter
        return(
            utils.uint_to_string(2, 2)  # 2: parameter command
            + utils.uint_to_string(self.subsystem_id, 2)
            + utils.uint_to_string(self.command_counter)
            + utils.uint_to_string(self.parameter_id, 2)
            + utils.real_to_string(self.parameter_1, 2)
            + utils.real_to_string(self.parameter_2, 2)
        )


class ProgramTrackEntry:

    def __init__(self, relative_time, azimuth_position, elevation_position):
        self.relative_time = relative_time
        self.azimuth_position = azimuth_position
        self.elevation_position = elevation_position

    def get(self):
        return(
            utils.int_to_string(self.relative_time)
            + utils.real_to_string(self.azimuth_position, 2)
            + utils.real_to_string(self.elevation_position, 2)
        )


class ProgramTrackCommand:

    def __init__(self,
            load_mode,
            start_time,
            axis_rates,
            parameter_id=61,
            interpolation_mode=4,
            tracking_mode=1,
            subsystem_id=5):
        self.load_mode = load_mode
        self.start_time = start_time
        self.azimuth_rate = axis_rates[0]
        self.elevation_rate = axis_rates[1]
        self.parameter_id = parameter_id
        self.interpolation_mode = interpolation_mode
        self.tracking_mode = tracking_mode
        self.subsystem_id = subsystem_id

        self.sequence = []
        self.command_counter = None

    def append_entry(self, entry):
        if not isinstance(entry, ProgramTrackEntry):
            raise ValueError('Not a ProgramTrackEntry object.')
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
            utils.uint_to_string(4, 2)  # 4: program track parameter command
            # The only subsystem supported is 5, tracking, but it is possible
            # to be overridden to generate some specific errors
            + utils.uint_to_string(self.subsystem_id, 2)
            + utils.uint_to_string(self.command_counter)
            + utils.uint_to_string(self.parameter_id, 2)
            + utils.uint_to_string(self.interpolation_mode, 2)
            + utils.uint_to_string(self.tracking_mode, 2)
            + utils.uint_to_string(self.load_mode, 2)
            + utils.uint_to_string(len(self.sequence), 2)
            + utils.real_to_string(self.start_time, 2)
            + utils.real_to_string(self.azimuth_rate, 2)
            + utils.real_to_string(self.elevation_rate, 2)
            + sequence_bytes
        )


class Command:

    def __init__(self, *command_list):
        self.command_list = []
        for command in command_list:
            if not self._check_command(command):
                raise ValueError(f"Wrong command type: '{type(command)}'.")
            self.command_list.append(command)
        self.command_counter = None

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
            raise ValueError(f"Wrong command type: '{type(command)}'.")

    def get(self):
        commands = ''

        if not self.command_counter:
            self.command_counter = utils.day_milliseconds()

        for i, command in enumerate(self.command_list):
            commands += command.get(self.command_counter + 1 + i)

        time.sleep(0.001 * len(self.command_list))

        return(
            start_flag
            + utils.uint_to_string(20 + len(commands))
            + utils.uint_to_string(self.command_counter)
            + utils.uint_to_string(len(self.command_list))
            + commands
            + end_flag
        )

    def get_counter(self, index=None):
        if index is None:
            return self.command_counter
        elif index > 0 and index >= len(self.command_list):
            raise ValueError(f'Index {index} out of range.')
        elif index < 0 and abs(index) > len(self.command_list):
            raise ValueError(f'Index {index} out of range.')
        else:
            return self.command_list[index].command_counter
