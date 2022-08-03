#!/usr/bin/python
"""This library can be used to compose the commands to be sent to the USDs
whithout having to handle byte values, checksums or other low level parameters.
Each public method implemented in this class returns a specific command encoded
ad a byte string, ready to be sent via socket to the simulator or, eventually,
the hardware."""
from __future__ import print_function
from simulators import utils


byte_start_fa = '\xFA'
byte_start_fc = '\xFC'


def _compose(address_on_response, usd_index, byte_command, params=None):
    """Composes the message according to the USDs communication protocol.
    It merges the starting byte along with the desired USD index, the desired
    command, its parameters and returns the whole command encoded as a byte
    string.

    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param byte_command: the byte representing the desired command. It has to
        be handled internally by the calling method.
    :param params: the command parameters. Some commands, especially the `set_`
        commands, receive some parameters. This variable holds them as a list.
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
        command += utils.int_to_string(
            val=len(cmd),
            n_bytes=1
        )
    else:
        if not isinstance(usd_index, int):
            raise TypeError('Argument usd_index must be an integer.')
        if usd_index not in range(32):
            raise IndexError('Argument usd_index must be inside range [0:32]')
        length = bin(len(cmd))[2:].zfill(3)
        address = bin(usd_index)[2:].zfill(5)
        command += utils.int_to_string(
            val=utils.twos_to_int(length + address),
            n_bytes=1
        )

    command += cmd
    command += utils.checksum(command)
    return command


def soft_reset(usd_index=None, address_on_response=True):
    """Returns the `soft_reset` command string.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(soft_reset())
    \xfc\x00\x01\x01\x01
    >>> print(soft_reset(address_on_response=False))
    \xfa\x00\x01\x01\x03
    >>> print(soft_reset(usd_index=1))
    \xfc\x21\x01\xe1
    """
    return _compose(address_on_response, usd_index, '\x01')


def soft_trigger(usd_index=None, address_on_response=True):
    """Returns the `soft_trigger` command string.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(soft_trigger())
    \xfc\x00\x01\x02\x00
    >>> print(soft_trigger(address_on_response=False))
    \xfa\x00\x01\x02\x02
    >>> print(soft_trigger(usd_index=1))
    \xfc\x21\x02\xe0
    """
    return _compose(address_on_response, usd_index, '\x02')


def get_version(usd_index=None, address_on_response=True):
    """Returns the `get_version` command string.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(get_version())
    \xfc\x00\x01\x10\xf2
    >>> print(get_version(address_on_response=False))
    \xfa\x00\x01\x10\xf4
    >>> print(get_version(usd_index=1))
    \xfc\x21\x10\xd2
    """
    return _compose(address_on_response, usd_index, '\x10')


def soft_stop(usd_index=None, address_on_response=True):
    """Returns the `soft_stop` command string.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(soft_stop())
    \xfc\x00\x01\x11\xf1
    >>> print(soft_stop(address_on_response=False))
    \xfa\x00\x01\x11\xf3
    >>> print(soft_stop(usd_index=1))
    \xfc\x21\x11\xd1
    """
    return _compose(address_on_response, usd_index, '\x11')


def get_position(usd_index=None, address_on_response=True):
    """Returns the `get_position` command string.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(get_position())
    \xfc\x00\x01\x12\xf0
    >>> print(get_position(address_on_response=False))
    \xfa\x00\x01\x12\xf2
    >>> print(get_position(usd_index=1))
    \xfc\x21\x12\xd0
    """
    return _compose(address_on_response, usd_index, '\x12')


def get_status(usd_index=None, address_on_response=True):
    """Returns the `get_status` command string.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(get_status())
    \xfc\x00\x01\x13\xef
    >>> print(get_status(address_on_response=False))
    \xfa\x00\x01\x13\xf1
    >>> print(get_status(usd_index=1))
    \xfc\x21\x13\xcf
    """
    return _compose(address_on_response, usd_index, '\x13')


def get_driver_type(usd_index=None, address_on_response=True):
    """Returns the `get_driver_type` command string.

    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(get_driver_type())
    \xfc\x00\x01\x14\xee
    >>> print(get_driver_type(address_on_response=False))
    \xfa\x00\x01\x14\xf0
    >>> print(get_driver_type(usd_index=1))
    \xfc\x21\x14\xce
    """
    return _compose(address_on_response, usd_index, '\x14')


def set_min_frequency(frequency, usd_index=None, address_on_response=True):
    """Returns the `set_min_frequency` command string, composed using the given
    frequency parameter.

    :param frequency: the frequency to which the minimum USD frequency should
        be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_min_frequency(1))
    \xfc\x00\x03\x20\x00\x01\xdf
    >>> print(set_min_frequency(1, address_on_response=False))
    \xfa\x00\x03\x20\x00\x01\xe1
    >>> print(set_min_frequency(1, usd_index=1))
    \xfc\x61\x20\x00\x01\x81
    """
    if not isinstance(frequency, int):
        raise TypeError('Argument frequency must be an integer.')

    frequency = utils.int_to_string(
        val=frequency,
        n_bytes=2,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x20', frequency)


def set_max_frequency(frequency, usd_index=None, address_on_response=True):
    """Returns the `set_max_frequency` command string, composed using the given
    frequency parameter.

    :param frequency: the frequency to which the maximum USD frequency should
        be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_max_frequency(1))
    \xfc\x00\x03\x21\x00\x01\xde
    >>> print(set_max_frequency(1, address_on_response=False))
    \xfa\x00\x03\x21\x00\x01\xe0
    >>> print(set_max_frequency(1, usd_index=1))
    \xfc\x61\x21\x00\x01\x80
    """
    if not isinstance(frequency, int):
        raise TypeError('Argument frequency must be an integer.')

    frequency = utils.int_to_string(
        val=frequency,
        n_bytes=2,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x21', frequency)


def set_slope_multiplier(multiplier, usd_index=None, address_on_response=True):
    """Returns the `set_slope_multiplier` command string, composed using the
    given multiplier parameter.

    :param multiplier: the slope multiplier to which the USD slope multiplier
        should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_slope_multiplier(1))
    \xfc\x00\x02\x22\x01\xde
    >>> print(set_slope_multiplier(1, address_on_response=False))
    \xfa\x00\x02\x22\x01\xe0
    >>> print(set_slope_multiplier(1, usd_index=1))
    \xfc\x41\x22\x01\x9f
    """
    if not isinstance(multiplier, int):
        raise TypeError('Argument multiplier must be an integer.')

    multiplier = utils.int_to_string(
        val=multiplier,
        n_bytes=1,
    )
    return _compose(address_on_response, usd_index, '\x22', multiplier)


def set_reference_position(position, usd_index=None, address_on_response=True):
    """Returns the `set_reference_position` command string, composed using the
    given position parameter.

    :param position: the position to which the USD reference position should be
        set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_reference_position(1))
    \xfc\x00\x05\x23\x00\x00\x00\x01\xda
    >>> print(set_reference_position(1, address_on_response=False))
    \xfa\x00\x05\x23\x00\x00\x00\x01\xdc
    >>> print(set_reference_position(1, usd_index=1))
    \xfc\xa1\x23\x00\x00\x00\x01\x3e
    """
    if not isinstance(position, int):
        raise TypeError('Argument position must be an integer.')
    if position < -2147483648 or position > 2147483647:
        raise ValueError(
            'Argument position must be inside range [-2147483648:2147483647].'
        )

    position = utils.int_to_string(
        val=position,
        n_bytes=4,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x23', position)


def set_io_pins(byte_value, usd_index=None, address_on_response=True):
    """Returns the `set_io_pins` command string, composed using the given byte
    parameter.

    :param byte_value: the byte to which the USD io pins should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_io_pins(0))
    \xfc\x00\x02\x25\x00\xdc
    >>> print(set_io_pins(0, address_on_response=False))
    \xfa\x00\x02\x25\x00\xde
    >>> print(set_io_pins(0, usd_index=1))
    \xfc\x41\x25\x00\x9d
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_string(
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
    """Returns the `set_resolution` command string, composed using the given
    resolution parameter.

    :param resolution: the resolution to which the USD resolution should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_resolution(1))
    \xfc\x00\x02\x26\x01\xda
    >>> print(set_resolution(1, address_on_response=False))
    \xfa\x00\x02\x26\x01\xdc
    >>> print(set_resolution(1, usd_index=1))
    \xfc\x41\x26\x01\x9b
    """
    if isinstance(resolution, int):
        resolution = utils.uint_to_string(
            val=resolution,
            n_bytes=1
        )
    elif isinstance(resolution, str) and len(resolution) == 1:
        pass
    else:
        raise TypeError('Argument resolution must be an integer.')
    return _compose(address_on_response, usd_index, '\x26', resolution)


def reduce_current(byte_value, usd_index=None, address_on_response=True):
    """Returns the `reduce_current` command string, composed using the given
    byte parameter.

    :param byte_value: the byte to which the USD byte for reduced current
        should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(reduce_current(0))
    \xfc\x00\x02\x27\x00\xda
    >>> print(reduce_current(0, address_on_response=False))
    \xfa\x00\x02\x27\x00\xdc
    >>> print(reduce_current(0, usd_index=1))
    \xfc\x41\x27\x00\x9b
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_string(
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
    """Returns the `set_response_delay` command string, composed using the
    given delay parameter.

    :param delay: the delay to which the USD delay should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_response_delay(5))
    \xfc\x00\x02\x28\x05\xd4
    >>> print(set_response_delay(5, address_on_response=False))
    \xfa\x00\x02\x28\x05\xd6
    >>> print(set_response_delay(5, usd_index=1))
    \xfc\x41\x28\x05\x95
    """
    if not isinstance(delay, int):
        raise TypeError('Argument delay must be an integer.')

    delay = utils.uint_to_string(
        val=delay,
        n_bytes=1
    )
    return _compose(address_on_response, usd_index, '\x28', delay)


def toggle_delayed_execution(
        byte_value,
        usd_index=None,
        address_on_response=True):
    """Returns the `toggle_delayed_execution` command string, composed using
    the given byte parameter.

    :param byte_value: the byte to which the USD byte for delayed execution
        should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(toggle_delayed_execution(1))
    \xfc\x00\x02\x29\x01\xd7
    >>> print(toggle_delayed_execution(1, address_on_response=False))
    \xfa\x00\x02\x29\x01\xd9
    >>> print(toggle_delayed_execution(1, usd_index=1))
    \xfc\x41\x29\x01\x98
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_string(
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
    """Returns the `set_absolute_position` command string, composed using the
    given position parameter.

    :param position: the absolute position to which the USD should be
        positioned
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_absolute_position(1))
    \xfc\x00\x05\x30\x00\x00\x00\x01\xcd
    >>> print(set_absolute_position(1, address_on_response=False))
    \xfa\x00\x05\x30\x00\x00\x00\x01\xcf
    >>> print(set_absolute_position(1, usd_index=1))
    \xfc\xa1\x30\x00\x00\x00\x01\x31
    """
    if not isinstance(position, int):
        raise TypeError('Argument position must be an integer.')
    if position < -2147483648 or position > 2147483647:
        raise ValueError(
            'Argument position must be inside range [-2147483648:2147483647].'
        )

    position = utils.int_to_string(
        val=position,
        n_bytes=4,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x30', position)


def set_relative_position(position, usd_index=None, address_on_response=True):
    """Returns the `set_relative_position` command string, composed using the
    given position parameter.

    :param position: the relative position to which the USD should be
        positioned
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_relative_position(1))
    \xfc\x00\x05\x31\x00\x00\x00\x01\xcc
    >>> print(set_relative_position(1, address_on_response=False))
    \xfa\x00\x05\x31\x00\x00\x00\x01\xce
    >>> print(set_relative_position(1, usd_index=1))
    \xfc\xa1\x31\x00\x00\x00\x01\x30
    """
    if not isinstance(position, int):
        raise TypeError('Argument position must be an integer.')
    if position < -2147483648 or position > 2147483647:
        raise ValueError(
            'Argument position must be inside range [-2147483648:2147483647].'
        )

    position = utils.int_to_string(
        val=position,
        n_bytes=4,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x31', position)


def rotate(direction, usd_index=None, address_on_response=True):
    """Returns the `rotate` command string, composed using the given direction
    parameter.

    :param direction: the direction to which the USD should start moving
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(rotate(1))
    \xfc\x00\x02\x32\x01\xce
    >>> print(rotate(1, address_on_response=False))
    \xfa\x00\x02\x32\x01\xd0
    >>> print(rotate(1, usd_index=1))
    \xfc\x41\x32\x01\x8f
    """
    if not isinstance(direction, int):
        raise TypeError('Argument direction must be an integer.')

    direction = utils.int_to_string(
        val=direction,
        n_bytes=1
    )
    return _compose(address_on_response, usd_index, '\x32', direction)


def set_velocity(velocity, usd_index=None, address_on_response=True):
    """Returns the `set_velocity` command string, composed using the given
    velocity parameter.

    :param velocity: the velocity with which the USD should be moving
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_velocity(1))
    \xfc\x00\x04\x35\x00\x00\x01\xc9
    >>> print(set_velocity(1, address_on_response=False))
    \xfa\x00\x04\x35\x00\x00\x01\xcb
    >>> print(set_velocity(1, usd_index=1))
    \xfc\x81\x35\x00\x00\x01\x4c
    """
    if not isinstance(velocity, int):
        raise TypeError('Argument velocity must be an integer.')

    velocity = utils.int_to_string(
        val=velocity,
        n_bytes=3,
        little_endian=False
    )
    return _compose(address_on_response, usd_index, '\x35', velocity)


def set_stop_io(byte_value, usd_index=None, address_on_response=True):
    """Returns the `set_stop_io` command string, composed using the given byte
    parameter.

    :param byte_value: the byte to which the USD byte for stop IO should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_stop_io(0))
    \xfc\x00\x02\x2a\x00\xd7
    >>> print(set_stop_io(0, address_on_response=False))
    \xfa\x00\x02\x2a\x00\xd9
    >>> print(set_stop_io(0, usd_index=1))
    \xfc\x41\x2a\x00\x98
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_string(
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
    """Returns the `set_positioning_io` command string, composed using the
    given byte parameter.

    :param byte_value: the byte to which the USD byte for positioning IO should
        be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_positioning_io(0))
    \xfc\x00\x02\x2b\x00\xd6
    >>> print(set_positioning_io(0, address_on_response=False))
    \xfa\x00\x02\x2b\x00\xd8
    >>> print(set_positioning_io(0, usd_index=1))
    \xfc\x41\x2b\x00\x97
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_string(
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
    """Returns the `set_home_io` command string, composed using the given byte
    parameter.

    :param byte_value: the byte to which the USD byte for home IO should be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_home_io(0))
    \xfc\x00\x02\x2c\x00\xd5
    >>> print(set_home_io(0, address_on_response=False))
    \xfa\x00\x02\x2c\x00\xd7
    >>> print(set_home_io(0, usd_index=1))
    \xfc\x41\x2c\x00\x96
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_string(
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
    """Returns the `set_working_mode` command string, composed using the given
    byte parameter.

    :param byte_value: the byte to which the USD byte for working mode should
        be set
    :param usd_index: the desired USD index along the line. For a broadcast
        command usd_index can be set to None.
    :param address_on_response: a boolean indicating whether the command should
        start with the '\xFC' byte (address_on_response=True) or with the
        '\xFA' byte (address_on_response=False).

    >>> print(set_working_mode(0))
    \xfc\x00\x03\x2d\x00\x00\xd3
    >>> print(set_working_mode(0, address_on_response=False))
    \xfa\x00\x03\x2d\x00\x00\xd5
    >>> print(set_working_mode(0, usd_index=1))
    \xfc\x61\x2d\x00\x00\x75
    """
    if isinstance(byte_value, int):
        byte_value = utils.uint_to_string(
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
