#!/usr/bin/python
"""This library holds various useful functions that are widely used by all the
simulators systems. Most of them handle low level operations such as
conversions to and from binary strings or byte arrays."""
import math
import struct
import importlib
import inspect
import os
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import patch
from simulators.common import BaseSystem


ACS_TO_UNIX_TIME = 10000000


def checksum(msg):
    """Computes the checksum of a string message.

    :param msg: the message of which the checksum will be calculated and
        returned
    :type msg: str
    :return: the checksum of the given string message
    :rtype: chr

    >>> checksum('fooo')
    'L'
    """
    # Remove the notation.  I.e: '0b1111 -> '1111'
    bin_sum = bin(sum(ord(x) for x in msg))[2:]
    # The string should always have lenght 8.  In case
    # there are more than 8 bits, we remove the most
    # significant one:
    # I.e. '101010101' (len 9) -> 01010101 (len 8)
    bin_sum_fixed_lenght = bin_sum.zfill(8)[-8:]
    # Eventually we should return the one complement
    return chr(int(bin_sum_fixed_lenght, 2) ^ 0xFF)


def binary_complement(bin_string, mask=''):
    """Returns the binary complement of bin_string, with bits masked by mask.

    :param bin_string: the binary_string of which the binary complement will be
        calculated
    :param mask: a binary string that will act as mask allowing to complement
        only bin_string's digits corresponding to mask's ones, leaving the
        bin_string's digits corresponding to mask's zeros as they are
    :type bin_string: str
    :type mask: str
    :return: the binary complement of the given bin_string
    :rtype: str

    >>> binary_complement('11010110')
    '00101001'

    >>> binary_complement('10110', '10111')
    '00001'
    """

    if len(mask) > len(bin_string):
        mask = mask[-len(bin_string):]
    else:
        mask = '1' * (len(bin_string) - len(mask)) + mask

    retval = ''

    for index, value in enumerate(bin_string):
        if mask[index] == '1':
            if value == '0':
                retval += '1'
            elif value == '1':
                retval += '0'
            else:
                raise ValueError(
                    f'String {bin_string} is not expressed in binary notation.'
                )
        elif mask[index] == '0':
            retval += '0'
        else:
            raise ValueError(
                f'Mask {mask} is not expressed in binary notation.'
            )

    return retval


def twos_to_int(binary_string):
    """Returns the two's complement of binary_string.

    :param binary_string: the string containing only zeros and ones. It is
        mandatory to pad this value to the desired bits length before passing
        it to the method in order to avoid representation errors.
    :type binary_string: str
    :return: the two's complement of the given binary_string, as an integer
    :rtype: int

    >>> twos_to_int('11111011')
    -5

    >>> binary_string = '111'
    >>> twos_to_int(binary_string)
    -1
    >>> binary_string = binary_string.zfill(8)
    >>> binary_string
    '00000111'
    >>> twos_to_int(binary_string)
    7
    """
    # Convert the binary string to integer without any representation
    val = int(binary_string, 2)
    # Check if the string represents a negative integer
    if (val & (1 << (len(binary_string) - 1))) != 0:
        # Perform two's complement
        val = val - (1 << len(binary_string))
    return val


def int_to_twos(val, n_bytes=4):
    """Returns the two's complement of the given integer as a string of zeroes
    and ones with len = 8*n_bytes.

    :param val: the signed integer to be returned as binary string in two's
        complement
    :param n_bytes: the number of total bytes to use for the given signed
        integer conversion to two's complement
    :type val: int
    :type n_bytes: int
    :return: the two's complement of val, as a binary string
    :rtype: str

    >>> int_to_twos(5)
    '00000000000000000000000000000101'

    >>> int_to_twos(5, 2)
    '0000000000000101'

    >>> int_to_twos(-1625)
    '11111111111111111111100110100111'

    >>> int_to_twos(-1625, 2)
    '1111100110100111'

    >>> int_to_twos(4294967295)
    Traceback (most recent call last):
        ...
    ValueError: 4294967295 out of range (-2147483648, 2147483647).
    """
    n_bits = 8 * n_bytes
    min_range = -int(math.pow(2, n_bits - 1))
    max_range = int(math.pow(2, n_bits - 1)) - 1

    if val < min_range or val > max_range:
        raise ValueError(
            f"{val} out of range ({min_range}, {max_range})."
        )
    binary_string = bin(val & int("1" * n_bits, 2))[2:]
    return f'{binary_string.zfill(n_bits)}'


