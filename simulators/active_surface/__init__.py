import time
from threading import Thread
from multiprocessing import Value
from ctypes import c_bool
from SocketServer import ThreadingTCPServer
from simulators import utils
from simulators.common import ListeningSystem
from simulators.active_surface.usd import USD

# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers.s This list contains tuples
# (l_address, s_address, args). l_address is the tuple (ip, port) that
# defines the listening node that exposes the parse method, s_address
# is the tuple that defines the optional sending node that exposes the
# get_message method, while args is a tuple of optional extra arguments.
servers = []
for line in range(96):  # 96 servers
    l_address = ('0.0.0.0', 11000 + line)
    servers.append((l_address, (), ThreadingTCPServer, (1, 17)))
# While the protocol allows up to 32 USDs per line,
# the SRT only has a maximum of 17 USDs on the same line


class System(ListeningSystem):
    """The active surface is composed of 8 sectors, and each sector
    has 12 lines of actuators.  The antenna control software must open
    one TCP socket for each line.  This class represents a line.
    """

    functions = {
        0x01: "_soft_reset",
        0x02: "_soft_trigger",
        0x10: "_get_version",
        0x11: "_soft_stop",
        0x12: "_get_position",
        0x13: "_get_status",
        0x14: "_get_driver_type",
        0x20: "_set_min_frequency",
        0x21: "_set_max_frequency",
        0x22: "_set_slope_multiplier",
        0x23: "_set_reference_position",
        0x25: "_set_io_pins",
        0x26: "_set_resolution",
        0x27: "_reduce_current",
        0x28: "_set_response_delay",
        0x29: "_toggle_delayed_execution",
        0x30: "_set_absolute_position",
        0x31: "_set_relative_position",
        0x32: "_rotate",
        0x35: "_set_velocity",
        0x2A: "_set_stop_io",
        0x2B: "_set_positioning_io",
        0x2C: "_set_home_io",
        0x2D: "_set_working_mode",
    }

    byte_switchall = '\x00'
    byte_ack = '\x06'
    byte_nak = '\x15'

    max_usd_per_line = 32

    delay_step = 0.000512  # 512 microseconds
    slope_time = 10  # msec

    def __init__(self, min_usd_index=0, max_usd_index=31):
        self.initialized = False
        if min_usd_index < 0 or min_usd_index > 31:
            raise ValueError(
                'Choose a minimum USD index between 0 and 31!'
            )
        elif max_usd_index < 0 or max_usd_index > 31:
            raise ValueError(
                'Choose a maximum USD index between 0 and 31!'
            )
        elif max_usd_index < min_usd_index:
            raise ValueError(
                'max_usd_index cannot be lower than min_usd_index!'
            )
        self._set_default()
        self.stop = Value(c_bool, False)
        self.min_usd_index = min_usd_index
        self.drivers = [
            USD() for _ in range(max_usd_index - min_usd_index + 1)
        ]
        self.positioning_thread = Thread(
            target=self._positioning,
            args=(self.drivers, self.stop)
        )
        self.positioning_thread.daemon = True
        self.initialized = True
        self.positioning_thread.start()

    def __del__(self):
        if self.initialized:
            self.stop.value = True
            self.positioning_thread.join()

    def _set_default(self):
        """This method reset the received command string to its default value.
        It is called when a tail character is received or when a command is
        received malformed."""
        self.msg = b''
        self.msg_to_all = False
        self.expected_bytes = 0

    def parse(self, byte):
        self.msg += byte

        if len(self.msg) == 1:
            if self.msg[0] != '\xFA' and self.msg[0] != '\xFC':
                self._set_default()
                return False
            return True
        elif len(self.msg) == 2:
            if ord(self.msg[1]) == 0x00:
                self.msg_to_all = True
            else:
                binary = bin(ord(self.msg[1]))[2:].zfill(8)
                self.expected_bytes = int(binary[:3], 2)
                if self.expected_bytes > 7 or self.expected_bytes < 1:
                    exp_bytes = self.expected_bytes
                    self._set_default()
                    raise ValueError(
                        "Wrong byte_nbyte_address value: got %d, expected %d."
                        % (exp_bytes, 7)
                    )
            return True
        elif len(self.msg) == 3:
            if self.msg_to_all is True:
                self.expected_bytes = ord(self.msg[2])
                if self.expected_bytes > 7 or self.expected_bytes < 1:
                    exp_bytes = self.expected_bytes
                    self._set_default()
                    raise ValueError(
                        "Wrong byte_nbyte value: got %d, expected %d."
                        % (exp_bytes, 7)
                    )
            else:
                self.expected_bytes -= 1
            return True
        else:
            if self.expected_bytes == 0:
                return self._parser(self.msg)
            else:
                self.expected_bytes -= 1
                return True

    def _parser(self, msg):
        """While the `parse` method receives the incoming commands and checks
        for their correctness, this method performs the actual parsing and
        launches the execution of the desired command procedures."""
        self._set_default()

        if utils.checksum(msg[:-1]) != msg[-1]:
            raise ValueError("Checksum error.")

        byte_start = ord(msg[0])

        if msg[1] == self.byte_switchall:
            driver = -1

            nparams = ord(msg[2])
            cparams = msg[4:(4 + nparams - 1)]

            command = ord(msg[3])
        else:
            binary = bin(ord(msg[1]))[2:].zfill(8)

            driver = int(binary[3:], 2) - self.min_usd_index

            nparams = int(binary[:3], 2)
            cparams = msg[3:(3 + nparams - 1)]

            command = ord(msg[2])

        name = self.functions.get(command)
        if name is not None:
            params = [driver, byte_start, [ord(x) for x in cparams]]
            method = getattr(self, name)
            t0 = time.time()
            retval = method(params)
            if driver != -1:
                if self.drivers[driver].delay_multiplier == 255:
                    return True
                else:
                    time_to_sleep = (
                        self.drivers[driver].delay_multiplier
                        * self.delay_step
                    )
                    elapsed_time = time.time() - t0
                    time.sleep(max(0, time_to_sleep - elapsed_time))
                return retval
            else:
                return True
        else:
            raise ValueError("Unknown command: " + hex(command))

    def _soft_reset(self, params):
        """This method calls the desired USD's `soft_reset` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return.
        """
        if params[2]:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.soft_reset()
                return None
            else:
                self.drivers[params[0]].soft_reset()
                return self.byte_ack

    def _soft_trigger(self, params):
        """This method calls the desired USD's `soft_trigger` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return.
        """
        if params[2]:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.soft_trigger()
                return None
            else:
                self.drivers[params[0]].soft_trigger()
                return self.byte_ack

    def _get_version(self, params):
        """This method calls the desired USD's `get_version` method.
        If a broadcast command is received it calls the said method for every
        USD of the line.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted.
        """
        if params[0] == -1:
            return None
        if params[2]:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])
            if params[1] == 0xFA:
                retval += chr(sum(self.drivers[params[0]].version) + 0xF)
            elif params[1] == 0xFC:
                byte_nbyte_address = (
                    int(bin(1)[2:].zfill(3)
                    + bin(params[0] + self.min_usd_index)[2:].zfill(5), 2)
                )
                retval += (
                    chr(byte_nbyte_address)
                    + chr(sum(self.drivers[params[0]].version) + 0xF)
                )
            return retval + utils.checksum(retval)

    def _soft_stop(self, params):
        """This method calls the desired USD's `soft_stop` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted.
        """
        if params[2]:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.soft_stop()
                return None
            else:
                self.drivers[params[0]].soft_stop()
                return self.byte_ack

    def _get_position(self, params):
        """This method calls the desired USD's `get_position` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The response is the actual position of the driver.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted.
        """
        if params[0] == -1:
            return None
        if params[2]:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            binary_position = utils.int_to_twos(
                self.drivers[params[0]].current_position
            )

            val = utils.binary_to_bytes(binary_position, little_endian=False)

            if params[1] == 0xFA:
                retval += val
            elif params[1] == 0xFC:
                byte_nbyte_address = (
                    int(bin(4)[2:].zfill(3)
                    + bin(params[0] + self.min_usd_index)[2:].zfill(5), 2)
                )
                retval += chr(byte_nbyte_address) + val

            return retval + utils.checksum(retval)

    def _get_status(self, params):
        """This method calls the desired USD's `get_status` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The response is the actual status of the driver.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted.
        """
        if params[0] == -1:
            return None
        if params[2]:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            status = self.drivers[params[0]].get_status()

            if params[1] == 0xFA:
                retval += status
            elif params[1] == 0xFC:
                byte_nbyte_address = (
                    int(bin(3)[2:].zfill(3)
                    + bin(params[0] + self.min_usd_index)[2:].zfill(5), 2)
                )
                retval += chr(byte_nbyte_address) + status

            return retval + utils.checksum(retval)

    def _get_driver_type(self, params):
        """This method calls the desired USD's `get_driver_type` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The response is the type of the driver.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted.
        """
        if params[0] == -1:
            return None
        if params[2]:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            if params[1] == 0xFA:
                retval += chr(self.drivers[params[0]].driver_type)
            elif params[1] == 0xFC:
                byte_nbyte_address = (
                    int(bin(1)[2:].zfill(3)
                    + bin(params[0] + self.min_usd_index)[2:].zfill(5), 2)
                )
                retval += (
                    chr(byte_nbyte_address)
                    + chr(self.drivers[params[0]].driver_type)
                )

            return retval + utils.checksum(retval)

    def _set_min_frequency(self, params):
        """This method calls the desired USD's `set_min_frequency` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired
            frequency, received in the form of 2 consecutive bytes.
        """
        if len(params[2]) != 2:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            frequency = utils.bytes_to_int(
                [chr(x) for x in params[2]],
                little_endian=False
            )

            if frequency >= 20 and frequency <= 10000:
                if params[0] == -1:
                    for driver in self.drivers:
                        if frequency <= driver.max_frequency:
                            driver.min_frequency = frequency
                    return None
                else:
                    if frequency <= self.drivers[params[0]].max_frequency:
                        self.drivers[params[0]].min_frequency = frequency
                        return self.byte_ack
                    else:
                        return self.byte_nak
            else:
                if params[0] == -1:
                    return None
                else:
                    return self.byte_nak

    def _set_max_frequency(self, params):
        """This method calls the desired USD's `set_max_frequency` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired
            frequency, received in the form of 2 consecutive bytes.
        """
        if len(params[2]) != 2:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            frequency = utils.bytes_to_int(
                [chr(x) for x in params[2]],
                little_endian=False
            )

            if frequency >= 20 and frequency <= 10000:
                if params[0] == -1:
                    for driver in self.drivers:
                        if frequency >= driver.min_frequency:
                            driver.max_frequency = frequency
                    return None
                else:
                    if frequency >= self.drivers[params[0]].min_frequency:
                        self.drivers[params[0]].max_frequency = frequency
                        return self.byte_ack
                    else:
                        return self.byte_nak
            else:
                if params[0] == -1:
                    return None
                else:
                    return self.byte_nak

    def _set_slope_multiplier(self, params):
        """This method calls the desired USD's `set_slope_multiplier` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired slope
            multiplier, received as a single byte.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            slope_multiplier = params[2][0] + 1

            if params[0] == -1:
                for driver in self.drivers:
                    driver.slope_multiplier = slope_multiplier
                    return None
            else:
                self.drivers[params[0]].slope_multiplier = slope_multiplier
                return self.byte_ack

    def _set_reference_position(self, params):
        """This method calls the desired USD's `set_reference_position` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired
            reference position, received as 4 consecutive bytes.
        """
        if len(params[2]) != 4:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            reference_pos = utils.bytes_to_int(
                [chr(x) for x in params[2]],
                little_endian=False
            )

            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_reference_position(reference_pos)
                return None
            else:
                self.drivers[params[0]].set_reference_position(reference_pos)
                return self.byte_ack

    def _set_io_pins(self, params):
        """This method calls the desired USD's `set_io_pins` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is a byte containing
            the desired IO pins configuration.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_io_pins(params[2][0])
                return None
            else:
                self.drivers[params[0]].set_io_pins(params[2][0])
                return self.byte_ack

    def _set_resolution(self, params):
        """This method calls the desired USD's `set_resolution` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is a byte containing
            the desired resolution configuration.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_resolution(params[2][0])
                return None
            else:
                self.drivers[params[0]].set_resolution(params[2][0])
                return self.byte_ack

    def _reduce_current(self, params):
        """This method calls the desired USD's `reduce_current` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is a byte containing
            the desired configuration for the current reduction of the USD
            after it moves to a given position.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.reduce_current(params[2][0])
                return None
            else:
                self.drivers[params[0]].reduce_current(params[2][0])
                return self.byte_ack

    def _set_response_delay(self, params):
        """This method calls the desired USD's `set_response_delay` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired delay
            multiplier that sets the delay after the given USD sends its
            response, received as 1 byte.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.delay_multiplier = params[2][0]
            else:
                self.drivers[params[0]].delay_multiplier = params[2][0]

            if params[0] == -1:
                return None
            else:
                return self.byte_ack

    def _toggle_delayed_execution(self, params):
        """This method calls the desired USD's `toggle_delayed_execution`
        method. If a broadcast command is received it calls the said method
        for every USD of the line. The possible response are `byte_ack` or
        `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last paramenter is a byte containing
            the desired configuration for the delayed execution.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.toggle_delayed_execution(params[2][0])
                return None
            else:
                self.drivers[params[0]].toggle_delayed_execution(params[2][0])
                return self.byte_ack

    def _set_absolute_position(self, params):
        """This method calls the desired USD's `set_absolute_position` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired
            absolute position to which the USD should move, received as 4
            consecutive bytes.
        """
        if len(params[2]) != 4:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            absolute_position = utils.bytes_to_int(
                [chr(x) for x in params[2]],
                little_endian=False
            )

            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_absolute_position(absolute_position)
                return None
            else:
                driver = self.drivers[params[0]]
                if driver.set_absolute_position(absolute_position):
                    return self.byte_ack
                else:
                    return self.byte_nak

    def _set_relative_position(self, params):
        """This method calls the desired USD's `soft_reset` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired
            position relative to the current one, to which the USD should move,
            received as 4 consecutive bytes.
        """
        if len(params[2]) != 4:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            relative_position = utils.bytes_to_int(
                [chr(x) for x in params[2]],
                little_endian=False
            )

            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_relative_position(relative_position)
                return None
            else:
                driver = self.drivers[params[0]]
                if driver.set_relative_position(relative_position):
                    return self.byte_ack
                else:
                    return self.byte_nak

    def _rotate(self, params):
        """This method calls the desired USD's `soft_reset` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is a signed integer,
            which sign indicates the direction of the rotation of the USD.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            sign = utils.sign(
                utils.twos_to_int(bin(params[2][0])[2:].zfill(8))
            )
            # Start an infinite rotation, sign = direction
            if params[0] == -1:
                for driver in self.drivers:
                    driver.rotate(sign)
                return None
            else:
                if self.drivers[params[0]].rotate(sign):
                    return self.byte_ack
                else:
                    return self.byte_nak

    def _set_velocity(self, params):
        """This method calls the desired USD's `soft_reset` method.
        If a broadcast command is received it calls the said method for every
        USD of the line. The possible response are `byte_ack` or `byte_nak`.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last parameter is the desired
            rotation velocity of the USD, received as 3 consecutive bytes.
        """
        if len(params[2]) != 3:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            velocity = utils.bytes_to_int(
                [chr(x) for x in params[2]],
                little_endian=False
            )

            if velocity > 100000 or velocity < -100000:
                if params[0] == -1:
                    return None
                else:
                    return self.byte_nak
            else:
                if params[0] == -1:
                    for driver in self.drivers:
                        driver.set_velocity(velocity)
                    return None
                else:
                    if self.drivers[params[0]].set_velocity(velocity):
                        return self.byte_ack
                    else:
                        return self.byte_nak

    def _set_stop_io(self, params):
        """This method calls the desired USD's `set_stop_io` method.
        If a broadcast command is received it calls the said method for every
        USD of the line.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last paramenter is a byte containing
            the desired configuration of the io pins able to stop the USD
            movement in an arbitrary way.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_stop_io(params[2][0])
                return None
            else:
                self.drivers[params[0]].set_stop_io(params[2][0])
                return self.byte_ack

    def _set_positioning_io(self, params):
        """This method calls the desired USD's `set_positioning_io` method.
        If a broadcast command is received it calls the said method for every
        USD of the line.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last paramenter is a byte containing
            the desired configuration of the io pins to set whenever a USD
            finishes its movement.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_positioning_io(params[2][0])
                return None
            else:
                self.drivers[params[0]].set_positioning_io(params[2][0])
                return self.byte_ack

    def _set_home_io(self, params):
        """This method calls the desired USD's `set_home_io` method.
        If a broadcast command is received it calls the said method for every
        USD of the line.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last paramenter is a byte containing
            the desired configuration of the io pins able to stop the USD from
            moving and setting the current position as the reference one.
        """
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_home_io(params[2][0])
                return None
            else:
                self.drivers[params[0]].set_home_io(params[2][0])
                return self.byte_ack

    def _set_working_mode(self, params):
        """This method calls the desired USD's `set_working_mode` method.
        If a broadcast command is received it calls the said method for every
        USD of the line.

        :param params: a list of parameters containing the desired driver index
            (-1 for a broadcast command), and the `byte_start` which indicates
            which kind of response the driver should return. In case the
            `byte_start` parameter equals '\xFC' the response should contain
            the address of the USD, if the `byte_start` equals '\xFA', the said
            address should be omitted. The last paramenter is a byte containing
            the desired configuration for the working mode of the given USD.
        """
        if len(params[2]) != 2:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_working_mode(params[2])
                return None
            else:
                self.drivers[params[0]].set_working_mode(params[2])
                return self.byte_ack

    @staticmethod
    def _positioning(drivers, stop):
        t0 = time.time()
        while not stop.value:
            t1 = time.time()
            elapsed = t1 - t0
            t0 = t1

            for driver in drivers:
                driver.calc_position(elapsed)

            t2 = time.time()
            elapsed = t2 - t1
            time.sleep(max(0.01 - elapsed, 0))
