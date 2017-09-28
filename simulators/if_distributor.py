from simulators.common import BaseSystem


class System(BaseSystem):

    header = b'#'
    tail = b'\n'
    max_msg_length = 12  # b'#AAA 99 999\n'
    # The dictionary devices has the device types as keys,
    # and a dictionary as value.  The value has the address as
    # key and the allowed values as value
    devices = {
        'ATT': {
            0: {0: 0, 1: 0.025, 2: 0.05},
            1: {0: 0.035, 1: 0.70},
            2: {0: 0.01}
        },
        'SWT': {
            0: {0: 0, 1: 1}
        },
    }
    version = b'SRT IF Distributor 4.6.5 5.4.3'

    def __init__(self):
        self.msg = b''
        self._set_default()

    def _set_default(self):
        for device in self.devices:
            for address in self.devices[device]:
                attr_name = '%s_%s' % (device, address)
                value = self.devices[device][address][0]
                setattr(self, attr_name, value)

    def parse(self, byte):
        self.msg += byte
        if len(self.msg) == 1 and byte != self.header:
            self.msg = b''
            return False
        elif len(self.msg) == 1 and byte == self.header:
            return True  # Got the header
        elif len(self.msg) < self.max_msg_length and byte != self.tail:
            return True  # Waiting for the tail
        elif len(self.msg) == self.max_msg_length and byte != self.tail:
            self.msg = b''
            raise ValueError(
                'message too long: max length should be %d.' %
                self.max_msg_length
            )
        elif byte == self.tail:
            command = self.msg[1:-1]  # Remove the header and tail
            self.msg = b''
            # Setup command
            if b' ' in command and b'?' not in command:
                try:
                    device, address, value = command.split()
                except ValueError:
                    raise ValueError(
                        'the setup command must have three items: '
                        'device, address, and value.'
                    )

                if device not in self.devices:
                    raise ValueError(
                        'device %s not in %s' % (device, self.devices.keys()))

                try:
                    device_address = int(address)
                except ValueError:
                    raise ValueError('the device ID must be an integer.')

                if device_address not in self.devices[device]:
                    raise ValueError(
                        'device %d does not exist.' % device_address)

                try:
                    device_value = int(value)
                except ValueError:
                    raise ValueError('the device value must be an integer.')

                if device_value not in self.devices[device][device_address]:
                    raise ValueError(
                        'device value %d not allowed' % device_value)
                else:
                    attr_name = '%s_%s' % (device, device_address)
                    values = self.devices[device][device_address]
                    attr_value = values[device_value]
                    setattr(self, attr_name, attr_value)
                    return b''

            # Get request
            if b' ' in command and b'?' in command:
                command = command.rstrip('?')
                try:
                    device, address = command.split()
                except ValueError:
                    raise ValueError(
                        'the get command must have two items: '
                        'device and address.'
                    )

                if device not in self.devices:
                    raise ValueError(
                        'device %s not in %s' % (device, self.devices.keys()))

                try:
                    device_address = int(address)
                except ValueError:
                    raise ValueError('the device ID must be an integer.')

                if device_address not in self.devices[device]:
                    raise ValueError(
                        'device %d does not exist.' % device_address)
                else:
                    attr_name = '%s_%s' % (device, device_address)
                    return b'#%s\n' % getattr(self, attr_name)

            # IDN request
            if command == b'*IDN?':
                return self.version

            # RST command
            if command == b'*RST':
                self._set_default()

            # Not expected command
            return b'#COMMAND UNKNOW\n'

# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers.s This list contains tuples (address, args).
# address is the tuple (ip, port) that defines the node, while args is a tuple
# of optional extra arguments.
servers = [(('127.0.0.1', 12000), ())]