def binary_to_bytes(binary_string, little_endian=True):
    """Converts a binary string in a string of bytes.

    :param binary_string: the original binary string that has to be converted
        to a byte string
    :param little_endian: boolean indicating whether the returned string should
        be formatted with little endian or big endian notation
    :type binary_string: str
    :type little_endian: bool
    :return: the bytestring representation of binary_string
    :rtype: str

    >>> binary_to_bytes('0110100001100101011011000110110001101111', False)
    b'\x68\x65\x6C\x6C\x6F'
    """
    byte_string = b''

    for i in range(0, len(binary_string), 8):
        byte_string += bytes([int(binary_string[i:i + 8], 2) & 0xFF])

    return byte_string[::-1] if little_endian else byte_string


def binary_to_string(binary_string, little_endian=True):
    """Converts a binary string in a string.

    :param binary_string: the original binary string that has to be converted
        to a string
    :param little_endian: boolean indicating whether the returned string should
        be formatted with little endian or big endian notation
    :type binary_string: str
    :type little_endian: bool
    :return: the string representation of binary_string
    :rtype: str

    >>> binary_to_string('0110100001100101011011000110110001101111', False)
    '\x68\x65\x6C\x6C\x6F'
    """
    return binary_to_bytes(
        binary_string,
        little_endian
    ).decode('latin-1')


def bytes_to_int(byte_string, little_endian=True):
    """Converts a string of bytes to an integer (like C atoi function).

    :param byte_string: the signed integer represented as bytes
    :param little_endian: boolean indicating whether the byte_string param was
        received with little endian or big endian notation
    :type byte_string: bytes
    :type little_endian: bool
    :return: the value of byte_string, converted to signed integer
    :rtype: int

    >>> bytes_to_int(b'hello', False)
    448378203247
    """
    return int.from_bytes(
        byte_string,
        'little' if little_endian else 'big', signed=True
    )


def string_to_int(string, little_endian=True):
    """Converts a string to an integer (like C atoi function).

    :param string: the signed integer represented as bytes
    :param little_endian: boolean indicating whether the byte_string param was
        received with little endian or big endian notation
    :type string: str
    :type little_endian: bool
    :return: the value of byte_string, converted to signed integer
    :rtype: int

    >>> string_to_int('hello', False)
    448378203247
    """
    return bytes_to_int(string.encode('latin-1'), little_endian)


def bytes_to_binary(byte_string, little_endian=True):
    """Converts a string of bytes to a binary string.

    :param byte_string: the byte string to be converted to binary
    :param little_endian: boolean indicating whether the byte_string param was
        received with little endian or big endian notation
    :type byte_string: str
    :type little_endian: bool
    :return: the binary representation of byte_string
    :rtype: str

    >>> bytes_to_binary(b'hi', little_endian=False)
    '0110100001101001'
    """
    binary_string = ''

    if little_endian:
        byte_string = byte_string[::-1]

    for char in byte_string:
        binary_string += bin(char)[2:].zfill(8)

    return binary_string


def string_to_binary(string, little_endian=True):
    """Converts a string of bytes to a binary string.

    :param byte_string: the byte string to be converted to binary
    :param little_endian: boolean indicating whether the byte_string param was
        received with little endian or big endian notation
    :type byte_string: str
    :type little_endian: bool
    :return: the binary representation of byte_string
    :rtype: str

    >>> string_to_binary('hi', little_endian=False)
    '0110100001101001'
    """
    return bytes_to_binary(string.encode('latin-1'), little_endian)


def bytes_to_uint(byte_string, little_endian=True):
    """Converts a string of bytes to an unsigned integer.

    :param byte_string: the unsigned integer represented as bytes
    :param little_endian: boolean indicating whether the byte_string param was
        received with little endian or big endian notation
    :type byte_string: str
    :little_endian: bool
    :return: the value of byte_string, converted to unsigned integer
    :rtype: int

    >>> bytes_to_uint(b'hi', little_endian=False)
    26729
    """
    return int(bytes_to_binary(byte_string, little_endian), 2)


def string_to_uint(string, little_endian=True):
    """Converts a string to an unsigned integer.

    :param string: the unsigned integer represented as string
    :param little_endian: boolean indicating whether the string param was
        received with little endian or big endian notation
    :type string: str
    :little_endian: bool
    :return: the value of string, converted to unsigned integer
    :rtype: int

    >>> string_to_uint('hi', little_endian=False)
    26729
    """
    return bytes_to_uint(string.encode('latin-1'), little_endian)


