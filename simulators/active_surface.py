#!/usr/bin/python
import time
import Queue
from simulators import utils
from simulators.common import BaseSystem


class Driver(object):
    """This class represents a single USD actuator. It is completely handled by
    the active surface System class."""

    standby_delay_step = 0.004096  # 4096 microseconds

    #: Resolution denominator, i.e.:
    #: 0 -> 1/1, full step
    #: 1 -> 1/2, half step
    #: ...
    #: 7 -> 1/128th of step
    resolutions = {
        0: 1,
        1: 2,
        2: 4,
        3: 8,
        4: 16,
        5: 32,
        6: 64,
        7: 128,
    }

    #: Current reduction percentage
    standby_modes = {
        0: 0,
        1: 0,
        2: 0.25,
        3: 0.50,
    }

    baud_rates = {
        0: 9600,
        1: 19200
    }

    def __init__(self, driver_reset_delay=0):
        self.driver_reset_delay = driver_reset_delay  # Real delay: 100ms
        self._set_default()

    def _set_default(self):
        self.reference_position = 0
        self.current_position = 0
        self.position_queue = Queue.Queue()
        self.delay_multiplier = 5  # x * delay_step. 255: no response
        self.standby_delay_multiplier = 0
        self.standby_mode = self.standby_modes.get(0)
        self.current_percentage = 1.0
        self.version = [1, 3]  # Major, minor
        self.driver_type = 0x20  # 0x20: USD50xxx, 0x21: USD60xxx
        self.slope_multiplier = 1
        self.min_frequency = 20
        self.max_frequency = 10000
        self.io_dir = [0, 1, 0]  # 0: input, 1: output
        # The following values show the corresponding I/O line value,
        # but only if the direction of the I/O line is set to output
        # i.e.: (io_dir[x] = 1)
        self.io_val = [0, 0, 0]
        # I/O lines combination that automatically raises the TRIGGER event
        self.trigger_io_level = [0, 0, 0]
        self.trigger_io_enable = [0, 0, 0]
        # I/O lines combination that automatically raises the STOP event
        self.stop_io_level = [0, 0, 0]
        self.stop_io_enable = [0, 0, 0]
        # I/O lines combination assumed by the driver after a positioning event
        self.pos_io_level = [0, 0, 0]
        self.pos_io_enable = [0, 0, 0]
        # I/O lines combination assumed by the driver after positioning to HOME
        self.home_io_level = [0, 0, 0]
        self.home_io_enable = [0, 0, 0]
        self.running = False  # True: driver is moving
        self.delayed_execution = False  # True: positioning by TRIGGER event
        self.ready = False  # True: new position enqueued
        self.standby_status = True  # True: full current, False: fractioned
        self.auto_resolution = True
        self.resolution = self.resolutions.get(0)
        self.velocity = 0
        self.baud_rate = self.baud_rates.get(0)
        self.stop = True

        time.sleep(self.driver_reset_delay)

    def soft_reset(self):
        self._set_default()

    def soft_trigger(self):
        if self.ready is True and self.running is False:
            self._move_to(self.position_queue.get())
            if self.position_queue.empty() is True:
                self.ready = False

    def get_status(self):
        par0 = 0x00  # Reserved for future use

        par1 = (
            '0'
            + str(self.io_dir[2])
            + str(self.io_dir[1])
            + str(self.io_dir[0])
            + '0'
            + str(self.io_val[2])
            + str(self.io_val[1])
            + str(self.io_val[0]))

        for key, val in self.resolutions.iteritems():
            if val == self.resolution:
                res = key
                break

        par2 = (
            str(int(self.running))
            + str(int(self.delayed_execution))
            + str(int(self.ready))
            + str(int(self.standby_status))
            + str(int(self.auto_resolution))
            + bin(res)[2:].zfill(3))

        return (
            chr(par0)
            + chr(int(par1, 2))
            + chr(int(par2, 2)))

    def set_reference_position(self, position):
        # Update enqueued position values?
        self.reference_position = position

    def set_io_pins(self, param):
        binary_string = bin(param)[2:].zfill(8)

        self.io_dir[0] = int(binary_string[3], 2)
        if self.io_dir[0] == 1:
            self.io_val[0] = int(binary_string[7], 2)
        else:
            self.io_val[0] = 0

        self.io_dir[1] = int(binary_string[2], 2)
        if self.io_dir[1] == 1:
            self.io_val[1] = int(binary_string[6], 2)
        else:
            self.io_val[1] = 0

        self.io_dir[2] = int(binary_string[1], 2)
        if self.io_dir[2] == 1:
            self.io_val[2] = int(binary_string[5], 2)
        else:
            self.io_val[2] = 0

    def set_resolution(self, param):
        binary_string = bin(param)[2:].zfill(4)

        if int(binary_string[0], 2) == 1:
            self.auto_resolution = True
            self.resolution = self.resolutions.get(0)
        else:
            self.auto_resolution = False
            self.resolution = self.resolutions.get(int(binary_string[-3:], 2))

    def reduce_current(self, param):
        binary_string = bin(param)[2:].zfill(8)

        self.standby_mode = self.standby_modes.get(int(binary_string[0:2], 2))
        self.standby_delay_multiplier = int(binary_string[2:], 2)

    def toggle_delayed_execution(self, param):
        binary_string = bin(param)[2:].zfill(8)

        self.delayed_execution = bool(binary_string[0])
        # binary_string[1] is currently unused

        self.trigger_io_enable[0] = int(binary_string[7], 2)
        if self.trigger_io_enable[0] == 1:
            self.trigger_io_level[0] = int(binary_string[4], 2)
        else:
            self.trigger_io_level[0] = 0

        self.trigger_io_enable[1] = int(binary_string[6], 2)
        if self.trigger_io_enable[1] == 1:
            self.trigger_io_level[1] = int(binary_string[3], 2)
        else:
            self.trigger_io_level[1] = 0

        self.trigger_io_enable[2] = int(binary_string[5], 2)
        if self.trigger_io_enable[2] == 1:
            self.trigger_io_level[2] = int(binary_string[2], 2)
        else:
            self.trigger_io_level[2] = 0

        # Empty the position queue
        self.position_queue = Queue.Queue()

    def set_absolute_position(self, position):
        if self.delayed_execution is True:
            self.position_queue.put(self.reference_position + position)
            self.ready = True
        else:
            self._move_to(self.reference_position + position)

    def set_relative_position(self, position):
        if self.delayed_execution is True:
            self.position_queue.put(self.current_position + position)
            self.ready = True
        else:
            self._move_to(self.current_position + position)

    def rotate(self, sign):
        if self.running:
            # Failed command, return False so the parser can return a byte_nak
            return False
        else:
            # The following 3 lines should run in a separate thread
            self._accel_ramp(sign)
            self._move(sign * self.max_frequency)
            self._decel_ramp(sign)
            return True

    def set_velocity(self, velocity):
        # Start rotating with given velocity without an acceleration ramp
        self.velocity = velocity

        if velocity != 0:
            self._move(velocity)

    def set_stop_io(self, param):
        binary_string = bin(param)[2:].zfill(8)

        # binary_string[0:2] is currently unused

        self.stop_io_enable[0] = int(binary_string[7], 2)
        if self.stop_io_enable[0] == 1:
            self.stop_io_level[0] = int(binary_string[4], 2)
        else:
            self.stop_io_level[0] = 0

        self.stop_io_enable[1] = int(binary_string[6], 2)
        if self.stop_io_enable[1] == 1:
            self.stop_io_level[1] = int(binary_string[3], 2)
        else:
            self.stop_io_level[1] = 0

        self.stop_io_enable[2] = int(binary_string[5], 2)
        if self.stop_io_enable[2] == 1:
            self.stop_io_level[2] = int(binary_string[2], 2)
        else:
            self.stop_io_level[2] = 0

    def set_positioning_io(self, param):
        binary_string = bin(param)[2:].zfill(8)

        # binary_string[0:2] is currently unused

        self.pos_io_enable[0] = int(binary_string[7], 2)
        if self.pos_io_enable[0] == 1:
            self.pos_io_level[0] = int(binary_string[4], 2)
        else:
            self.pos_io_level[0] = 0

        self.pos_io_enable[1] = int(binary_string[6], 2)
        if self.pos_io_enable[1] == 1:
            self.pos_io_level[1] = int(binary_string[3], 2)
        else:
            self.pos_io_level[1] = 0

        self.pos_io_enable[2] = int(binary_string[5], 2)
        if self.pos_io_enable[2] == 1:
            self.pos_io_level[2] = int(binary_string[2], 2)
        else:
            self.pos_io_level[2] = 0

    def set_home_io(self, param):
        binary_string = bin(param)[2:].zfill(8)

        self.home_io_enable[0] = int(binary_string[7], 2)
        if self.home_io_enable[0] == 1:
            self.home_io_level[0] = int(binary_string[4], 2)
        else:
            self.home_io_level[0] = 0

        self.home_io_enable[1] = int(binary_string[6], 2)
        if self.home_io_enable[1] == 1:
            self.home_io_level[1] = int(binary_string[3], 2)
        else:
            self.home_io_level[1] = 0

        self.home_io_enable[2] = int(binary_string[5], 2)
        if self.home_io_enable[2] == 1:
            self.home_io_level[2] = int(binary_string[2], 2)
        else:
            self.home_io_level[2] = 0

    def set_working_mode(self, params):
        binary_string = bin(params[0])[2:].zfill(8)

        # binary_string[0:7] is currently unused
        self.baud_rate = self.baud_rates.get(int(binary_string[7], 2))

        #  params[1] is currently unused

    def _accel_ramp(self, sign):
        # Should gradually accelerate from 0 to min_frequency to max_frequency
        # Not yet implemented
        # while False:
        #     delta = 0
        #     self.current_position += delta * sign
        pass

    def _decel_ramp(self, sign):
        # Should gradually decelerate from max_frequency to min_frequency to 0
        # Not yet implemented
        # while False:
        #     delta = 0
        #     self.current_position += delta * sign
        pass

    def _move_to(self, new_position):
        # Should be launched in a separate thread
        # ((freq / resolution) / 200) * 60 = RPM

        self.running = True
        sign = -1 if new_position < self.current_position else +1
        self._accel_ramp(sign)

        while self.current_position != new_position:
            if self.stop is False:
                # Immediate positioning, should be done gradually
                # i.e.:
                # delta = sign * ...
                # self.current_position += delta
                self.current_position = new_position
            else:
                # Stop received, execute the deceleration ramp immediately
                break

        self._decel_ramp(sign)
        self.stop = False
        self.running = False
        self._go_standby()

    def _move(self, frequency):
        self.running = True

        while self.stop is False or self.velocity != 0:
            frequency = frequency  # Placeholder to avoid linter errors
            break  # Not yet implemented

        self.running = False
        self._go_standby()

    def _go_standby(self):
        time.sleep(self.standby_delay_multiplier * self.standby_delay_step)
        self.current_percentage = 1.0 - self.standby_mode
        self.standby_status = False if self.standby_mode > 0 else True


