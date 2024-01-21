import time
import socket
from threading import Timer
from multiprocessing import Value
from ctypes import c_bool
from math import modf
from random import randint
from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem
from simulators.utils import uint_to_bytes, binary_to_string, string_to_binary


servers = [
    # SRT TotalPower simulator, 14 channels
    (('0.0.0.0', 11500), (), ThreadingTCPServer, {"channels": 14}),
    # Medicina TotalPower simulator, 4 channels
    (('0.0.0.0', 11510), (), ThreadingTCPServer, {"channels": 4})
]


def _get_time(time_offset=0):
    now = time.time()
    now_microsec, now_sec = modf(now)
    now_microsec = str(now_microsec)[2:8]
    _, sec = modf(now + time_offset)
    return int(now_sec), int(now_microsec), int(sec)


class System(ListeningSystem):

    tail = ['\x0A', '\x0D']  # NEWLINE and CR

    ack = 'ack\n'
    nak = 'nak\n'

    firmware_string = 'fpga 29.12.2009 simulator, firmware rev.48'

    commands = {
        'T': '_T',
        'E': '_E',
        'I': '_I',
        'A': '_A',
        '?': '_status',
        'N': '_N',
        'M': '_M',
        'Z': '_Z',
        'S': '_S',
        'R': '_R',
        'X': '_X',
        'V': '_V',
        'pause': '_pause',
        'stop': '_stop',
        'resume': '_resume'
    }

    params_types = {
        'I': [str, int, int],
        'A': [int, str, int, int],
        'X': [int, int, int, str, int]
    }

    def __init__(self, channels=14):
        self.channels = channels
        self.boards = [Board() for _ in range(self.channels)]

        # Status bits
        self.zero = 0
        self.calOn = 0
        self.zeroPeriod = 0
        self.calOnPeriod = 0
        self.fastSwitch = 0
        self.externalNoise = 0
        self.toggle = 0
        self.sample_counter = 0

        self.time_offset = 0
        self.sample_period = 1000  # milliseconds
        self.data_address = ""
        self.data_port = 0
        self.data_configured = False
        self.data_socket = None
        self.pause = Value(c_bool, True)
        self.stop = Value(c_bool, False)
        self.data_timer = None
        self.msg = ''

    def __del__(self):
        if isinstance(self.data_socket, socket.socket):
            self.data_socket.close()

    def parse(self, byte):
        if byte in self.tail:
            msg = self.msg
            self.msg = ''
            return self._execute(msg)
        self.msg += byte
        return True

    def _execute(self, msg):
        msg = msg.strip()
        args = [x.strip() for x in msg.split(' ')]

        cmd = self.commands.get(args[0])
        if not cmd:
            return False
        cmd = getattr(self, cmd)

        params = args[1:]
        try:
            params_types = self.params_types.get(args[0], int)
            if not isinstance(params_types, list):
                params_types = [params_types] * len(params)
            elif len(params) != len(params_types):
                return self.nak
            for index, _ in enumerate(params):
                params[index] = params_types[index](params[index])
        except ValueError:
            return self.nak
        response = cmd(params)
        return response

    def _T(self, params):
        if len(params) != 2:
            return self.nak
        new_time = float(f'{params[0]}.{params[1]:06d}')
        now = time.time()
        self.time_offset = now - new_time
        t = _get_time(self.time_offset)
        return f'{params[0]}, {params[1]}, {t[0]}, {t[1]}, {t[2]}\x0D\x0A'

    def _E(self, params):
        if len(params) != 2:
            return self.nak
        t = _get_time(self.time_offset)
        return f'{params[0]}, {params[1]}, {t[0]}, {t[1]}, {t[2]}\x0D\x0A'

    def _I(self, params):
        if params[0] not in ['B', 'P', 'G', 'Z']:
            return self.nak
        elif params[1] not in range(16):
            return self.nak
        elif params[2] not in range(1, 5):
            return self.nak

        for board in self.boards:
            board.I = params[0]
            board.A = params[1]
            board.F = params[2]
        return self.ack

    def _A(self, params):
        board = params[0] - 1
        if (board not in range(self.channels) or
                params[1] not in ['B', 'P', 'G', 'Z'] or
                params[2] not in range(16) or
                params[3] not in range(1, 5)):
            return f'nak {params[0]}\n'

        self.boards[board].I = params[1]
        self.boards[board].A = params[2]
        self.boards[board].F = params[3]
        return self.ack

    def _status(self, _):
        t = _get_time(self.time_offset)
        response = f'{t[0]} {t[1]} {t[2]} '
        response += f'{self._get_status(ascii_format=True)} '
        response += f'{self.sample_period} '
        response += f'{self.calOnPeriod} '
        response += f'{self.zeroPeriod}'
        for board in self.boards:
            response += f' {board.I} {board.A} {board.B}'
        return response + '\x0D\x0A'

    def _N(self, params):
        if len(params) != 1:
            return self.nak
        elif params[0] not in [0, 1]:
            return self.nak
        self.calOn = params[0]
        return self.ack

    def _M(self, params):
        if len(params) != 1:
            return self.nak
        elif params[0] not in [0, 1]:
            return self.nak
        self.externalNoise = params[0]
        return self.ack

    def _Z(self, params):
        if len(params) != 1:
            return self.nak
        elif params[0] not in [0, 1]:
            return self.nak
        for board in self.boards:
            if params[0] == 1:
                board.I = 'Z'
            elif params[0] == 0:
                board.I = None
        return self.ack

    def _S(self, params):
        if len(params) != 1:
            return self.nak
        self.sample_period = params[0]
        return self.ack

    def _R(self, _):
        response = f'{_get_time(self.time_offset)[0]} 0 0 '
        response += ' '.join(
            [f'{randint(0, 1000000)}' for __ in range(self.channels)]
        )
        return response + '\x0D\x0A'

    def _V(self, _):
        return self.firmware_string

    def _X(self, params):
        self.sample_period = params[0]  # sample period (orig. sample_rate)
        self.calOnPeriod = params[1]    # cal_on_period
        self.zeroPeriod = params[2]     # tpzero_period
        self.data_address = params[3]   # data_storage_server_address
        self.data_port = params[4]      # data_storage_server_port

        self.sample_counter = 0
        self.cal_off_samples = 0
        self.stop.value = False
        self.pause.value = False
        self.data_socket = socket.socket()
        self.data_socket.connect((self.data_address, self.data_port))
        self.data_configured = True
        return self.ack

    def _resume(self, _):
        if not self.data_configured:
            # Not configured, we cannot start
            return self.nak

        self.stop.value = False
        self.pause.value = False
        self.data_timer = Timer(
            1000 / self.sample_period * (float(self.sample_period) / 1000),
            self._send_packet,
            args=(self.stop, self.pause)
        )
        self.data_timer.start()
        return self.ack

    def _pause(self, _):
        self.pause.value = True
        return self.ack

    def _stop(self, _):
        self.stop.value = True

        def _wait_for_timer():
            self.data_timer.join()
            self.data_timer = None

        if self.data_timer and self.data_timer.is_alive():
            t = Timer(0, _wait_for_timer)
            t.start()

        return self.ack

    def _send_packet(self, stop, pause):
        packet = b''
        # Timestamp of the last packet
        t0 = timestamp = time.time()
        # Subtract the whole acquisition duration in order to mimic the start
        # time of the acquisition
        timestamp -= \
            (1000 / self.sample_period) * (float(self.sample_period) / 1000)
        for _ in range(int(1000 / self.sample_period)):
            # The epoch should represent the ending instant of each sample,
            # therefore, we add a sample_period
            timestamp += float(self.sample_period) / 1000
            packet += uint_to_bytes(int(timestamp))
            # Add a sample_period to the timestamp each sample we generate
            packet += uint_to_bytes(self.sample_counter, n_bytes=2)

            if self.calOnPeriod:
                if self.cal_off_samples == self.calOnPeriod:
                    self.calOn = 1
                    self.cal_off_samples = 0
                else:
                    self.cal_off_samples += 1
            packet += self._get_status()
            self.calOn = 0

            # Signal strength, 200 noise floor, 2000 strong signal
            for __ in range(self.channels):
                packet += uint_to_bytes(
                    randint(200, 2000) * self.sample_period
                )
            self.sample_counter += 1
            if self.sample_counter == 65536:
                self.sample_counter = 0

        # Packet complete, send it
        self.toggle = 0 if self.toggle else 1
        try:
            self.data_socket.sendall(packet)
        except socket.error:
            # For some reason the socket is not connected.
            # Stop the acquisition
            self._stop(None)

        # Start the timer again if not paused
        if stop.value:
            self.sample_counter = 0
            self.cal_off_samples = 0
            self.data_socket.close()
        elif pause.value:
            return
        else:
            # Restart the timer
            next_packet = t0 + \
                1000 / self.sample_period * (float(self.sample_period) / 1000)
            t = Timer(
                max(0, next_packet - time.time()),
                self._send_packet,
                args=(stop, pause)
            )
            t.start()
            self.data_timer = t

    def _get_status(self, ascii_format=False):
        # First byte alternates between \xA0 and \x90 each second of data
        status = '\xA0' if self.toggle else '\x90'
        status = string_to_binary(status)
        # Next 2 bits are always set to 01
        status += '01'
        # Inputs set to 50 Ohm
        status += str(self.zero)
        # Calibration mark is ON
        status += str(self.calOn)
        # This bit alternates between 0 and 1 each second of data
        status += str(self.toggle)
        # Last 3 bits are always 1
        status += '111'
        status = binary_to_string(status)
        if not ascii_format:
            return status.encode('latin-1')
        else:
            return ''.join([hex(ord(c))[-2:] for c in status[::-1]])


class Board:

    sources = {
        'P': 'PRIM',
        'B': 'BWG',
        'G': 'GREG',
        'Z': '50_OHM'
    }

    bandwidths = {
        1: 2000,
        2: 1250,
        3: 730,
        4: 300
    }

    def __init__(self):
        self._input = 'PRIM'
        self._previous_input = 'PRIM'
        self._attenuation = 7
        self._filter = 1

    @property
    def I(self):
        return self._input

    @I.setter
    def I(self, source):
        if source in self.sources.values():
            self._previous_input = self._input
            self._input = source
        elif source in self.sources:
            self._previous_input = self._input
            self._input = self.sources.get(source)
        elif not source and self._input == '50_OHM':
            self._input = self._previous_input
        else:
            return False
        return True

    @property
    def A(self):
        return self._attenuation

    @A.setter
    def A(self, attenuation):
        if attenuation not in range(16):
            return False
        self._attenuation = attenuation
        return True

    @property
    def F(self):
        return self._filter

    @F.setter
    def F(self, f):
        if f not in range(1, 5):
            return False
        self._filter = f
        return True

    @property
    def B(self):
        return self.bandwidths.get(self._filter)