def real_to_binary(num, precision=1):
    """Returns the binary representation of a floating-point number
    (IEEE 754 standard).
    A single-precision format description can be found here:
    https://en.wikipedia.org/wiki/Single-precision_floating-point_format
    A double-precision format description can be found here:
    https://en.wikipedia.org/wiki/Double-precision_floating-point_format.

    :param num: the floating-point number to be converted
    :param precision: integer indicating whether the floating-point precision
        to be adopted should be single (1) or double (2)
    :type num: float
    :type precision: int
    :return: the binary string of the given floating-point value
    :rtype: str

    >>> real_to_binary(619.34000405413)
    '01000100000110101101010111000011'

    >>> real_to_binary(619.34000405413, 2)
    '0100000010000011010110101011100001010100000010111010011111110111'

    >>> real_to_binary(0.56734, 1)
    '00111111000100010011110100110010'
    """
    if precision == 1:
        return ''.join(
            bin(c).replace('0b', '').rjust(8, '0')
            for c in struct.pack('!f', num)
        )
    elif precision == 2:
        return ''.join(
            bin(c).replace('0b', '').rjust(8, '0')
            for c in struct.pack('!d', num)
        )
    else:
        raise ValueError(f"Unknown precision {precision}.")


def real_to_bytes(num, precision=1, little_endian=True):
    """Returns the bytestring representation of a floating-point number
    (IEEE 754 standard).

    :param num: the floating-point number to be converted
    :param precision: integer indicating whether the floating-point precision
        to be adopted should be single (1) or double (2)
    :param little_endian: boolean indicating whether the byte string should be
        returned with little endian or big endian notation
    :type num: float
    :type precision: int
    :type little_endian: bool
    :return: the bytes string of the given floating-point value
    :rtype: str

    >>> [hex(x) for x in real_to_bytes(436.56, 1, False)]
    ['0x43', '0xda', '0x47', '0xae']

    >>> [hex(x) for x in real_to_bytes(436.56, 2, False)]
    ['0x40', '0x7b', '0x48', '0xf5', '0xc2', '0x8f', '0x5c', '0x29']
    """

    binary_number = real_to_binary(num, precision)
    return binary_to_bytes(binary_number, little_endian=little_endian)


def real_to_string(num, precision=1, little_endian=True):
    """Returns the string representation of a floating-point number
    (IEEE 754 standard).

    :param num: the floating-point number to be converted
    :param precision: integer indicating whether the floating-point precision
        to be adopted should be single (1) or double (2)
    :param little_endian: boolean indicating whether the byte string should be
        returned with little endian or big endian notation
    :type num: float
    :type precision: int
    :type little_endian: bool
    :return: the string of the given floating-point value
    :rtype: str

    >>> [hex(ord(x)) for x in real_to_string(436.56, 1, False)]
    ['0x43', '0xda', '0x47', '0xae']

    >>> [hex(ord(x)) for x in real_to_string(436.56, 2, False)]
    ['0x40', '0x7b', '0x48', '0xf5', '0xc2', '0x8f', '0x5c', '0x29']
    """

    binary_number = real_to_binary(num, precision)
    binary_number = binary_to_bytes(binary_number, little_endian=little_endian)
    return binary_number.decode('latin-1')


def bytes_to_real(bytes_real, precision=1, little_endian=True):
    """Returns the floating-point representation (IEEE 754 standard) of
    bytestring number.

    :param bytes_real: the floating-point number represented as bytes
    :param precision: integer indicating whether the floating-point precision
        to be adopted should be single (1) or double (2)
    :param little_endian: boolean indicating whether the bytes_real param was
        received with little endian or big endian notation
    :type bytes_real: bytes
    :type precision: int
    :type little_endian: bool
    :return: the floating-point value of the given bytes string
    :rtype: float

    >>> round(bytes_to_real(b'\x44\x77\x2C\x31', 1, False), 2)
    988.69

    >>> round(bytes_to_real(b'\x40\x7A\x25\x7D\x2E\x68\x51\x5D', 2, False), 2)
    418.34
    """
    if little_endian:
        bytes_real = bytes_real[::-1]

    if precision == 1:
        return struct.unpack('!f', bytes_real)[0]
    elif precision == 2:
        return struct.unpack('!d', bytes_real)[0]
    else:
        raise ValueError(f"Unknown precision {precision}.")


