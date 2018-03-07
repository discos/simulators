#!/usr/bin/python
import math
import struct
from datetime import datetime, timedelta


def checksum(msg):
    """Return the checksum of a string message.

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
    """Return the binary complement of bin_string, with bits masked by mask.

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
                    'String %s is not expressed in binary notation.' %
                    bin_string
                )
        elif mask[index] == '0':
            retval += '0'
        else:
            raise ValueError(
                'Mask %s is not expressed in binary notation.' %
                mask
            )

    return retval


def twos_to_int(binary_string):
    """Return the two's complement of binary_string.

    >>> twos_to_int('11111011')
    -5

    It is mandatory to pad the binary string to the desired bits length
    before passing it to the method in order to avoid representation errors.

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
    """Return the two's complement of the given integer as a string of zeroes
    and ones with len = 8*n_bytes.

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
            "%d out of range (%d, %d)."
            % (val, min_range, max_range)
        )
    binary_string = bin(val & int("1" * n_bits, 2))[2:]
    return ("{0:0>%s}" % n_bits).format(binary_string)


def binary_to_bytes(binary_string, little_endian=True):
    """Convert a binary string in a string of bytes.

    >>> binary_to_bytes('0110100001100101011011000110110001101111', False)
    '\x68\x65\x6C\x6C\x6F'
    """

    byte_string = b''

    for i in range(0, len(binary_string), 8):
        byte_string += chr(int(binary_string[i:i + 8], 2))

    return byte_string[::-1] if little_endian else byte_string


def bytes_to_int(byte_string, little_endian=True):
    """Convert a string of bytes to an integer (like C atoi function).

    >>> bytes_to_int(b'hello', False)
    448378203247
    """
    binary_string = ''

    if little_endian:
        byte_string = byte_string[::-1]

    for char in byte_string:
        binary_string += bin(ord(char))[2:].zfill(8)

    return twos_to_int(binary_string)


def bytes_to_uint(byte_string, little_endian=True):
    """Convert a string of bytes to an unsigned integer.

    >>> bytes_to_uint(b'hi', little_endian=False)
    26729
    """
    binary_string = ''

    if little_endian:
        byte_string = byte_string[::-1]

    for char in byte_string:
        binary_string += bin(ord(char))[2:].zfill(8)

    return int(binary_string, 2)


def real_to_binary(num, precision=1):
    """Return the binary representation of a floating-point number
    (IEEE 754 standard).
    A single-precision format description can be found here:
    https://en.wikipedia.org/wiki/Single-precision_floating-point_format
    A double-precision format description can be found here:
    https://en.wikipedia.org/wiki/Double-precision_floating-point_format.

    >>> real_to_binary(619.34000405413)
    '01000100000110101101010111000011'

    >>> real_to_binary(619.34000405413, 2)
    '0100000010000011010110101011100001010100000010111010011111110111'

    >>> real_to_binary(0.56734, 1)
    '00111111000100010011110100110010'
    """
    if precision == 1:
        return ''.join(
            bin(ord(c)).replace('0b', '').rjust(8, '0')
            for c in struct.pack('!f', num)
        )
    elif precision == 2:
        return ''.join(
            bin(ord(c)).replace('0b', '').rjust(8, '0')
            for c in struct.pack('!d', num)
        )
    else:
        raise ValueError(
            "Unknown precision %d."
            % (precision)
        )


def real_to_bytes(num, precision=1, little_endian=True):
    """Return the bytestring representation of a floating-point number
    (IEEE 754 standard).

    >>> [hex(ord(x)) for x in real_to_bytes(436.56, 1, False)]
    ['0x43', '0xda', '0x47', '0xae']

    >>> [hex(ord(x)) for x in real_to_bytes(436.56, 2, False)]
    ['0x40', '0x7b', '0x48', '0xf5', '0xc2', '0x8f', '0x5c', '0x29']
    """

    binary_number = real_to_binary(num, precision)
    return binary_to_bytes(binary_number, little_endian=little_endian)


def bytes_to_real(bytes_real, precision=1, little_endian=True):
    """Return the floating-point representation (IEEE 754 standard)
    of bytestring number.

    >>> round(bytes_to_real('\x43\xDA\x47\xAE', 1, False), 2)
    436.56

    >>> round(bytes_to_real('\x40\x7B\x48\xF5\xC2\x8F\x5C\x29', 2, False), 2)
    436.56
    """

    if little_endian:
        bytes_real = bytes_real[::-1]

    if precision == 1:
        return struct.unpack('!f', bytes_real)[0]
    elif precision == 2:
        return struct.unpack('!d', bytes_real)[0]
    else:
        raise ValueError(
            "Unknown precision %d."
            % (precision)
        )


