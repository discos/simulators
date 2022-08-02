import codecs
from random import randint
from socketserver import ThreadingUDPServer
from simulators.common import ListeningSystem


# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers. This list contains tuples
# (l_address, s_address, kwargs). l_address is the tuple (ip, port) that
# defines the listening node that exposes the parse method, s_address
# is the tuple that defines the optional sending node that exposes the
# subscribe and unsubscribe methods, while kwargs is a dict of optional
# extra arguments.
servers = [(('0.0.0.0', 12600), (), ThreadingUDPServer, {})]


class System(ListeningSystem):

    header = '#'
    tail = '\n'
    firmware_string = 'GAIA Simulator Rev. 1.0.0 / 2022.02.08.1'
    channels = range(1, 11)
    name = 'GAIASIMBOARD'

    commands = {
        '*IDN?': '_idn',
        'LOADCONF': '_loadconf',
        'CONF?': '_conf',
        'SETD': '_setd',
        'SETG': '_setg',
        'SETSG': '_setsg',
        'SETSD': '_setsd',
        'SETSGZ': '_setsgz',
        'SETSDZ': '_setsdz',
        'SAVECPU': '_savecpu',
        'RESETD': '_resetd',
        'RESETG': '_resetg',
        'SAVE': '_save',
        'SETDF': '_setdf',
        'SETGF': '_setgf',
        'GETEF': '_getef',
        'ENABLE': '_enable',
        'DISABLE': '_disable',
        'GETVG': '_getvg',
        'GETVD': '_getvd',
        'GETID': '_getid',
        'GETREF': '_getref',
        'GETEMP': '_getemp',
        'NAME?': '_name'
    }

    # Only arguments, no command id
    params = {
        '*IDN?': 0,
        'LOADCONF': 1,
        'CONF?': 0,
        'SETD': 2,
        'SETG': 2,
        'SETSG': 1,
        'SETSD': 1,
        'SETSGZ': 1,
        'SETSDZ': 1,
        'SAVECPU': 1,
        'RESETD': 1,
        'RESETG': 1,
        'SAVE': 1,
        'SETDF': 1,
        'SETGF': 1,
        'GETEF': 1,
        'ENABLE': 1,
        'DISABLE': 1,
        'GETVG': 1,
        'GETVD': 1,
        'GETID': 1,
        'GETREF': 1,
        'GETEMP': 1,
        'NAME?': 0
    }

    errors = {
        1000: 'ERROR_ARGS_NOT_VALID',
        1001: 'ERROR_COMMAND_UNKNOWN',
        1002: 'ERROR_FIRST_ARG_NOT_NUMBER',
        1003: 'ERROR_FIRST_ARG_OUT_OF_RANGE',
        1004: 'ERROR_NO_ARGS',
        1005: 'ERROR_NO_SECOND_ARG',
        1006: 'ERROR_TERMINATOR',
        1007: 'ERROR_SECOND_ARG_LENGTH_ZERO',
        1008: 'ERROR_SECOND_ARG_NOT_PRESENT',
        1009: 'ERROR_SECOND_ARG_NOT_NUMBER',
        1010: 'ERROR_SECOND_ARG_OUT_OF_RANGE',
        1011: 'ERROR_SINGLE_WORD_COMMAND_UNKNOWN',
        1012: 'ERROR_START_CHAR_NOT_PRESENT',
        1013: 'ERROR_THIRD_ARG_NOT_PRESENT',
        1014: 'ERROR_THIRD_ARG_OUT_OF_RANGE',
        1015: 'ERROR_TOO_MANY_ARGS',
        1016: 'ERROR_IP_NOT_VALID',
        1017: 'ERROR_SUBNETMASK_NOT_VALID',
        1018: 'ERROR_GATEWAY_NOT_VALID',
        1019: 'ERROR_ORDER_ON_MEMORY_INVALID',
        1020: 'ERROR_SPEED_SLOPE_VALUE_INVALID',
        1021: 'ERROR_ON_SWITCH_READ_MODE',
        1022: 'ERROR_COMMAND_NOT_VALID_IN_READ_MODE',
        1023: 'ERROR_NAME_BOARD_TOO_SHORT_OR_TOO_LONG',
        1024: 'ERROR_NO_COMMAND_ID',
        1025: 'ERROR_ON_LOAD_CONF',
        2000: 'ERROR_CHECKSUM'
    }

    def __init__(self):
        self.VD = 10 * [0]
        self.VG = 10 * [0]
        self.conf = 0
        self.msg = ''
        self.cmd_id = ''

    def parse(self, byte):
        self.msg += byte
        if not self.msg.startswith(self.header):
            self.msg = ''
        elif byte == self.tail:
            msg = self.msg[:-1]
            self.msg = ''
            return self._execute(msg)
        return True

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, comprehensive of its header and tail.
        """
        args = msg.lstrip(self.header).strip().split()
        if not args:
            return self._error(1000)
        cmd = self.commands.get(args[0])
        if not cmd:
            return self._error(1001)
        l = self.params.get(args[0])  # cmd + arguments length
        args, self.cmd_id = args[1:-1], args[-1]
        if len(args) > l:  # too many args
            return self._error(1015)
        if l == 0:  # no arguments, just the id
            pass  # nothing to do for IDN and NAME commands
        if l >= 1:
            if not args:  # first argument missing
                return self._error(1004)
            try:
                args[0] = int(args[0])
            except ValueError:
                return self._error(1002)
            first_range = self.channels
            if cmd in ('_getref', '_getemp'):
                first_range = [1, 2]
            if args[0] not in first_range:
                return self._error(1003)
        if l == 2:
            if len(args) == 1:  # second argument missing
                return self._error(1008)
            try:
                args[1] = int(args[1])
            except ValueError:
                return self._error(1009)
            if args[1] not in range(1024):
                return self._error(1010)
        cmd = getattr(self, cmd)
        raw_response = cmd(args)
        tail = ' %s%s' % (self.cmd_id, self.tail)
        return self.header + str(raw_response) + tail

    def _error(self, error_code):
        error_string = self.errors.get(error_code)
        return '%sERROR(%d)[%s](%s) %s%c' % (
            self.header,
            error_code,
            error_string,
            codecs.encode(error_string.encode('raw_unicode_escape'), 'hex'),
            self.cmd_id,
            self.tail
        )

    def _idn(self, _):
        return self.firmware_string

    def _setd(self, args):
        x = args[0]
        y = args[1]
        self.VD[x - 1] = y
        return x

    def _setg(self, args):
        x = args[0]
        y = args[1]
        self.VG[x - 1] = y
        return x

    def _loadconf(self, args):
        self.conf = args[0]
        return self.conf

    def _conf(self, _):
        return self.conf

    @staticmethod
    def _setsg(args):
        return args[0]

    @staticmethod
    def _setsd(args):
        return args[0]

    @staticmethod
    def _setsgz(args):
        return args[0]

    @staticmethod
    def _setsdz(args):
        return args[0]

    @staticmethod
    def _savecpu(args):
        return args[0]

    @staticmethod
    def _resetd(args):
        return args[0]

    @staticmethod
    def _resetg(args):
        return args[0]

    @staticmethod
    def _save(args):
        return args[0]

    @staticmethod
    def _setdf(args):
        return args[0]

    @staticmethod
    def _setgf(args):
        return args[0]

    @staticmethod
    def _getef(args):
        return args[0]

    @staticmethod
    def _enable(args):
        return args[0]

    @staticmethod
    def _disable(args):
        return args[0]

    def _getvg(self, args):
        x = args[0]
        return self.VG[x - 1]

    def _getvd(self, args):
        x = args[0]
        return self.VD[x - 1]

    @staticmethod
    def _getid(_):
        return 0  # current in mA, inside range [0, X]

    @staticmethod
    def _getref(args):
        x = args[0]
        if x == 1:
            return 2.5
        return 5

    @staticmethod
    def _getemp(_):
        return randint(30, 36)

    def _name(self, _):
        return self.name