def string_to_real(string_real, precision=1, little_endian=True):
    """Returns the floating-point representation (IEEE 754 standard) of
    string number.

    :param string_real: the floating-point number represented as string
    :param precision: integer indicating whether the floating-point precision
        to be adopted should be single (1) or double (2)
    :param little_endian: boolean indicating whether the bytes_real param was
        received with little endian or big endian notation
    :type string_real: str
    :type precision: int
    :type little_endian: bool
    :return: the floating-point value of the given bytes string
    :rtype: float

    >>> round(string_to_real('\x44\x77\x2C\x31', 1, False), 2)
    988.69

    >>> round(string_to_real('\x40\x7A\x25\x7D\x2E\x68\x51\x5D', 2, False), 2)
    418.34
    """
    bytes_real = bytes(string_real, 'latin-1')
    return bytes_to_real(bytes_real, precision, little_endian)


def int_to_bytes(val, n_bytes=4, little_endian=True):
    """Returns the bytestring representation of a given signed integer.

    :param val: the signed integer to be converted
    :param n_bytes: the number of bytes to fit the given unsigned integer to
    :param little_endian: boolean indicating whether the byte string should be
        returned with little endian or big endian notation
    :type val: int
    :type n_bytes: int
    :type little_endian: bool
    :return: the bytes string value of the given signed integer
    :rtype: str

    >>> [hex(x) for x in int_to_bytes(354, little_endian=False)]
    ['0x0', '0x0', '0x1', '0x62']
    """
    return val.to_bytes(
        n_bytes,
        "little" if little_endian else "big", signed=True
    )


def int_to_string(val, n_bytes=4, little_endian=True):
    """Returns the string representation of a given signed integer.

    :param val: the signed integer to be converted
    :param n_bytes: the number of bytes to fit the given unsigned integer to
    :param little_endian: boolean indicating whether the byte string should be
        returned with little endian or big endian notation
    :type val: int
    :type n_bytes: int
    :type little_endian: bool
    :return: the string value of the given signed integer
    :rtype: str

    >>> [hex(ord(x)) for x in int_to_string(354, little_endian=False)]
    ['0x0', '0x0', '0x1', '0x62']
    """
    return int_to_bytes(
        val,
        n_bytes,
        little_endian
    ).decode('latin-1')


def uint_to_bytes(val, n_bytes=4, little_endian=True):
    """Returns the bytestring representation of a given unsigned integer.

    :param val: the unsigned integer to be converted
    :param n_bytes: the number of bytes to fit the given unsigned integer to
    :param little_endian: boolean indicating whether the byte string should be
        returned with little endian or big endian notation
    :type val: int
    :type n_bytes: int
    :type little_endian: bool
    :return: the bytes string value of the given unsigned integer
    :rtype: bytes

    >>> [hex(x) for x in uint_to_bytes(657, little_endian=False)]
    ['0x0', '0x0', '0x2', '0x91']
    """

    n_bits = 8 * n_bytes
    min_range = 0
    max_range = int(math.pow(2, n_bits)) - 1

    if val < min_range or val > max_range:
        raise ValueError(f"{val} out of range ({min_range}, {max_range}).")

    return binary_to_bytes(
        bin(val)[2:].zfill(n_bytes * 8),
        little_endian=little_endian
    )


def uint_to_string(val, n_bytes=4, little_endian=True):
    """Returns the string representation of a given unsigned integer.

    :param val: the unsigned integer to be converted
    :param n_bytes: the number of chars to fit the given unsigned integer to
    :param little_endian: boolean indicating whether the byte string should be
        returned with little endian or big endian notation
    :type val: int
    :type n_bytes: int
    :type little_endian: bool
    :return: the string value of the given unsigned integer
    :rtype: str

    >>> [hex(ord(x)) for x in uint_to_string(657, little_endian=False)]
    ['0x0', '0x0', '0x2', '0x91']
    """
    return uint_to_bytes(
        val,
        n_bytes,
        little_endian
    ).decode('latin-1')


def sign(number):
    """Returns the sign (-1, 0, 1) of a given number (int or float) as an int.

    :param number: the number from which the sign will be extracted
    :type number: int
    :return: the sign multiplier of the given number
    :rtype: int

    >>> sign(5632)
    1

    >>> sign(0)
    0

    >>> sign(-264)
    -1
    """

    if not isinstance(number, (int, float)):
        raise ValueError(
            f'{str(number)} is not of a valid datatype. '
            + 'Use only int or float.'
        )
    return int(number and (1, -1)[number < 0])