class System(BaseSystem):
    """The active surface is composed of 8 sectors, and each sector
    has 12 lines of actuators.  The antenna control software must open
    one TCP socket for each line.  This class represents a line."""

    functions = {
        0x01: "soft_reset",
        0x02: "soft_trigger",
        0x10: "get_version",
        0x11: "soft_stop",
        0x12: "get_position",
        0x13: "get_status",
        0x14: "get_driver_type",
        0x20: "set_min_frequency",
        0x21: "set_max_frequency",
        0x22: "set_slope_multiplier",
        0x23: "set_reference_position",
        0x25: "set_io_pins",
        0x26: "set_resolution",
        0x27: "reduce_current",
        0x28: "set_response_delay",
        0x29: "toggle_delayed_execution",
        0x30: "set_absolute_position",
        0x31: "set_relative_position",
        0x32: "rotate",
        0x35: "set_velocity",
        0x2A: "set_stop_io",
        0x2B: "set_positioning_io",
        0x2C: "set_home_io",
        0x2D: "set_working_mode",
    }

    byte_switchall = '\x00'
    byte_ack = '\x06'
    byte_nak = '\x15'

    delay_step = 0.000512  # 512 microseconds
    slope_time = 10  # msec

    def __init__(self, driver_reset_delay=0):
        self._set_default()
        self.drivers = [Driver(driver_reset_delay) for _ in range(32)]

    def _set_default(self):
        self.msg = b''
        self.msg_to_all = False
        self.expected_bytes = 0

    def parse(self, byte):
        """This method takes a byte (single character string) and returns:
        False when the given byte is not the header, but the header is
        expected, True when the given byte is the header or a following
        expected byte, the response (the string to be sent back to the client)
        when the message is completed.
        The method eventually raises a ValueError in one of the following
        cases: the declared length of the message exceeds the maximum expected
        length, the sent message carries a wrong checksum, the client asks to
        execute an unknown command."""
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
            retval = method(params)
            if driver != -1:
                if self.drivers[driver].delay_multiplier == 255:
                    return True
                else:
                    time.sleep(
                        self.drivers[driver].delay_multiplier
                        * self.delay_step
                    )
                return retval
            else:
                return True
        else:
            raise ValueError("Unknown command: " + hex(command))

    def soft_reset(self, params):
        if params[2]:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.soft_reset()
                return
            else:
                self.drivers[params[0]].soft_reset()
                return self.byte_ack

    def soft_trigger(self, params):
        if params[2]:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.soft_trigger()
                return
            else:
                self.drivers[params[0]].soft_trigger()
                return self.byte_ack

    def get_version(self, params):
        if params[0] == -1:
            return
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

    def soft_stop(self, params):
        if params[2]:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.stop = True
                return
            else:
                self.drivers[params[0]].stop = True
                return self.byte_ack

    def get_position(self, params):
        if params[0] == -1:
            return
        if params[2]:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            binary_position = utils.int_to_twos(
                self.drivers[params[0]].current_position
            )

            val = utils.binary_to_bytes(binary_position)

            if params[1] == 0xFA:
                retval += val
            elif params[1] == 0xFC:
                byte_nbyte_address = (
                    int(bin(4)[2:].zfill(3)
                    + bin(params[0])[2:].zfill(5), 2)
                )
                retval += chr(byte_nbyte_address) + val

            return retval + utils.checksum(retval)

    def get_status(self, params):
        if params[0] == -1:
            return
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

    def get_driver_type(self, params):
        if params[0] == -1:
            return
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

    def set_min_frequency(self, params):
        if len(params[2]) != 2:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            frequency = utils.bytes_to_int([chr(x) for x in params[2]])

            if frequency >= 20 and frequency <= 10000:
                if params[0] == -1:
                    for driver in self.drivers:
                        if frequency <= driver.max_frequency:
                            driver.min_frequency = frequency
                    return
                else:
                    if frequency <= self.drivers[params[0]].max_frequency:
                        self.drivers[params[0]].min_frequency = frequency
                        return self.byte_ack
                    else:
                        return self.byte_nak
            else:
                if params[0] == -1:
                    return
                else:
                    return self.byte_nak

    def set_max_frequency(self, params):
        if len(params[2]) != 2:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            frequency = utils.bytes_to_int([chr(x) for x in params[2]])

            if frequency >= 20 and frequency <= 10000:
                if params[0] == -1:
                    for driver in self.drivers:
                        if frequency >= driver.min_frequency:
                            driver.max_frequency = frequency
                    return
                else:
                    if frequency >= self.drivers[params[0]].min_frequency:
                        self.drivers[params[0]].max_frequency = frequency
                        return self.byte_ack
                    else:
                        return self.byte_nak
            else:
                if params[0] == -1:
                    return
                else:
                    return self.byte_nak

    def set_slope_multiplier(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            slope_multiplier = params[2][0] + 1

            if params[0] == -1:
                for driver in self.drivers:
                    driver.slope_multiplier = slope_multiplier
                    return
            else:
                self.drivers[params[0]].slope_multiplier = slope_multiplier
                return self.byte_ack

    def set_reference_position(self, params):
        if len(params[2]) != 4:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            reference_position = utils.bytes_to_int(
                [chr(x) for x in params[2]]
            )

            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_reference_position(reference_position)
                return
            else:
                self.drivers[params[0]].set_reference_position(
                    reference_position)
                return self.byte_ack

    def set_io_pins(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_io_pins(params[2][0])
                return
            else:
                self.drivers[params[0]].set_io_pins(params[2][0])
                return self.byte_ack

    def set_resolution(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_resolution(params[2][0])
                return
            else:
                self.drivers[params[0]].set_resolution(params[2][0])
                return self.byte_ack

    def reduce_current(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.reduce_current(params[2][0])
                return
            else:
                self.drivers[params[0]].reduce_current(params[2][0])
                return self.byte_ack

    def set_response_delay(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.delay_multiplier = params[2][0]
            else:
                self.drivers[params[0]].delay_multiplier = params[2][0]

            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def toggle_delayed_execution(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.toggle_delayed_execution(params[2][0])
            else:
                self.drivers[params[0]].toggle_delayed_execution(params[2][0])
                return self.byte_ack

    def set_absolute_position(self, params):
        if len(params[2]) != 4:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            absolute_position = utils.bytes_to_int([chr(x) for x in params[2]])

            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_absolute_position(absolute_position)
            else:
                self.drivers[params[0]].set_absolute_position(
                    absolute_position)
                return self.byte_ack

    def set_relative_position(self, params):
        if len(params[2]) != 4:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            relative_position = utils.bytes_to_int([chr(x) for x in params[2]])

            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_relative_position(relative_position)
            else:
                self.drivers[params[0]].set_relative_position(
                    relative_position)
                return self.byte_ack

    def rotate(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            param = utils.twos_to_int(bin(params[2][0])[2:].zfill(8))
            sign = +1 if param >= 0 else -1
            # Start an infinite rotation, sign = direction
            if params[0] == -1:
                for driver in self.drivers:
                    driver.rotate(sign)
            else:
                if self.drivers[params[0]].rotate(sign):
                    return self.byte_ack
                else:
                    return self.byte_nak

    def set_velocity(self, params):
        if len(params[2]) != 3:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            velocity = utils.bytes_to_int([chr(x) for x in params[2]])

            if velocity > 100000 or velocity < -100000:
                if params[0] == -1:
                    return
                else:
                    return self.byte_nak
            else:
                if params[0] == -1:
                    for driver in self.drivers:
                        driver.set_velocity(velocity)
                else:
                    self.drivers[params[0]].set_velocity(velocity)
                    return self.byte_ack

    def set_stop_io(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_stop_io(params[2][0])
            else:
                self.drivers[params[0]].set_stop_io(params[2][0])
                return self.byte_ack

    def set_positioning_io(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_positioning_io(params[2][0])
            else:
                self.drivers[params[0]].set_positioning_io(params[2][0])
                return self.byte_ack

    def set_home_io(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_home_io(params[2][0])
            else:
                self.drivers[params[0]].set_home_io(params[2][0])
                return self.byte_ack

    def set_working_mode(self, params):
        if len(params[2]) != 2:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for driver in self.drivers:
                    driver.set_working_mode(params[2])
            else:
                self.drivers[params[0]].set_working_mode(params[2])
                return self.byte_ack

# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers.s This list contains tuples (address, args).
# address is the tuple (ip, port) that defines the node, while args is a tuple
# of optional extra arguments.
servers = []
for line in range(96):  # 96 lines
    address = ('127.0.0.1', 11000 + line)
    servers.append((address, ()))  # No extra arguments
