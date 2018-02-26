import time
from threading import Thread
from simulators import utils
from simulators.acu_status.general_status import GeneralStatus
from simulators.acu_status.axis_status import AxisStatus
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

start_flag = b'\x1A\xCF\xFC\x1D'
end_flag = b'\xD1\xCF\xFC\xA1'


class System(ListeningSystem, SendingSystem):

    subsystems = {
        1: 'AZ',
        2: 'EL',
        5: 'PS',
    }

    commands = {
        1: 'mode_command',
        2: 'parameter_command',
        4: 'program_track_parameter_command',
    }

    def __init__(self, sampling_time=0.2):
        """
        param sampling_time: seconds between the sending of consecutive
        status messages
        """
        self._set_default()
        self.sampling_time = sampling_time
        self.command_counter = None
        self.macro_cmd_counter = None

        self.GS = GeneralStatus()
        self.AZ = AxisStatus(
            n_motors=8,
            max_rates=(0.85, 0.4),
            op_range=(-90, 450),
            stow_pos=[180],
        )  # Azimuth status
        self.EL = AxisStatus(
            n_motors=4,
            max_rates=(0.5, 0.25),
            op_range=(5, 90),
            stow_pos=[90],
        )  # Elevation status
        self.CW = AxisStatus()  # Azimuth Cable Wrap status
        self.PS = PointingStatus(self.AZ, self.EL, self.CW)
        self.FS = FacilityStatus()

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
            self.msg_length = utils.bytes_to_uint(self.msg[-4:])

        if len(self.msg) == 12:
            macro_cmd_counter = utils.bytes_to_uint(self.msg[-4:])
            if macro_cmd_counter == self.macro_cmd_counter:
                self._set_default()
                raise ValueError('Duplicated macro command counter.')
            else:
                self.macro_cmd_counter = macro_cmd_counter

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
            self._parse_commands(msg)

        return True

    def get_message(self):
        status = (
            self.GS.get_status()
            + self.AZ.get_axis_status()
            + self.EL.get_axis_status()
            + self.CW.get_axis_status()
            + self.AZ.get_motor_status()
            + self.EL.get_motor_status()
            + self.CW.get_motor_status()
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

    def _parse_commands(self, msg):
        cmds_number = utils.bytes_to_int(msg[12:16])
        commands_string = msg[16:-4]  # Trimming end flag

        commands = []

        while commands_string:
            current_id = utils.bytes_to_uint(commands_string[:2])

            if current_id == 1 or current_id == 2:
                command = commands_string[:26]
                commands_string = commands_string[26:]
            elif current_id == 4:
                command_ending = commands_string.find(end_flag)
                command = commands_string[:command_ending]
                commands_string = commands_string[command_ending + 4:]
            else:
                raise ValueError('Unknown command.')

            command_counter = utils.bytes_to_uint(command[4:8])
            if command_counter == self.command_counter:
                raise ValueError('Duplicated command counter.')
            else:
                self.command_counter = command_counter

            commands.append(command)

        if len(commands) != cmds_number:
            raise ValueError('Malformed message.')

        for command in commands:
            method = self._get_method(command)
            if not method:
                raise ValueError('Command has invalid parameters.')

            t = Thread(target=method, args=(command,))
            t.daemon = True
            t.start()
            time.sleep(0.01)

        return True

    def _get_method(self, command):
        command_id = utils.bytes_to_uint(command[:2])
        subsystem_id = utils.bytes_to_uint(command[2:4])

        command_name = self.commands.get(command_id)
        subsystem_name = self.subsystems.get(subsystem_id)

        command_method = None
        if subsystem_name:
            subsystem = getattr(self, subsystem_name)
            command_method = getattr(subsystem, command_name)

        return command_method
