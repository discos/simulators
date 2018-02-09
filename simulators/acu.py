from simulators import utils
from simulators.acu_status.general_status import GeneralStatus
from simulators.acu_status.axis_status import (
    AzimuthAxisStatus, ElevationAxisStatus
)
from simulators.acu_status.pointing_status import PointingStatus
from simulators.acu_status.facility_status import FacilityStatus
from simulators.common import ListeningSystem, SendingSystem


# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers.s This list contains tuples
# (l_address, s_address, args). l_address is the tuple (ip, port) that
# defines the listening node that exposes the parse method, s_address
# is the tuple that defines the optional sending node that exposes the
# get_message method, while args is a tuple of optional extra arguments.
servers = []
servers.append((('127.0.0.1', 13000), ('127.0.0.1', 13001), ()))

start_flag = b'\x1D\xFC\xCF\x1A'
end_flag = b'\xA1\xFC\xCF\xD1'


class System(ListeningSystem, SendingSystem):

    def __init__(self, sampling_time=0.2):
        """
        param sampling_time: seconds between the sending of consecutive
        status messages
        """
        self.acu = ACU()
        self._set_default()
        self.sampling_time = sampling_time
        self.cmd_counter = None

    def _set_default(self):
        self.msg = b''
        self.msg_length = 0
        self.cmds_number = 0

    def parse(self, byte):
        self.msg += byte

        while self.msg and len(self.msg) <= 4:
            if self.msg != start_flag[:len(self.msg)]:
                self.msg = self.msg[1:]
            else:
                break

        if not self.msg:
            return False

        if len(self.msg) == 8:
            self.msg_length = utils.bytes_to_int(self.msg[-4:])

        if len(self.msg) == 12:
            cmd_counter = utils.bytes_to_uint(self.msg[-4:])
            if cmd_counter == self.cmd_counter:
                self._set_default()
                raise ValueError('Duplicated cmd_counter.')
            else:
                self.cmd_counter = cmd_counter

        if len(self.msg) == 16:
            self.cmds_number = utils.bytes_to_int(self.msg[-4:])

        if len(self.msg) > 16 and len(self.msg) == self.msg_length:
            msg = self.msg
            self._set_default()
            if msg[-4:] != end_flag:
                raise ValueError(
                    'Wrong end flag: got %s, expected %s.'
                    % (msg[-4:], end_flag)
                )
            return self.acu.parse_commands(msg)

        return True

    def get_message(self):
        return self.acu.get_status()


class ACU(object):

    functions = {
        1: '_mode_command',
        2: '_parameter_command',
        4: '_program_track_parameter_command',
    }

    def __init__(self):
        """
        param sampling_time: seconds between the sending of consecutive
        status messages
        """
        self.GS = GeneralStatus()
        self.Azimuth = AzimuthAxisStatus()
        self.Elevation = ElevationAxisStatus()
        self.PS = PointingStatus(self.Azimuth, self.Elevation)
        self.FS = FacilityStatus()

        self.status_message = None

    def get_status(self):
        status = (
            self.GS.get_status()
            + self.Azimuth.get_axis_status()
            + self.Elevation.get_axis_status()
            + self.Azimuth.get_cable_wrap_axis_status()
            + self.Azimuth.get_motor_status()
            + self.Elevation.get_motor_status()
            + self.Azimuth.get_cable_wrap_motor_status()
            + self.PS.get_status()
            + self.FS.get_status()
        )

        msg_length = utils.uint_to_bytes(len(status) + 16)
        msg_counter = utils.uint_to_bytes(utils.day_milliseconds())

        status_message = start_flag
        status_message += msg_length
        status_message += msg_counter
        status_message += status
        status_message += end_flag

        return status_message

    def parse_commands(self, msg):
        cmds_number = utils.bytes_to_int(msg[12:16])
        commands_string = msg[16:-4]  # Trimming end flag

        commands = []

        while commands_string:
            current_id = utils.bytes_to_int(commands_string[:2])

            if current_id == 1 or current_id == 2:
                commands.append(commands_string[:26])
                commands_string = commands_string[26:]
            elif current_id == 4:
                command_ending = commands_string.find(end_flag)
                commands.append(commands_string[:command_ending])
                commands_string = commands_string[command_ending + 4:]
            else:
                raise ValueError('Unknown command.')

        if len(commands) != cmds_number:
            raise ValueError('Malformed message.')

        for command in commands:
            command_id = utils.bytes_to_int(command[:2])
            name = self.functions.get(command_id)
            if name is not None:
                method = getattr(self, name)
                method(command)

        return True

    def _mode_command(self, command):
        subsystem_id = utils.bytes_to_int(command[2:4])

        if subsystem_id == 1:
            self.Azimuth.mode_command(command)
        elif subsystem_id == 2:
            self.Elevation.mode_command(command)
        else:
            raise ValueError('Unknown subsystem.')

    def _parameter_command(self, command):
        subsystem_id = utils.bytes_to_int(command[2:4])

        if subsystem_id == 1:
            self.Azimuth.parameter_command(command)
        elif subsystem_id == 2:
            self.Elevation.parameter_command(command)
        elif subsystem_id == 5:
            self.PS.parameter_command(command)
        else:
            raise ValueError('Unknown subsystem.')

    def _program_track_parameter_command(self, command):
        subsystem_id = utils.bytes_to_int(command[2:4])

        if subsystem_id == 5:
            self.PS.program_track_parameter_command(command)
        else:
            raise ValueError('Unknown subsystem.')

    def stop(self):
        self.Azimuth.stop()
        self.Elevation.stop()
        self.run = False
