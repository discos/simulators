import math
from datetime import datetime


def checksum(msg):
    """Return the checksum of a string message.

    >>> checksum('foo')
    187
    """
    # Remove the notation.  I.e: '0b1111 -> '1111'
    bin_sum = bin(sum(ord(x) for x in msg))[2:]
    # The string should always have lenght 8.  In case
    # there are more than 8 bits, we remove the most
    # significant one:
    # I.e. '101010101' (len 9) -> 01010101 (len 8)
    bin_sum_fixed_lenght = bin_sum.zfill(8)[-8:]
    # Eventually we should return the one complement
    return int(bin_sum_fixed_lenght, 2) ^ 0xFF


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


def int_to_twos(val):
    """Return the two's complement of the given integer as a string of zeroes
    and ones with len = 32.

    >>> int_to_twos(5)
    '00000000000000000000000000000101'

    >>> int_to_twos(-1625)
    '11111111111111111111100110100111'

    >>> int_to_twos(4294967295)
    Traceback (most recent call last):
        ...
    ValueError: 4294967295 out of range (-2147483648, 2147483647).
    """
    if val < -2147483648 or val > 2147483647:
        raise ValueError(
            "%d out of range (%d, %d)."
            % (val, -2147483648, 2147483647)
        )
    binary_string = bin(val & int("1" * 32, 2))[2:]
    return ("{0:0>%s}" % 32).format(binary_string)


def mjd():
    """Return the modified julian date. https://bowie.gsfc.nasa.gov/time/"""
    utcnow = datetime.utcnow()

    year = utcnow.year
    month = utcnow.month
    day = utcnow.day

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

    if yearp < 0:
        c = math.trunc((365.25 * yearp) - 0.75)
    else:
        c = math.trunc(365.25 * yearp)

    d = math.trunc(30.6001 * (monthp + 1))

    jd = b + c + d + day + 1720994.5

    modified_julian_day = jd - 2400000.5

    # Total UTC hours of the day
    day_hours = utcnow.hour
    # Total minutes of the day
    day_minutes = (day_hours * 60) + utcnow.minute
    # Total seconds of the day
    day_seconds = (day_minutes * 60) + utcnow.second
    # Total microseconds of the day
    day_microseconds = (day_seconds * 1000000) + utcnow.microsecond

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
