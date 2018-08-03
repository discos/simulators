from simulators.common import ListeningSystem


class System(ListeningSystem):
    """The IFDistributor, also known as Intermediate Frequency Distributor,
    shifts the received signal wave. This system is the simulator of the SRT
    original IFDistributor, which was never truly developed because of some
    orders delay that rendered the whole project obsolete. This may become
    useful in the future in case a new IFDistributor gets developed starting
    from the old schematics."""

    header = b'#'
    tail = b'\n'
    max_msg_length = 12  # b'#AAA 99 999\n'
    # The dictionary devices has the device types as keys,
    # and a dictionary as value.  The value has the address as
    # key and the allowed values as value
    allowed_commands = ['ATT', 'SWT']
    max_channels = 96
    max_att = 31.75
    att_step = 0.25
    max_att_multiplier = max_att / att_step
    channels = [max_att_multiplier] * max_channels
    switched = False
    version = b'SRT IF Distributor Simulator 1.0'

    def __init__(self):
        self.msg = b''
        self._set_default()

    def _set_default(self):
        """This method sets the initial values for the system. It is a
        separate method from the constructor because it can get called at
        runtime when a reset command is received.."""
        self.channels = [self.max_att_multiplier] * self.max_channels
        self.switched = False

    def parse(self, byte):
        self.msg += byte
        if len(self.msg) == 1:
            if byte == self.header:
                return True  # Got the header
            else:
                self.msg = b''
                return False
        elif len(self.msg) < self.max_msg_length:
            if byte != self.tail:
                return True
        elif len(self.msg) == self.max_msg_length:
            if byte != self.tail:
                self.msg = b''
                raise ValueError(
                    'Message too long: max length should be %d.'
                    % self.max_msg_length
                )

        msg = self.msg[1:-1]  # Remove the header and tail
        self.msg = b''
        return self._execute(msg)

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, after its header and tail got
            stripped away.
        """
        if b' ' in msg and b'?' not in msg:  # Setup request
            try:
                command, channel, value = msg.split()
            except ValueError:
                raise ValueError(
                    'The setup message must have three items: '
                    'command, channel, and value.'
                )

            if command not in self.allowed_commands:
                raise ValueError(
                    'Command %s not in %s'
                    % (command, self.allowed_commands)
                )

            try:
                channel = int(channel)
            except ValueError:
                raise ValueError('The channel ID must be an integer.')

            if channel >= self.max_channels or channel < 0:
                raise ValueError(
                    'Channel %d does not exist.' % channel)

            try:
                value = int(value)
            except ValueError:
                raise ValueError('The command value must be an integer.')

            if command == 'ATT':
                if value < 0 or value >= self.max_att_multiplier:
                    raise ValueError('Value %d not allowed' % value)
                else:
                    self.channels[channel] = value
            elif command == 'SWT':
                if value == 0:
                    self.switched = False
                elif value == 1:
                    self.switched = True
                else:
                    raise ValueError(
                        'SWT command accepts only values 00 or 01')
            return b''
        elif b' ' in msg and b'?' in msg:  # Get request
            msg = msg.rstrip('?')
            try:
                command, channel = msg.split()
            except ValueError:
                raise ValueError(
                    'The get message must have two items: '
                    'command and channel.'
                )

            try:
                channel = int(channel)
            except ValueError:
                raise ValueError('The channel ID must be an integer.')

            if channel >= self.max_channels or channel < 0:
                raise ValueError(
                    'Channel %d does not exist.' % channel)
            else:
                if command == 'ATT':
                    return b'#%s\n' % str(
                        self.channels[channel] * self.att_step)
                elif command == 'SWT':
                    return b'#%s\n' % (1 if self.switched else 0)
                else:
                    raise ValueError(
                        'Command %s not in %s'
                        % (command, self.allowed_commands))
        elif msg == b'*IDN?':  # IDN request
            return self.version
        elif msg == b'*RST':  # RST command
            self._set_default()
            return None
        else:  # Not expected command
            return b'#COMMAND UNKNOWN\n'
