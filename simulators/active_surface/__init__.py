import time
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
    l_address = ('127.0.0.1', 11000 + line)
    servers.append((l_address, (), ()))  # No sending servers or extra args


class System(ListeningSystem):
    """The active surface is composed of 8 sectors, and each sector
    has 12 lines of actuators.  The antenna control software must open
    one TCP socket for each line.  This class represents a line."""

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

    delay_step = 0.000512  # 512 microseconds
    slope_time = 10  # msec

    def __init__(self, driver_reset_delay=0):
        #: param driver_reset_delay: a parameter that is passed down to all of
        #: the children USDs. Refer to USD class to further documentation
        self._set_default()
        self.drivers = [USD(driver_reset_delay) for _ in range(32)]

    def _set_default(self):
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

            driver = int(binary[3:], 2)

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
                    + bin(params[0])[2:].zfill(5), 2)
                )
                retval += (
                    chr(byte_nbyte_address)
                    + chr(sum(self.drivers[params[0]].version) + 0xF)
                )
            return retval + utils.checksum(retval)

    def _soft_stop(self, params):
        if params[2]:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.stop = True
                return None
            else:
                self.drivers[params[0]].stop = True
                return self.byte_ack

    def _get_position(self, params):
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
                    + bin(params[0])[2:].zfill(5), 2)
                )
                retval += chr(byte_nbyte_address) + val

            return retval + utils.checksum(retval)

    def _get_status(self, params):
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
                    + bin(params[0])[2:].zfill(5), 2)
                )
                retval += chr(byte_nbyte_address) + status

            return retval + utils.checksum(retval)

    def _get_driver_type(self, params):
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
                    + bin(params[0])[2:].zfill(5), 2)
                )
                retval += (
                    chr(byte_nbyte_address)
                    + chr(self.drivers[params[0]].driver_type)
                )

            return retval + utils.checksum(retval)

    def _set_min_frequency(self, params):
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
        if len(params[2]) != 4:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            reference_position = utils.bytes_to_int(
                [chr(x) for x in params[2]],
                little_endian=False
            )

            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_reference_position(reference_position)
                return None
            else:
                self.drivers[params[0]].set_reference_position(
                    reference_position)
                return self.byte_ack

    def _set_io_pins(self, params):
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
                self.drivers[params[0]].set_absolute_position(
                    absolute_position)
                return self.byte_ack

    def _set_relative_position(self, params):
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
                self.drivers[params[0]].set_relative_position(
                    relative_position)
                return self.byte_ack

    def _rotate(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return None
            else:
                return self.byte_nak
        else:
            param = utils.twos_to_int(bin(params[2][0])[2:].zfill(8))
            sign = +1 if param >= 0 else -1
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
                    self.drivers[params[0]].set_velocity(velocity)
                    return self.byte_ack

    def _set_stop_io(self, params):
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
