import thread
import time
from simulators import utils
from simulators.acu_status import general_status
from simulators.acu_status import subsystem
from simulators.acu_status import pointing_status
from simulators.acu_status import facility_status
from simulators.common import BaseSystem


start_flag = b'\x1D\xFC\xCF\x1A'
end_flag = b'\xA1\xFC\xCF\xD1'


class System(BaseSystem):
    def __init__(self, queue_sampling_time=0.2):
        """
        param queue_sampling_time: seconds between the sending of consecutive
        status messages
        """
        self.acu = ACU(queue_sampling_time)
        self._set_default()

    def _set_default(self):
        self.msg = b''
        self.msg_length = 0
        self.cmd_counter = 0
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
            self.cmd_counter = utils.bytes_to_int(self.msg[-4:])

        if len(self.msg) == 16:
            self.cmds_number = utils.bytes_to_int(self.msg[-4:])

        if len(self.msg) > 16 and len(self.msg) == self.msg_length:
            msg = self.msg
            self._set_default()
            if msg[-4:] != end_flag:
                raise ValueError(
                    "Wrong end flag: got %s, expected %s."
                    % (msg[-4:], end_flag)
                )
            return self.acu.parse_commands(msg)

        return True

    def get_status(self):
        return self.acu.get_status()


class ACU(object):

    functions = {
        1: "mode_command",
        2: "parameter_command",
        4: "program_track_parameter_command",
    }

    def __init__(self, status_sampling_time=0.2):
        """
        param status_sampling_time: seconds between the sending of consecutive
        status messages
        """
        self.GS = general_status.GeneralStatus()
        self.Azimuth = subsystem.Subsystem()
        self.Elevation = subsystem.Subsystem()
        self.AzimuthCableWrap = subsystem.Subsystem()
        self.PS = pointing_status.PointingStatus()
        self.FS = facility_status.FacilityStatus()

        self.status_counter = 0
        self.status_message = None

        if status_sampling_time > 0:
            self.status_sampling_time = status_sampling_time
            thread.start_new_thread(self._update_status, ())

    def get_status(self):
        if self.status_message is None:
            status_message = self._status_message()
        else:
            status_message = self.status_message
            self.status_message = None

        return status_message

    def _status_message(self):
        status = (
            self.GS.get_status()
            + self.Azimuth.get_axis_status()
            + self.Elevation.get_axis_status()
            + self.AzimuthCableWrap.get_axis_status()
            + self.Azimuth.get_motor_status()
            + self.Elevation.get_motor_status()
            + self.AzimuthCableWrap.get_motor_status()
            + self.PS.get_status()
            + self.FS.get_status()
        )

        msg_length = utils.uint_to_bytes(len(status) + 12)
        msg_counter = utils.uint_to_bytes(self.status_counter)

        status_message = start_flag
        status_message += msg_length
        status_message += msg_counter
        status_message += status
        status_message += end_flag

        self.status_counter += 1

        return status_message

    def _update_status(self):
        while True:
            self.status_message = self._status_message()
            time.sleep(self.status_sampling_time)

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
                raise ValueError("Unknown command.")

        if len(commands) != cmds_number:
            raise ValueError("Malformed message.")

        for command in commands:
            command_id = utils.bytes_to_int(command[:2])
            name = self.functions.get(command_id)
            if name is not None:
                method = getattr(self, name)
                method(command)

        return True

    def mode_command(self, command):
        subsystem_id = utils.bytes_to_int(command[2:4])

        if subsystem_id == 1:
            self.Azimuth.mode_command(command)
        elif subsystem_id == 2:
            self.Elevation.mode_command(command)
        else:
            raise ValueError("Unknown subsystem.")

    def parameter_command(self, command):
        subsystem_id = utils.bytes_to_int(command[2:4])

        if subsystem_id == 1:
            self.Azimuth.parameter_command(command)
        elif subsystem_id == 2:
            self.Elevation.parameter_command(command)
        elif subsystem_id == 5:
            self.PS.parameter_command(command)
        else:
            raise ValueError("Unknown subsystem.")

    def program_track_parameter_command(self, command):
        pass
