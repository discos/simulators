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
    return int(bin_sum_fixed_lenght, base=2) ^ 0xFF
    

def twos_to_int(binary_string):
    val = int(binary_string, base=2)
    if (val & (1 << (len(binary_string) - 1))) != 0:
        val = val - (1 << len(binary_string))
    return val

def int_to_twos(val):
    binary_string = bin(val & int("1"*32, 2))[2:]
    return ("{0:0>%s}" % 32).format(binary_string)

def mjd():
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

    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or (year == 1582 and month < 10) or (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)

    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)

    D = math.trunc(30.6001 * (monthp + 1))

    jd = B + C + D + day + 1720994.5

    return jd - 2400000.5 + float((((((utcnow.hour * 60) + utcnow.minute) * 60) + utcnow.second) * 1000000) + utcnow.microsecond) / 86400000000

def day_milliseconds():
    utcnow = datetime.utcnow()

    return ((((((utcnow.hour * 60) + utcnow.minute) * 60) + utcnow.second) * 1000000) + utcnow.microsecond) / 1000


if __name__ == '__main__':
    import doctest
    doctest.testmod()
