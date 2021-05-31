import time
from math import modf
from SocketServer import ThreadingTCPServer
from simulators.common import ListeningSystem


servers = [(('0.0.0.0', 13000), (), ThreadingTCPServer, {})]


class System(ListeningSystem):

    tail = [b'\x0A', b'\x0D']  # NEWLINE and CR

    ack = b'ack\n'
    nak = b'nak\n'

    channels = 14
    default_att = 7
    default_filter = 1

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
        'V': '_V'
    }

    params_types = {
        'I': [str, int, int],
        'A': [int, str, int, int],
        'C': [str]
    }

    def __init__(self):
        # INT that represents the time offset from UTC UNIX time
        self.time_offset = 0
        self.msg = ''
        self._set_default()

    def _set_default(self):
        self.attenuations = {
            'B': [self.default_att] * self.channels,
            'P': [self.default_att] * self.channels,
            'G': [self.default_att] * self.channels,
            'Z': [self.default_att] * self.channels
        }
        self.filters = {
            'B': [1] * self.channels,
            'P': [1] * self.channels,
            'G': [1] * self.channels,
            'Z': [1] * self.channels
        }
        self.noise_mark = 0
        self.ext_noise_mark = 0
        self.fifty_ohm = 0

    def parse(self, byte):
        self.msg += byte

        if len(self.msg) == 1:
            if byte in self.commands.keys():
                return True
            else:
                self.msg = ''
                return False
        else:
            if byte not in self.tail:
                return True
            else:
                msg = self.msg[:-1]
                self.msg = ''
                return self._execute(msg)

    def _execute(self, msg):
        args = [x.strip() for x in msg.split(' ')]

        cmd = self.commands.get(args[0])
        cmd = getattr(self, cmd)

        params = args[1:]
        try:
            params_types = self.params_types.get(args[0], int)
            if not isinstance(params_types, list):
                params_types = [params_types] * len(params)
            elif len(params) != len(params_types):
                return self.nak
            for index in xrange(len(params)):
                params[index] = params_types[index](params[index])
        except ValueError:
            return self.nak
        return cmd(params)

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
        response = '%d,%d,%d,%d,%d' % (params[0], params[1], t[0], t[1], t[2])
        return response + '\x0D\x0A'

    def _E(self, params):
        if len(params) != 2:
            return self.nak
        t = self._get_time()
        response = '%d,%d,%d,%d,%d' % (params[0], params[1], t[0], t[1], t[2])
        return response + '\x0D\x0A'

    def _I(self, params):
        if params[0] not in ['B', 'P', 'G', 'Z']:
            return self.nak
        elif params[1] not in range(16):
            return self.nak
        elif params[2] not in range(1, 5):
            return self.nak
        self.attenuations[params[0]] = [params[1]] * self.channels
        self.filters[params[0]] = [params[2]] * self.channels
        return self.ack

    def _A(self, params):
        if params[0] not in range(self.channels):
            return 'nak %d\n' % params[0]
        if params[1] not in ['B', 'P', 'G', 'Z']:
            return 'nak %d\n' % params[0]
        elif params[2] not in range(16):
            return 'nak %d\n' % params[0]
        elif params[3] not in range(1, 5):
            return 'nak %d\n' % params[0]

        self.attenuations[params[1]][params[0]] = params[2]
        self.filters[params[1]][params[0]] = params[3]
        return self.ack

    def _status(self, params):
        # epoca_cpu_sec, epoca_cpu_microsec, epoca_fpga, sample_rate[ms], marca_sync, tpzero_sync, I, Att, BW_0, BW
        pass

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
        self.noise_mark = params[0]
        return self.ack

    def _M(self, params):
        if len(params) != 1:
            return self.nak
        elif params[0] not in [0, 1]:
            return self.nak
        self.ext_noise_mark = params[0]
        return self.ack

    def _Z(self, params):
        if len(params) != 1:
            return self.nak
        elif params[0] not in [0, 1]:
            return self.nak
        self.fifty_ohm = params[0]
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