def mjd(date=None):
    """Returns the modified julian date (MJD) of a given datetime object.
    If no datetime object is given, it returns the current MJD.
    For more informations about modified julian date check the following link:
    https://core2.gsfc.nasa.gov/time/

    :param date: the object to calculate the equivalent modified julian date.
        If None, the current time is used.
    :type date: datetime
    :return: the modified julian date of the given date value
    :rtype: float

    >>> d = datetime(2018, 1, 20, 10, 30, 45, 100000)
    >>> mjd(d)
    58138.43802199074
    """
    if not date:
        date = datetime.utcnow()
    elif date < datetime(1858, 11, 17):
        raise ValueError('Provide a date after Nov 17 1858')

    year = date.year
    month = date.month
    day = date.day

    if month in [1, 2]:
        year = year - 1
        month = month + 12

    a = math.trunc(year / 100.)
    b = 2 - a + math.trunc(a / 4.)
    c = math.trunc(365.25 * year)
    d = math.trunc(30.6001 * (month + 1))

    modified_julian_day = int(b + c + d + day - 679006)

    # Total UTC hours of the day
    day_hour = date.hour
    # Total minutes of the day
    day_minute = (day_hour * 60) + date.minute
    # Total seconds of the day
    day_second = (day_minute * 60) + date.second
    # Total microseconds of the day
    day_microsecond = (day_second * 1000000) + date.microsecond

    day_percent = day_microsecond / 86400000000.
    modified_julian_date = modified_julian_day + day_percent

    return float(modified_julian_date)


def mjd_to_date(original_mjd_date):
    """Returns the UTC date representation of a modified julian date one.

    :param original_mjd_date: a floating point number representing the modified
        julian date to be converted to a datetime object.
    :type original_mjd_date: float
    :return: the datetime object of the given modified julian date
    :rtype: datetime

    >>> mjd_to_date(58138.43802199074)
    datetime.datetime(2018, 1, 20, 10, 30, 45, 100000)
    """
    try:
        if not isinstance(original_mjd_date, (int, float)):
            raise ValueError
        if original_mjd_date < 0:
            raise ValueError
    except ValueError as ex:
        raise ValueError(
            'Provide a non-negative floating-point number!'
        ) from ex

    str_d = repr(original_mjd_date)
    mjdate, microsecond = str_d.split('.')
    mjdate = int(mjdate)
    microsecond = microsecond + (12 - len(microsecond)) * '0'
    microsecond = int(round(float('0.' + microsecond) * 86400000000))

    mjdate += 2400000.5

    mjdate = mjdate + 0.5

    f, i = math.modf(mjdate)
    i = int(i)

    a = math.trunc((i - 1867216.25) / 36524.25)
    b = i + 1 + a - math.trunc(a / 4.)
    c = b + 1524
    d = math.trunc((c - 122.1) / 365.25)
    e = math.trunc(365.25 * d)
    g = math.trunc((c - e) / 30.6001)

    day = int(c - e + f - math.trunc(30.6001 * g))

    if g < 13.5:
        month = g - 1
    else:
        month = g - 13

    if month > 2.5:
        year = d - 4716
    else:
        year = d - 4715

    second, microsecond = divmod(microsecond, 1000000)
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)

    result_date = datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        microsecond
    )

    return result_date


def day_microseconds(date=None):
    """Returns the microseconds elapsed since last midnight UTC.

    :param date: the object to calculate the total day amount of microseconds.
        If None, the current time is used.
    :type date: datetime
    :return: the number of microseconds elapsed since last midnight previous to
        given date
    :rtype: int
    """
    if not date:
        date = datetime.utcnow()
    elif not isinstance(date, datetime):
        raise ValueError('Date parameter must be a datetime object.')

    # Total UTC hours of the day
    day_hours = date.hour
    # Total minutes of the day
    day_minutes = (day_hours * 60) + date.minute
    # Total seconds of the day
    day_seconds = (day_minutes * 60) + date.second
    # Total microseconds of the day
    return (day_seconds * 1000000) + date.microsecond


def day_milliseconds(date=None):
    """Returns the milliseconds elapsed since last midnight UTC.

    :param date: the object to calculate the total day amount of milliseconds.
        If None, the current time is used.
    :type date: datetime
    :return: the number of milliseconds elapsed since last midnight previous to
        given date
    :rtype: int
    """
    if not date:
        date = datetime.utcnow()
    elif not isinstance(date, datetime):
        raise ValueError('Date parameter must be a datetime object.')
    microseconds = day_microseconds(date)
    return int(round(float(microseconds) / 1000))


