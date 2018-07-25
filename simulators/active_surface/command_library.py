from simulators import utils


byte_start_fa = '\xFA'
byte_start_fc = '\xFC'


def _compose(address_on_response, usd_index, byte_command, params=None):
    """This method composes the message according to the USDs communication
    protocol. It merges the byte_start along with the desired usd index, the
    command and its parameters and returns the whole command encoded as a byte
    string.

    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param byte_command: the byte representing the desired command. It's
        handled internally by the other methods.
    :param params: the command parameters. Some commands, especially the `set_`
        commands, receive some parameters. This holds them as a list.
    """

    if address_on_response:
        command = byte_start_fc
    else:
        command = byte_start_fa

    cmd = byte_command
    if params is None:
        params = []
    for param in params:
        cmd += param

    if usd_index is None:
        command += '\x00'
        command += utils.int_to_bytes(
            val=len(cmd),
            n_bytes=1
        )
    else:
        if not isinstance(usd_index, int):
            raise TypeError('Argument usd_index must be an integer.')
        elif usd_index not in range(32):
            raise IndexError('Argument usd_index must be inside range [0:32]')
        else:
            length = bin(len(cmd))[2:].zfill(3)
            address = bin(usd_index)[2:].zfill(5)
            command += utils.int_to_bytes(
                val=utils.twos_to_int(length + address),
                n_bytes=1
            )

    command += cmd
    command += utils.checksum(command)
    return command


def soft_reset(usd_index=None, address_on_response=True):
    """This method returns the soft_reset command, composed using the given
    parameters.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    return _compose(address_on_response, usd_index, '\x01')


def soft_trigger(usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    return _compose(address_on_response, usd_index, '\x02')


def get_version(usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    return _compose(address_on_response, usd_index, '\x10')


def soft_stop(usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    return _compose(address_on_response, usd_index, '\x11')


def get_position(usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    return _compose(address_on_response, usd_index, '\x12')


def get_status(usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    return _compose(address_on_response, usd_index, '\x13')


def get_driver_type(usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    return _compose(address_on_response, usd_index, '\x14')


def set_min_frequency(frequency, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(frequency, int):
        raise TypeError('Argument frequency must be an integer.')

    frequency = utils.int_to_bytes(
        val=frequency,
        n_bytes=2,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x20', frequency)


def set_max_frequency(frequency, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(frequency, int):
        raise TypeError('Argument frequency must be an integer.')

    frequency = utils.int_to_bytes(
        val=frequency,
        n_bytes=2,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x21', frequency)


def set_slope_multiplier(multiplier, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(multiplier, int):
        raise TypeError('Argument multiplier must be an integer.')

    multiplier = utils.int_to_bytes(
        val=multiplier,
        n_bytes=1,
    )
    return _compose(address_on_response, usd_index, '\x22', multiplier)


def set_reference_position(position, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(position, int):
        raise TypeError('Argument position must be an integer.')
    if position < -2147483648 or position > 2147483647:
        raise ValueError(
            'Argument position must be inside range [-2147483648:2147483647].'
        )

    position = utils.int_to_bytes(
        val=position,
        n_bytes=4,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x23', position)


def set_io_pins(byte_value, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_bytes(
            val=byte_value,
            n_bytes=1
        )
    elif isinstance(byte_value, str) and len(byte_value) == 1:
        pass
    else:
        raise TypeError('Argument byte_value must be an integer'
            + 'or a single character string.')
    return _compose(address_on_response, usd_index, '\x25', byte_value)


def set_resolution(resolution, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(resolution, int):
        resolution = utils.uint_to_bytes(
            val=resolution,
            n_bytes=1
        )
    elif isinstance(resolution, str) and len(resolution) == 1:
        pass
    else:
        raise TypeError('Argument resolution must be an integer.')
    return _compose(address_on_response, usd_index, '\x26', resolution)


def reduce_current(byte_value, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_bytes(
            val=byte_value,
            n_bytes=1
        )
    elif isinstance(byte_value, str) and len(byte_value) == 1:
        pass
    else:
        raise TypeError('Argument byte_value must be an integer'
            + 'or a single character string')
    return _compose(address_on_response, usd_index, '\x27', byte_value)


def set_response_delay(delay, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(delay, int):
        raise TypeError('Argument delay must be an integer.')

    delay = utils.uint_to_bytes(
        val=delay,
        n_bytes=1
    )
    return _compose(address_on_response, usd_index, '\x28', delay)


def toggle_delayed_execution(
        byte_value,
        usd_index=None,
        address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_bytes(
            val=byte_value,
            n_bytes=1
        )
    elif isinstance(byte_value, str) and len(byte_value) == 1:
        pass
    else:
        raise TypeError('Argument byte_value must be an integer'
            + 'or a single character string')
    return _compose(address_on_response, usd_index, '\x29', byte_value)


def set_absolute_position(position, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(position, int):
        raise TypeError('Argument position must be an integer.')
    if position < -2147483648 or position > 2147483647:
        raise ValueError(
            'Argument position must be inside range [-2147483648:2147483647].'
        )

    position = utils.int_to_bytes(
        val=position,
        n_bytes=4,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x30', position)


def set_relative_position(position, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(position, int):
        raise TypeError('Argument position must be an integer.')
    if position < -2147483648 or position > 2147483647:
        raise ValueError(
            'Argument position must be inside range [-2147483648:2147483647].'
        )

    position = utils.int_to_bytes(
        val=position,
        n_bytes=4,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x31', position)


def rotate(direction, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(direction, int):
        raise TypeError('Argument direction must be an integer.')

    direction = utils.int_to_bytes(
        val=direction,
        n_bytes=1
    )
    return _compose(address_on_response, usd_index, '\x32', direction)


def set_velocity(velocity, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if not isinstance(velocity, int):
        raise TypeError('Argument velocity must be an integer.')

    velocity = utils.int_to_bytes(
        val=velocity,
        n_bytes=3,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x35', velocity)


def set_stop_io(byte_value, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_bytes(
            val=byte_value,
            n_bytes=1
        )
    elif isinstance(byte_value, str) and len(byte_value) == 1:
        pass
    else:
        raise TypeError('Argument byte_value must be an integer'
            + 'or a single character string')
    return _compose(address_on_response, usd_index, '\x2A', byte_value)


def set_positioning_io(byte_value, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_bytes(
            val=byte_value,
            n_bytes=1
        )
    elif isinstance(byte_value, str) and len(byte_value) == 1:
        pass
    else:
        raise TypeError('Argument byte_value must be an integer'
            + 'or a single character string')
    return _compose(address_on_response, usd_index, '\x2B', byte_value)


def set_home_io(byte_value, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_bytes(
            val=byte_value,
            n_bytes=1
        )
    elif isinstance(byte_value, str) and len(byte_value) == 1:
        pass
    else:
        raise TypeError('Argument byte_value must be an integer'
            + 'or a single character string')
    return _compose(address_on_response, usd_index, '\x2C', byte_value)


def set_working_mode(byte_value, usd_index=None, address_on_response=True):
    """
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_bytes(
            val=byte_value,
            n_bytes=1
        )
    elif isinstance(byte_value, str) and len(byte_value) == 1:
        pass
    else:
        raise TypeError('Argument byte_value must be an integer'
            + 'or a single character string')
    params = [byte_value, '\x00']
    return _compose(address_on_response, usd_index, '\x2D', params)
