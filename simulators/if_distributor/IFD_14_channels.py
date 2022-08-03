from simulators.common import ListeningSystem


class System(ListeningSystem):
    """The IFDistributor, also known as Intermediate Frequency Distributor,
    shifts the received signal wave. This system is the simulator of the SRT
    original IFDistributor, which was never truly developed because of some
    orders delay that rendered the whole project obsolete. This may become
    useful in the future in case a new IFDistributor gets developed starting
    from the old schematics."""

    header = '#'
    tail = '\n'
    max_msg_length = 12  # '#AAA 99 999\n'
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
    version = 'SRT IF Distributor Simulator 1.0'

    def __init__(self):
        self.msg = ''
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
                self.msg = ''
                return False
        elif len(self.msg) < self.max_msg_length:
            if byte != self.tail:
                return True
        elif len(self.msg) == self.max_msg_length:
            if byte != self.tail:
                self.msg = ''
                raise ValueError(
                    'Message too long: max length should '
                    + f'be {self.max_msg_length}.'
                )

        msg = self.msg[1:-1]  # Remove the header and tail
        self.msg = ''
        return self._execute(msg)

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, after its header and tail got
            stripped away.
        """
        if ' ' in msg and '?' not in msg:  # Setup request
            try:
                command, channel, value = msg.split()
            except ValueError as ex:
                raise ValueError(
                    'The setup message must have three items: '
                    'command, channel, and value.'
                ) from ex

            if command not in self.allowed_commands:
                raise ValueError(
                    f'Command {command} not in {self.allowed_commands}'
                )

            try:
                channel = int(channel)
            except ValueError as ex:
                raise ValueError('The channel ID must be an integer.') from ex

            if channel >= self.max_channels or channel < 0:
                raise ValueError(
                    f'Channel {channel} does not exist.')

            try:
                value = int(value)
            except ValueError as ex:
                raise ValueError(
                    'The command value must be an integer.'
                ) from ex

            if command == 'ATT':
                if value < 0 or value >= self.max_att_multiplier:
                    raise ValueError(f'Value {value} not allowed')
                self.channels[channel] = value
            elif command == 'SWT':
                if value == 0:
                    self.switched = False
                elif value == 1:
                    self.switched = True
                else:
                    raise ValueError(
                        'SWT command accepts only values 00 or 01'
                    )
            return ''
        elif ' ' in msg and '?' in msg:  # Get request
            msg = msg.rstrip('?')
            try:
                command, channel = msg.split()
            except ValueError as ex:
                raise ValueError(
                    'The get message must have two items: '
                    'command and channel.'
                ) from ex

            try:
                channel = int(channel)
            except ValueError as ex:
                raise ValueError('The channel ID must be an integer.') from ex

            if channel >= self.max_channels or channel < 0:
                raise ValueError(
                    f'Channel {channel} does not exist.'
                )
            if command == 'ATT':
                return f'#{str(self.channels[channel] * self.att_step)}\n'
            elif command == 'SWT':
                return f'#{1 if self.switched else 0}\n'
            else:
                raise ValueError(
                    f'Command {command} not in {self.allowed_commands}'
                )
        elif msg == '*IDN?':  # IDN request
            return self.version
        elif msg == '*RST':  # RST command
            self._set_default()
            return None
        else:  # Not expected command
            return '#COMMAND UNKNOWN\n'
