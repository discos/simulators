import time
from SocketServer import ThreadingTCPServer
from simulators.common import ListeningSystem


# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers. This list contains tuples
# (l_address, s_address, args). l_address is the tuple (ip, port) that
# defines the listening node that exposes the parse method, s_address
# is the tuple that defines the optional sending node that exposes the
# subscribe and unsibscribe methods, while args is a tuple of optional
# extra arguments.
servers = [(('0.0.0.0', 12500), (), ThreadingTCPServer, ())]


class System(ListeningSystem):

    tail = [b'\x0A', b'\x0D']  # NEWLINE and CR
    max_msg_length = 7  # b'I 16 1\n'
    max_channels = 17
    max_period = 5000

    ack = b'ack\n'
    nak = b'nak\n'

    commands = {
        'I': '_set_input',
        'C': '_set_calibration',
        '?': '_get_status',
        'F': '_get_frequency'
    }

    def __init__(self):
        self.slow_channel = 16
        self.current_channel = self.slow_channel
        self.polarities = [0] * self.max_channels
        self.calon = [0] * self.max_channels
        self.msg = b''

    def parse(self, byte):
        self.msg += byte

        if len(self.msg) == 1:
            if byte in self.commands.keys():
                return True
            else:
                self.msg = b''
                return False
        elif len(self.msg) < self.max_msg_length:
            if byte not in self.tail:
                return True
        elif len(self.msg) == self.max_msg_length:
            if byte not in self.tail:
                self.msg = b''
                raise ValueError(
                    'Message too long: max length should be %d'
                    % self.max_msg_length
                )

        msg = self.msg[:-1]
        self.msg = b''
        return self._execute(msg)

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, comprehensive of its header and tail.
        """
        args = [x.strip() for x in msg.split(' ')]

        cmd = self.commands.get(args[0])
        cmd = getattr(self, cmd)

        args = args[1:]

        params = []
        try:
            for param in args:
                params.append(int(param))
        except ValueError:
            return self.nak

        return cmd(params)

    def _set_input(self, params):
        if len(params) != 2:
            return self.nak
        channel, polarity = params
        if channel not in range(self.max_channels):
            return self.nak
        elif polarity not in [0, 1]:
            return self.nak
        self.current_channel = channel
        self.polarities[channel] = polarity
        return self.ack

    def _set_calibration(self, params):
        if len(params) != 1:
            return self.nak
        calon = params[0]
        if calon not in [0, 1]:
            return self.nak
        self.calon[self.slow_channel] = calon
        return self.ack

    def _get_status(self, params):
        if params:
            return self.nak
        retval = b'%s %s %s\n' % (
            self.current_channel,
            self.polarities[self.current_channel],
            self.calon[self.current_channel]
        )
        return retval

    def _get_frequency(self, params):
        if len(params) != 1:
            return self.nak
        period = params[0]
        if period < 0 or period > self.max_period:
            return self.nak
        period = period / 1000.
        time.sleep(period)
        return '%d %d %d' % (0, 0, 0)
