from random import randint
from SocketServer import ThreadingUDPServer
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

    tail = '\n'
    firmware_string = 'GAIA Simulator Rev. 1.0.0 / 2022.02.08.1'
    channels = range(1, 11)

    commands = {
        '*IDN?': '_idn',
        '#*IDN?': '_idn',
        '#SETD': '_setd',
        '#SETG': '_setg',
        '#SETSG': '_setsg',
        '#SETSD': '_setsd',
        '#SETSGZ': '_setsgz',
        '#SETSDZ': '_setsdz',
        '#SAVECPU': '_savecpu',
        '#RESETD': '_resetd',
        '#RESETG': '_resetg',
        '#SAVE': '_save',
        '#SETDF': '_setdf',
        '#SETGF': '_setgf',
        '#GETEF': '_getef',
        '#ENABLE': '_enable',
        '#DISABLE': '_disable',
        '#GETVG': '_getvg',
        '#GETVD': '_getvd',
        '#GETID': '_getid',
        '#GETREF': '_getref',
        '#GETEMP': '_getemp',
        '#NAME?': '_name'
    }

    params = {
        '*IDN?': 0,
        '#*IDN?': 0,
        '#SETD': 2,
        '#SETG': 2,
        '#SETSG': 1,
        '#SETSD': 1,
        '#SETSGZ': 1,
        '#SETSDZ': 1,
        '#SAVECPU': 1,
        '#RESETD': 1,
        '#RESETG': 1,
        '#SAVE': 1,
        '#SETDF': 1,
        '#SETGF': 1,
        '#GETEF': 1,
        '#ENABLE': 1,
        '#DISABLE': 1,
        '#GETVG': 1,
        '#GETVD': 1,
        '#GETID': 1,
        '#GETREF': 1,
        '#GETEMP': 1,
        '#NAME?': 0
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
        2000: 'ERROR_CHECKSUM'
    }

    def __init__(self):
        self.VD = 10 * [0]
        self.VG = 10 * [0]
        self.name = 'GAIASIMBOARD'
        self.msg = b''

    def parse(self, byte):
        self.msg += byte
        if byte == self.tail:
            msg = self.msg[:-1]
            self.msg = b''
            return self._execute(msg)
        return True

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, comprehensive of its header and tail.
        """
        args = msg.split()
        if not args:
            return
        cmd = self.commands.get(args[0])
        if not cmd:
            return self._error(1001)
        l = self.params.get(args[0])        # cmd + arguments length
        args = args[1:]
        if len(args) > l:                   # too many args
            return self._error(1015)
        if l >= 1:
            if len(args) == 0:              # first argument expected but missing
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
            if len(args) == 1:              # second argument expected but missing
                return self._error(1008)
            try:
                args[1] = int(args[1])
            except ValueError:
                return self._error(1009)
            if args[1] not in range(1024):
                return self._error(1010)
        cmd = getattr(self, cmd)
        return cmd(args)

    def _error(self, error_code):
        error_string = self.errors.get(error_code)
        return 'ERROR(%d)[%s](%s)%c' % (
            error_code,
            error_string,
            error_string.encode('hex'),
            self.tail
        )

    def _idn(self, _):
        return self.firmware_string + self.tail

    def _setd(self, args):
        x = args[0]
        y = args[1]
        self.VD[x-1] = y
        return '%d%c' % (x, self.tail)

    def _setg(self, args):
        x = args[0]
        y = args[1]
        self.VG[x-1] = y
        return '%d%c' % (x, self.tail)

    def _setsg(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _setsd(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _setsgz(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _setsdz(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _savecpu(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _resetd(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _resetg(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _save(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _setdf(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _setgf(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _getef(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _enable(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _disable(self, args):
        x = args[0]
        return '%d%c' % (x, self.tail)

    def _getvg(self, args):
        x = args[0]
        return '%d%c' % (self.VG[x-1], self.tail)

    def _getvd(self, args):
        x = args[0]
        return '%d%c' % (self.VD[x-1], self.tail)

    def _getid(self, _):
        # corrente tra 0 e XmA
        return '0%c' % self.tail

    def _getref(self, args):
        x = args[0]
        if x == 1:
            return '2.5' + self.tail
        elif x == 2:
            return '5' + self.tail

    def _getemp(self, _):
        return '%d%c' % (randint(30, 36), self.tail)

    def _name(self, _):
        return self.name + self.tail