def int_to_bytes(val, n_bytes=4, little_endian=True):
    """Return the bytestring representation of a given signed integer.

    >>> [hex(ord(x)) for x in int_to_bytes(354, little_endian=False)]
    ['0x0', '0x0', '0x1', '0x62']
    """

    return binary_to_bytes(int_to_twos(val, n_bytes), little_endian)


def uint_to_bytes(val, n_bytes=4, little_endian=True):
    """Return the bytestring representation of a given unsigned integer.

    >>> [hex(ord(x)) for x in uint_to_bytes(657, little_endian=False)]
    ['0x0', '0x0', '0x2', '0x91']
    """

    n_bits = 8 * n_bytes
    min_range = 0
    max_range = int(math.pow(2, n_bits)) - 1

    if val < min_range or val > max_range:
        raise ValueError(
            "%d out of range (%d, %d)."
            % (val, min_range, max_range)
        )

    return binary_to_bytes(
        bin(val)[2:].zfill(n_bytes * 8),
        little_endian=little_endian
    )


def sign(number):
    """Returns the sign (-1, 0, 1) of a given number (int or float).

    >>> sign(5632)
    1

    >>> sign(0)
    0

    >>> sign(-264)
    -1
    """

    if not isinstance(number, (int, long, float)):
        raise ValueError(
            '%s is not of a valid datatype. Use only int, long or float.'
            % str(number)
        )
    return number and (1, -1)[number < 0]


def mjd(time=None):
    """Returns the modified julian date (MJD) of a given datetime object.
    If no datetime object is given, it returns the current MJD.
    For more informations about modified julian date check the following link:
    https://bowie.gsfc.nasa.gov/time/

    >>> d = datetime(2018, 1, 20, 10, 30, 45, 100000)
    >>> mjd(d)
    58138.43802199074
    """

    if not time:
        time = datetime.utcnow()

    year = time.year
    month = time.month
    day = time.day

    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month

    # Check where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if (year < 1582 or (year == 1582 and month < 10)
            or (year == 1582 and month == 10 and day < 15)):
        # Before the beginning of Gregorian calendar
        b = 0
    else:
        # After the beginning of Gregorian calendar
        a = math.trunc(yearp / 100.)
        b = 2 - a + math.trunc(a / 4.)

    c = math.trunc(365.25 * yearp)
    d = math.trunc(30.6001 * (monthp + 1))

    jd = b + c + d + day + 1720994.5

    modified_julian_day = jd - 2400000.5

    return float(modified_julian_day + day_percentage(time))


def mjd_to_date(original_mjd_date):
    """Returns the UTC date representation of a modified julian date one.

    >>> mjd_to_date(58138.43802199074)
    datetime.datetime(2018, 1, 20, 10, 30, 45, 100000)
    """
    str_d = str(original_mjd_date)
    mjdate = int(str_d[:str_d.find('.')])
    millisecond = int(float('0.' + str_d[str_d.find('.') + 1:]) * 86400000)

    mjdate += 2400000.5

    mjdate = mjdate + 0.5

    f, i = math.modf(mjdate)
    i = int(i)

    a = math.trunc((i - 1867216.25) / 36524.25)

    if i > 2299160:
        b = i + 1 + a - math.trunc(a / 4.)
    else:
        b = i

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

    second, millisecond = divmod(millisecond, 1000)
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)

    result_date = datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        millisecond * 1000
    )

    return result_date


def day_microseconds(date=None):
    """Return the microseconds elapsed since last midnight UTC."""
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
    microseconds = day_microseconds(date)
    return int(round(float(microseconds) / 1000))


def day_percentage(date=None):
    """Return the day percentage. 00:00 = 0.0, 23:59:999999 = 1.0"""
    if not date:
        date = datetime.utcnow()

    if isinstance(date, datetime):
        microseconds = day_microseconds(date)
    elif isinstance(date, timedelta):
        microseconds = date.total_seconds() * 1000000
    else:
        raise ValueError('Date parameter must be a datetime object.')

    return float(microseconds) / 86400000000


if __name__ == '__main__':
    import doctest
    doctest.testmod()
