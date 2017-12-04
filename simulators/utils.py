#!/usr/bin/python
import math
import struct
from datetime import datetime


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


def binary_to_bytes(binary_string):
    """Convert a binary string in a string of bytes.

    >>> binary_to_bytes('0110100001100101011011000110110001101111')
    '\x68\x65\x6C\x6C\x6F'
    """

    byte_string = b''

    for i in range(0, len(binary_string), 8):
        byte_string += chr(int(binary_string[i:i + 8], 2))

    return byte_string


def bytes_to_int(byte_string):
    """Convert a string of bytes to an integer (like C atoi function).

    >>> bytes_to_int(b'hello')
    448378203247
    """
    binary_string = ''

    for char in byte_string:
        binary_string += bin(ord(char))[2:].zfill(8)

    return twos_to_int(binary_string)


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


def real_to_bytes(num, precision=1):
    """Return the bytestring representation of a floating-point number
    (IEEE 754 standard)."""
    binary_number = real_to_binary(num, precision)
    return binary_to_bytes(binary_number)


def bytes_to_real(bytes_real, precision=1):
    """Return the floating-point representation (IEEE 754 standard)
    of bytestring number."""
    if precision == 1:
        return struct.unpack('!f', bytes_real)[0]
    elif precision == 2:
        return struct.unpack('!d', bytes_real)[0]
    else:
        raise ValueError(
            "Unknown precision %d."
            % (precision)
        )


def int_to_bytes(val, n_bytes=4):
    """Return the bytestring representation of a given signed integer."""
    return binary_to_bytes(int_to_twos(val, n_bytes))


def uint_to_bytes(val, n_bytes=4):
    """Return the bytestring representation of a given unsigned integer."""
    n_bits = 8 * n_bytes
    min_range = 0
    max_range = int(math.pow(2, n_bits)) - 1

    if val < min_range or val > max_range:
        raise ValueError(
            "%d out of range (%d, %d)."
            % (val, min_range, max_range)
        )

    return binary_to_bytes(bin(val)[2:].zfill(n_bytes * 8))


def mjd(time=datetime.utcnow()):
    """Returns the modified julian date (MJD) of a given datetime object.
    If no datetime object is given, it returns the current MJD.
    For more informations about modified julian date check the following link:
    https://bowie.gsfc.nasa.gov/time/"""
    year = time.year
    month = time.month
    day = time.day
    hour = time.hour
    minute = time.minute
    second = time.second
    microsecond = time.microsecond

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

    # Total UTC hours of the day
    day_hours = hour
    # Total minutes of the day
    day_minutes = (day_hours * 60) + minute
    # Total seconds of the day
    day_seconds = (day_minutes * 60) + second
    # Total microseconds of the day
    day_microseconds = (day_seconds * 1000000) + microsecond

    # Day percentage, 00:00 = 0.0, 24:00=1.0
    day_percentage = round(float(day_microseconds) / 86400000000, 6)

    return float(modified_julian_day + day_percentage)


def day_milliseconds():
    """Return the milliseconds elapsed since last midnight UTC."""
    utcnow = datetime.utcnow()

    # Total UTC hours of the day
    day_hours = utcnow.hour
    # Total minutes of the day
    day_minutes = (day_hours * 60) + utcnow.minute
    # Total seconds of the day
    day_seconds = (day_minutes * 60) + utcnow.second
    # Total microseconds of the day
    day_microseconds = (day_seconds * 1000000) + utcnow.microsecond
    return day_microseconds / 1000  # Total milliseconds of the day


if __name__ == '__main__':
    import doctest
    doctest.testmod()