def day_percentage(date=None):
    """Returns the day percentage. 00:00 = 0.0, 23:59:999999 = 1.0

    :param date: the datetime or timedelta object of which will be calculated
        the equivalent percentage. If None, the current datetime is used.
    :type date: datetime or timedelta
    :return: the percentage of day elapsed since last midnight previous to
        given date
    :rtype: float
    """
    if not date:
        date = datetime.utcnow()

    if isinstance(date, datetime):
        microseconds = day_microseconds(date)
    elif isinstance(date, timedelta):
        microseconds = date.total_seconds() * 1000000
    else:
        raise ValueError('Date parameter must be a datetime object.')

    return microseconds / 86400000000.


def get_multitype_systems(path):
    """Returns a list of `.py` packages containing a `System` class. The path
    in which this method looks is the same path of the module that calls this
    very method. It is meant to be called by a module containing a
    `MultiTypeSystem` class.

    :param path: the path in which the function is going to recursively look
        for `System` classes
    :type path: str
    :return: a list of packages containing a `System` class
    :rtype: list
    """
    path = os.path.abspath(path)
    if os.path.isfile(path):
        path = os.path.dirname(path)
    systems = {}

    def scan_dir(directory):
        systems = {}
        for element in os.listdir(directory):
            f = os.path.join(directory, element)
            if os.path.isfile(f):
                if f[-3:] == '.py' and '__init__' not in f:
                    prefix = os.path.dirname(os.path.abspath(__file__)) + '/'
                    mod = f.replace(prefix, '')
                    mod = mod.replace('.py', '')
                    mod = mod.replace('/', '.')
                    mod = importlib.import_module(f'simulators.{mod}')
                    for _, obj in inspect.getmembers(mod):
                        if inspect.isclass(obj) and obj.__name__ == 'System':
                            if issubclass(obj, BaseSystem):
                                systems[mod.__name__.rsplit('.', 1)[1]] = mod
        return systems
    systems = scan_dir(path)
    return systems


def list_simulators(path=os.path.dirname(os.path.abspath(__file__))):
    """Returns the list of all available simulators in the package.

    :param path: the path in which the function will recursively look for
        simulators `System` classes
    :type path: str
    :return: the list of available simulators
    :rtype: list
    """
    systems = []

    def scan_dir(directory):
        systems = []
        for element in os.listdir(directory):
            f = os.path.join(directory, element)
            if os.path.isdir(f):
                systems += scan_dir(f)
            elif os.path.isfile(f):
                if f.endswith('__init__.py'):
                    prefix = path.rsplit('/', 1)[0] + '/'
                    mod = f.replace(prefix, '')
                    mod = mod.replace('.py', '')
                    mod = mod.replace('/__init__', '')
                    mod = mod.replace('/', '.')
                    mod = importlib.import_module(mod)
                    for _, obj in inspect.getmembers(mod):
                        if inspect.isclass(obj):
                            if obj.__name__ == 'System':
                                systems.append(mod.__name__.rsplit('.', 1)[1])
        return systems
    systems = scan_dir(path)
    systems.sort()
    return systems


class FastTimeMock:
    def __init__(self, speed_factor):
        self._real_time = time.time
        self._real_sleep = time.sleep
        self._real_timer = threading.Timer
        self.speed_factor = speed_factor

        self.start_time = self._real_time()
        self.fake_start = self.start_time

        self._patch_time = patch("time.time", side_effect=self._mock_time)
        self._patch_sleep = patch("time.sleep", side_effect=self._mock_sleep)
        self._patch_timer = patch(
            "threading.Timer",
            side_effect=self._mock_timer
        )

    def _mock_time(self):
        real_elapsed = self._real_time() - self.start_time
        return self.fake_start + real_elapsed * self.speed_factor

    def _mock_sleep(self, seconds):
        self._real_sleep(seconds / self.speed_factor)

    def _mock_timer(self, interval, function, args=None, kwargs=None):
        return self._real_timer(
            interval / self.speed_factor,
            function,
            args or [],
            kwargs or {}
        )

    def start(self):
        self._patch_time.start()
        self._patch_sleep.start()
        self._patch_timer.start()

    def stop(self):
        self._patch_time.stop()
        self._patch_sleep.stop()
        self._patch_timer.stop()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
