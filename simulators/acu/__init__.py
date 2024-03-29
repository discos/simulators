import time
from datetime import datetime, timedelta
from multiprocessing import Value, Array
from ctypes import c_bool, c_char
from threading import Thread
from queue import Queue, Empty
from socketserver import ThreadingTCPServer
from simulators import utils
from simulators.common import ListeningSystem, SendingSystem
from simulators.acu.general_status import GeneralStatus
from simulators.acu.axis_status import MasterAxisStatus, SlaveAxisStatus
from simulators.acu.pointing_status import PointingStatus
from simulators.acu.facility_status import FacilityStatus


servers = []
servers.append(
    (('0.0.0.0', 13000), ('0.0.0.0', 13001), ThreadingTCPServer, {})
)

start_flag = '\x1A\xCF\xFC\x1D'
end_flag = '\xD1\xCF\xFC\xA1'


class System(ListeningSystem, SendingSystem):
    """The ACU, or Antenna Control Unit handles the antenna movement along its
    azimuth and elevation axes. It also handles the tracking of radio sources
    by continuously receiving and interpolating the coordinates for a given
    celestial source.

    :param sampling_time: seconds between the sending of consecutive
        status messages
    """

    subsystems = {
        1: 'AZ',
        2: 'EL',
        5: 'PS',
    }

    commands = {
        1: '_mode_command',
        2: '_parameter_command',
        4: '_program_track_parameter_command',
    }

    default_sampling_time = 0.1

    def __init__(self, sampling_time=default_sampling_time):
        self._set_default()
        self.sampling_time = sampling_time
        self.cmd_counter = None

        self.GS = GeneralStatus()
        self.AZ = MasterAxisStatus(
            n_motors=8,
            max_rates=(0.85, 0.4),
            op_range=(-90, 450),
            start_pos=180
        )
        self.EL = MasterAxisStatus(
            n_motors=4,
            max_rates=(0.5, 0.25),
            op_range=(5, 90),
            start_pos=90,
            stow_pos=[90],
        )
        self.AZ.name = 'azimuth'
        self.EL.name = 'elevation'
        self.CW = SlaveAxisStatus(n_motors=1, master=self.AZ)
        self.PS = PointingStatus(self.AZ, self.EL, self.CW)
        self.FS = FacilityStatus()

        self.stop = Value(c_bool, False)

        self.command_threads = Queue()

        self.status = Array(c_char, 813)
        self.status[0:4] = bytes(start_flag, 'latin-1')
        self.status[4:8] = utils.uint_to_bytes(813)
        self.status[-4:] = bytes(end_flag, 'latin-1')

        subsystems = []
        subsystems.append(self.PS.update_status)
        subsystems.append(self.AZ.update_status)
        subsystems.append(self.EL.update_status)
        subsystems.append(self.CW.update_status)
        self._update_subsystems(subsystems)

        statuses = []
        statuses.append(self.GS.status)
        statuses.append(self.AZ.status)
        statuses.append(self.EL.status)
        statuses.append(self.CW.status)
        for motor in self.AZ.motor_status:
            statuses.append(motor.status)
        for motor in self.EL.motor_status:
            statuses.append(motor.status)
        for motor in self.CW.motor_status:
            statuses.append(motor.status)
        statuses.append(self.PS.status)
        statuses.append(self.FS.status)
        self._update_status(self.status, statuses)

        self.subscribe_q = Queue()
        self.unsubscribe_q = Queue()

        args = (
            self.stop,
            self.sampling_time,
            self.status,
            subsystems,
            statuses,
            self.command_threads,
            self._update_subsystems,
            self._update_status,
            self.subscribe_q,
            self.unsubscribe_q
        )

        self.update_thread = Thread(
            target=self._update_loop,
            args=args
        )
        self.update_thread.daemon = True
        self.update_thread.start()

    def __del__(self):
        self.system_stop()

    def system_stop(self):
        self.stop.value = True
        self.update_thread.join()
        while True:
            try:
                command_thread = self.command_threads.get_nowait()
                command_thread.join()
            except Empty:
                break
        return super().system_stop()

    def _set_default(self):
        """This method resets the received command string to its default value.
        It is called when a tail character is received or when a command is
        received malformed."""
        self.msg = ''
        self.msg_length = 0
        self.cmds_number = 0

    def parse(self, byte):
        self.msg += byte

        if len(self.msg) <= 4:
            if self.msg != start_flag[:len(self.msg)]:
                self.msg = ''

        if not self.msg:
            return False

        if len(self.msg) == 8:
            self.msg_length = utils.string_to_uint(self.msg[-4:])

        if len(self.msg) == 12:
            cmd_counter = utils.string_to_uint(self.msg[-4:])
            if cmd_counter == self.cmd_counter:
                self._set_default()
                raise ValueError('Duplicated command counter.')
            self.cmd_counter = cmd_counter

        if len(self.msg) == 16:
            self.cmds_number = utils.string_to_int(self.msg[-4:])

        if len(self.msg) > 16 and len(self.msg) == self.msg_length:
            msg = self.msg
            self._set_default()
            if msg[-4:] != end_flag:
                raise ValueError(
                    f'Wrong end flag: got {msg[-4:]}, expected {end_flag}.'
                )
            self._parse_commands(msg)

        return True

    @staticmethod
    def _update_subsystems(update_functions):
        for update_function in update_functions:
            update_function()

    @staticmethod
    def _update_status(status, statuses):
        payload = b''
        for subsystem_status in statuses:
            payload += subsystem_status.raw
        status[8:12] = utils.uint_to_bytes(utils.day_milliseconds())
        status[12:-4] = payload

    @staticmethod
    def _update_loop(stop, sampling_time, status, subsystems, statuses,
                     cmd_queue, update_subsystems, update_status,
                     subscribe_q, unsubscribe_q):
        command_threads = []
        nxt = None
        counter = 0
        subscribers = []
        while not stop.value:
            try:
                sub = subscribe_q.get_nowait()
                subscribers.append(sub)
            except Empty:
                pass
            try:
                sub = unsubscribe_q.get_nowait()
                subscribers.remove(sub)
            except Empty:
                pass
            try:
                command_threads.append(cmd_queue.get_nowait())
            except Empty:
                pass
            for command_thread in command_threads:
                if not command_thread.is_alive():
                    command_threads.remove(  # pylint: disable=W4701
                        command_thread
                    )

            update_subsystems(subsystems)

            if counter % 20 == 0:
                update_status(status, statuses)
                for q in subscribers:
                    while True:
                        try:
                            q.get_nowait()
                        except Empty:
                            break
                    q.put(status.raw)
                now = utils.bytes_to_real(status[721:729], precision=2)
                now = utils.mjd_to_date(now)
                counter = 0
            else:
                now = datetime.utcnow()

            counter += 1

            correction = 0
            if nxt:
                correction = max(0, (now - nxt).total_seconds())
                now = nxt
            nxt = now + timedelta(seconds=sampling_time / 20.)

            time.sleep(
                max(0, (nxt - datetime.utcnow()).total_seconds() - correction)
            )

        for command_thread in command_threads:
            cmd_queue.put(command_thread)

    def subscribe(self, q):
        self.subscribe_q.put(q)

    def unsubscribe(self, q):
        self.unsubscribe_q.put(q)

    def _parse_commands(self, msg):
        cmds_number = utils.string_to_int(msg[12:16])
        commands_string = msg[16:-4]  # Trimming end flag

        commands = []
        subsystems = []

        while commands_string:
            current_id = utils.string_to_uint(commands_string[:2])

            if current_id in [1, 2]:
                command = commands_string[:26]
                commands_string = commands_string[26:]
            elif current_id == 4:
                header = commands_string[:42]
                sequence_len = utils.string_to_uint(header[16:18])
                expected_length = 42 + (sequence_len * 20)
                if len(commands_string) < expected_length:
                    raise ValueError('Malformed program track sequence.')
                command = commands_string[:expected_length]
                commands_string = commands_string[expected_length:]
            else:
                raise ValueError('Unknown command.')

            subsystem = utils.string_to_uint(command[2:4])
            if subsystem not in subsystems:
                subsystems.append(subsystem)
                commands.append(command)
            else:
                raise ValueError(
                    f'More than one command for subsystem {subsystem}.'
                )

        if len(commands) != cmds_number:
            raise ValueError('Malformed message.')

        for command in commands:
            method = self._get_method(command)
            if not method:
                raise ValueError('Command has invalid parameters.')

            t = Thread(target=method, args=(command, self.stop))
            t.daemon = True
            t.start()
            self.command_threads.put(t)

    def _get_method(self, command):
        command_id = utils.string_to_uint(command[:2])
        subsystem_id = utils.string_to_uint(command[2:4])

        command_name = self.commands.get(command_id)
        subsystem_name = self.subsystems.get(subsystem_id)

        command_method = None
        if subsystem_name:
            subsystem = getattr(self, subsystem_name)
            command_method = getattr(subsystem, command_name)

        return command_method
