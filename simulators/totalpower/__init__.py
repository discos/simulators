import time
from math import modf
from SocketServer import ThreadingTCPServer
from simulators.common import ListeningSystem


servers = [(('0.0.0.0', 11500), (), ThreadingTCPServer, {})]


class System(ListeningSystem):

    tail = [b'\x0A', b'\x0D']  # NEWLINE and CR

    ack = b'ack\n'
    nak = b'nak\n'

    channels = 14

    commands = {
        'T': '_T',
        'E': '_E',
        'I': '_I',
        'A': '_A',
        '?': '_status',
        'G': '_G',
        'N': '_N',
        'M': '_M',
        'Z': '_Z',
        'S': '_S',
        'R': '_R',
        'X': '_X',
        'K': '_K',
        'C': '_C',
        'J': '_J',
        'O': '_O',
        '!': '_global',
        'W': '_W',
        'L': '_L',
        'V': '_V',
        'pause': '_pause',
        'stop': '_stop',
        'restore': '_restore',
        'quit': '_quit',
    }

    params_types = {
        'I': [str, int, int],
        'A': [int, str, int, int],
        'C': [str]
    }

    def __init__(self):
        # INT that represents the time offset from UTC UNIX time
        self.boards = [Board()] * self.channels
        self.zero = 0
        self.calOn = 0
        self.fastSwitch = 0
        self.externalNoise = 0
        self.time_offset = 0
        self.sample_rate = 1000
        self.msg = ''

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
            for index in range(len(params)):
                params[index] = params_types[index](params[index])
        except ValueError:
            return self.nak
        response = cmd(params)
        return response

    def _get_time(self):
        now = time.time()
        now_microsec, now_sec = modf(now)
        now_microsec = str(now_microsec)[:8].split('.')[1]
        _, sec = modf(now + self.time_offset)
        return int(now_sec), int(now_microsec), int(sec)

    def _T(self, params):
        if len(params) != 2:
            return self.nak
        new_time = float('%d.%.6d' % (params[0], params[1]))
        now = time.time()
        self.time_offset = now - new_time
        t = self._get_time()
        response = '%d, %d, %d, %d, %d' % (params[0], params[1], t[0], t[1], t[2])
        return response + '\x0D\x0A'

    def _E(self, params):
        if len(params) != 2:
            return self.nak
        t = self._get_time()
        response = '%d, %d, %d, %d, %d' % (params[0], params[1], t[0], t[1], t[2])
        return response + '\x0D\x0A'

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
        if board not in range(self.channels):
            return 'nak %d\n' % params[0]
        if params[1] not in ['B', 'P', 'G', 'Z']:
            return 'nak %d\n' % params[0]
        elif params[2] not in range(16):
            return 'nak %d\n' % params[0]
        elif params[3] not in range(1, 5):
            return 'nak %d\n' % params[0]

        self.boards[board].I = params[1]
        self.boards[board].A = params[2]
        self.boards[board].F = params[3]
        return self.ack

    def _status(self, params):
        t = self._get_time()
        # epoca_cpu_sec, epoca_cpu_microsec, epoca_fpga, status_word, sample_rate[ms], marca_sync, tpzero_sync, I0, Att0, BW0, etc
        response = '%d %d %d %d%d%d%d %d 0 0' % (
            t[0],
            t[1],
            t[2],
            self.zero,
            self.calOn,
            self.fastSwitch,
            self.externalNoise,
            self.sample_rate
        )
        for board in self.boards:
            response += ' %s %d %d' % (board.I, board.A, board.B)
        return response + '\x0D\x0A'

    def _G(self, params):
        if len(params) != 2:
            return self.nak
        # Do something
        return self.ack

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
        self.sample_rate = params[0]
        return self.ack

    def _R(self, params):
        pass

    def _X(self, params):
        pass

    def _K(self, params):
        pass

    def _C(self, params):
        pass

    def _J(self, params):
        pass

    def _O(self, params):
        pass

    def _global(self, params):
        pass

    def _W(self, params):
        pass

    def _L(self, params):
        pass

    def _V(self, params):
        pass

    def _pause(self, params):
        pass

    def _stop(self, params):
        return self.ack

    def _restore(self, params):
        pass

    def _quit(self, params):
        pass


class Board(object):

    sources = {
        'P': 'PRIM',
        'B': 'BWG',
        'G': 'GREG',
        'Z': '50_OHM'
    }

    bandwidths = {
        1: 330,
        2: 830,
        3: 1250,
        4: 2350
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
        elif source in self.sources.keys():
            self._previous_input = self._input
            self._input = self.sources.get(source)            
        elif not source and self._input == '50_OHM':
            self._input = self._previous_input
        else:
            return False
        return True

    @property
    def A(self):
        return self.attenuation

    @A.setter
    def A(self, attenuation):
        if attenuation not in range(16):
            return False
        self.attenuation = attenuation
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
