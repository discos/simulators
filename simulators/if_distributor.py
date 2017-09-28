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

    def __init__(self):
        self.msg = b''

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
            # Check if the command is a setup
            if b' ' in command:
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


# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers.s This list contains tuples (address, args).
# address is the tuple (ip, port) that defines the node, while args is a tuple
# of optional extra arguments.
servers = [(('127.0.0.1', 12000), ())]
