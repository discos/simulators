#!/usr/bin/python
import time
import Queue
import utils
from common import BaseSystem

class Driver(object):

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

    def __init__(self, driver_reset_delay=0):
        self.driver_reset_delay = driver_reset_delay  #Actually it should be 100ms
        self.reset()

    def reset(self):
        self.reference_position = 0
        self.current_position = 0
        self.position_queue = Queue.Queue()

        self.delay_multiplier = 0   # x*delay_step. 255=infinite delay (no response)

        self.version = [1, 3]       # Major, minor
        self.driver_type = 0x20     # 0x20 for USD50xxx, 0x21 for USD60xxx

        self.slope_multiplier = 1

        self.min_frequency = 20
        self.max_frequency = 10000

        self.IO_dir = [0, 0, 0]     # 0 = input, 1 = output
        self.IO_val = [0, 0, 0]     # These values show the corresponding
                                    # I/O line value, but only if the direction
                                    # of the I/O line is set to output
                                    # (IO_dir[x] = 1)

        self.running = False
        self.delayed_execution = False
        self.ready = False
        self.standby_status = True

        self.auto_resolution = True
        self.resolution = self.resolutions.get(0)

        time.sleep(self.driver_reset_delay)

    def soft_reset(self):
        self.reset()

    def soft_trigger(self):
        if self.ready is True and self.running is False:
            self.move_to(self.position_queue.get())
            if self.position_queue.empty() is True:
                self.ready = False

    def get_status(self):
        par0 = 0x00                 #reserved for future use

        par1 = ('0'
                + str(self.IO_dir[2])
                + str(self.IO_dir[1])
                + str(self.IO_dir[0])
                + '0'
                + str(self.IO_val[2])
                + str(self.IO_val[1])
                + str(self.IO_val[0]))

        for key, val in self.resolutions.iteritems():
            if val == self.resolution:
                res = key
                break

        par2 = (str(int(self.running))
                + str(int(self.delayed_execution))
                + str(int(self.ready))
                + str(int(self.standby_status))
                + str(int(self.auto_resolution))
                + bin(res)[2:].zfill(3))

        return (chr(par0)
                + chr(int(par1, base=2))
                + chr(int(par2, base=2)))

    def set_reference_position(self, position):
        # Update enqueued position values?
        self.reference_position = position

    def set_absolute_position(self, position):
        if self.delayed_execution is True:
            self.position_queue.put(self.reference_position + position)
            self.ready = True
        else:
            self.move_to(self.reference_position + position)

    def set_relative_position(self, position):
        if self.delayed_execution is True:
            self.position_queue.put(self.current_position + position)
            self.ready = True
        else:
            self.move_to(self.current_position + position)

    def set_IO_pins(self, param):
        binary_string = bin(param)[2:].zfill(8)

        self.IO_dir[0] = int(binary_string[3], base=2)
        if self.IO_dir[0] == 1:
            self.IO_val[0] = int(binary_string[7], base=2)

        self.IO_dir[1] = int(binary_string[2], base=2)
        if self.IO_dir[1] == 1:
            self.IO_val[1] = int(binary_string[6], base=2)

        self.IO_dir[2] = int(binary_string[1], base=2)
        if self.IO_dir[2] == 1:
            self.IO_val[2] = int(binary_string[5], base=2)

    def set_resolution(self, param):
        if int(param[0]) == 1:
            self.auto_resolution = True
            self.resolution = self.resolutions.get(0)
        else:
            self.auto_resolution = False
            self.resolution = self.resolutions.get(int(param[-3:], base=2))

    def move_to(self, new_position):
        #((freq / resolution) / 200)*60 = RPM
        self.current_position = new_position

class System(BaseSystem):

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
        0x25: "set_IO_pins",
        0x26: "set_resolution",
        0x27: "reduce_current",
        0x28: "set_response_delay",
        0x29: "toggle_delayed_execution",
        0x30: "set_absolute_position",
        0x31: "set_relative_position",
        0x32: "rotate",
        0x35: "set_velocity",
        0x2A: "hard_stop",
        0x2B: "set_positioning_IO",
        0x2C: "set_home_IO",
        0x2D: "set_working_mode",
    }

    byte_switchall = chr(0x00)
    byte_ack = chr(0x06)
    byte_nak = chr(0x15)

    delay_step = 0.000512
    slope_time = 10  # msec

    def __init__(self, driver_reset_delay=0):
        self.create_empty_msg()
        self.drivers = [Driver(driver_reset_delay) for x in xrange(32)]

    def create_empty_msg(self):
        #parsing operation variables
        self.msg = b''
        self.msg_to_all = False
        self.expected_bytes = 0

    def parse(self, byte):
        #Return None or the response.
        #Raise a ValueError in case of unexpected data
        self.msg += byte

        if len(self.msg) == 1:
            if ord(self.msg[0]) != 0xFA and ord(self.msg[0]) != 0xFC:
                self.create_empty_msg()
                return False
            return True
        elif len(self.msg) == 2:
            if ord(self.msg[1]) == 0x00:
                self.msg_to_all = True
            else:
                binary = bin(ord(self.msg[1]))[2:].zfill(8)
                self.expected_bytes = int(binary[:3], base=2)
                if self.expected_bytes > 7 or self.expected_bytes < 1:
                    exp_bytes = self.expected_bytes
                    self.create_empty_msg()
                    raise ValueError(
                        "Wrong byte_nbyte_address value: got %d, expected %d."
                        % (exp_bytes, 7)
                    )
            return True
        elif len(self.msg) == 3:
            if self.msg_to_all == True:
                self.expected_bytes = ord(self.msg[2])
                if self.expected_bytes > 7 or self.expected_bytes < 1:
                    exp_bytes = self.expected_bytes
                    self.create_empty_msg()
                    raise ValueError(
                        "Wrong byte_nbyte value: got %d, expected %d."
                        % (exp_bytes, 7)
                    )
            else:
                self.expected_bytes -= 1
            return True
        else:
            if self.expected_bytes == 0:
                return self.parser(self.msg)
            else:
                self.expected_bytes -= 1
                return True

    def parser(self, msg):
        self.create_empty_msg()

        if utils.checksum(msg[:-1]) != ord(msg[-1]):
            raise ValueError("Checksum error.")

        byte_start = ord(msg[0])

        if msg[1] == self.byte_switchall:
            driver = -1

            nparams = ord(msg[2])
            if nparams + 4 != len(msg):
                return True
            cparams = msg[4:(4+nparams-1)]

            command = ord(msg[3])
        else:
            binary = bin(ord(msg[1]))[2:].zfill(8)

            driver = int(binary[3:], base=2)

            nparams = int(binary[:3], base=2)
            if nparams + 3 != len(msg):
                return True
            cparams = msg[3:(3+nparams-1)]

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
                    time.sleep(self.drivers[driver].delay_multiplier*self.delay_step)
                return(retval)
            else:
                return True
        else:
            raise ValueError("Unknown command: " + hex(command))

    def soft_reset(self, params):
        if len(params[2]) != 0:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for x in range(len(self.drivers)):
                    self.drivers[x].soft_reset()
                return
            else:
                self.drivers[params[0]].soft_reset()
                return self.byte_ack

    def soft_trigger(self, params):
        if len(params[2]) != 0:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for x in range(len(self.drivers)):
                    self.drivers[x].soft_trigger()
                return
            else:
                self.drivers[params[0]].soft_trigger()
                return self.byte_ack

    def get_version(self, params):
        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])
            if params[1] == 0xFA:
                retval += (chr((self.drivers[params[0]].version[0] + 0xF)
                           + self.drivers[params[0]].version[1]))
            elif params[1] == 0xFC:
                byte_nbyte_address = (int(bin(1)[2:].zfill(3)
                                      + bin(params[0])[2:].zfill(5), base=2))
                retval += (chr(byte_nbyte_address)
                           + chr((self.drivers[params[0]].version[0] + 0xF)
                           + self.drivers[params[0]].version[1]))
            else:
                return self.byte_nak
            return retval + chr(utils.checksum(retval))

    def soft_stop(self, params):
        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            #software stop event
            return self.byte_ack

    def get_position(self, params):
        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            bin_position = utils.int_to_twos(self.drivers[params[0]].current_position)

            val = b''

            for i in range(0, len(bin_position), 8):
                val += chr(int(bin_position[i:i+8], base=2))

            if params[1] == 0xFA:
                retval += val
            elif params[1] == 0xFC:
                byte_nbyte_address = (int(bin(4)[2:].zfill(3)
                                      + bin(params[0])[2:].zfill(5), base=2))
                retval += chr(byte_nbyte_address) + val
            else:
                return self.byte_nak

            return retval + chr(utils.checksum(retval))

    def get_status(self, params):
        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            status = self.drivers[params[0]].get_status()

            if params[1] == 0xFA:
                retval += status
            elif params[1] == 0xFC:
                byte_nbyte_address = (int(bin(3)[2:].zfill(3)
                                      + bin(params[0])[2:].zfill(5), base=2))
                retval += chr(byte_nbyte_address) + status
            else:
                return self.byte_nak
            return retval + chr(utils.checksum(retval))

    def get_driver_type(self, params):
        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            if params[1] == 0xFA:
                retval += chr(self.drivers[params[0]].driver_type)
            elif params[1] == 0xFC:
                byte_nbyte_address = (int(bin(1)[2:].zfill(3)
                                      + bin(params[0])[2:].zfill(5), base=2))
                retval += (chr(byte_nbyte_address)
                           + chr(self.drivers[params[0]].driver_type))
            else:
                return self.byte_nak
            return retval + chr(utils.checksum(retval))

    def set_min_frequency(self, params):
        if len(params[2]) != 2:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            frequency = params[2][0]*0x100 + params[2][1]

            if frequency >= 20 and frequency <= 10000:
                if params[0] == -1:
                    for x in range(len(self.drivers)):
                        if frequency <= self.drivers[x].max_frequency:
                            self.drivers[x].min_frequency = frequency
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
            frequency = params[2][0]*0x100 + params[2][1]

            if frequency >= 20 and frequency <= 10000:
                if params[0] == -1:
                    for x in range(len(self.drivers)):
                        if frequency >= self.drivers[x].min_frequency:
                            self.drivers[x].max_frequency = frequency
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
                for x in range(len(self.drivers)):
                    self.drivers[x].slope_multiplier = slope_multiplier
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
            reference_position = utils.twos_to_int(bin(params[2][0]*0x1000000
                                                 + params[2][1]*0x10000
                                                 + params[2][2]*0x100
                                                 + params[2][3])[2:].zfill(32))

            if params[0] == -1:
                for x in range(len(self.drivers)):
                    self.drivers[x].reference_position = reference_position
                return
            else:
                self.drivers[params[0]].reference_position = reference_position
                return self.byte_ack

    def set_IO_pins(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for x in range(len(self.drivers)):
                    self.drivers[x].set_IO_pins(params[2][0])
                return
            else:
                self.drivers[params[0]].set_IO_pins(params[2][0])
                return self.byte_ack

    def set_resolution(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            param = bin(params[2][0])[2:].zfill(4)

            if params[0] == -1:
                for x in range(len(self.drivers)):
                    self.drivers[x].set_resolution(param)
                return
            else:
                self.drivers[params[0]].set_resolution(param)
                return self.byte_ack

    def reduce_current(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            binary = bin(params[2][0])[2:].zfill(8)

            current_demultiplier = int(binary[0:2], base=2)
            delay_multiplier = int(binary[2:], base=2)

            #change values accordingly
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def set_response_delay(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            if params[0] == -1:
                for x in range(len(self.drivers)):
                    self.drivers[x].delay_multiplier = params[2][0]
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
            byte_par0 = bin(params[2][0])[2:].zfill(8)
            bit7 = byte_par0[0]     #delayed execution, 1=enabled, 0=disabled
            bit6 = byte_par0[1]     #unused
            bit5 = byte_par0[2]     #I/O2 level
            bit4 = byte_par0[3]     #I/O1 level
            bit3 = byte_par0[4]     #I/O0 level
            bit2 = byte_par0[5]     #I/O2 enabling bit
            bit1 = byte_par0[6]     #I/O1 enabling bit
            bit0 = byte_par0[7]     #I/O0 enabling bit

            #change values accordingly
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def set_absolute_position(self, params):
        if len(params[2]) != 4:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            absolute_position = utils.twos_to_int(bin(params[2][0]*0x1000000
                                            + params[2][1]*0x10000
                                            + params[2][2]*0x100
                                            + params[2][3])[2:].zfill(32))
            if params[0] == -1:
                for x in range(len(drivers)):
                    self.drivers[x].set_absolute_position(absolute_position)
                return
            else:
                self.drivers[params[0]].set_absolute_position(absolute_position)
                return self.byte_ack

    def set_relative_position(self, params):
        if len(params[2]) != 4:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            relative_position = utils.twos_to_int(bin(params[2][0]*0x1000000
                                                + params[2][1]*0x10000
                                                + params[2][2]*0x100
                                                + params[2][3])[2:].zfill(32))
            if params[0] == -1:
                for x in range(len(drivers)):
                    self.drivers[x].set_relative_position(relative_position)
                return
            else:
                self.drivers[params[0]].set_relative_position(relative_position)
                return self.byte_ack

    def rotate(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            speed = utils.twos_to_int(bin(params[2][0])[2:].zfill(8))

            #rotate according to speed, sign = direction of rotation
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def set_velocity(self, params):
        if len(params[2]) != 3:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            velocity = utils.twos_to_int(bin(params[2][0]*0x10000
                                       + params[2][1]*0x100
                                       + params[2][2])[2:].zfill(24))
            if velocity > 100000 or velocity < -100000:
                if params[0] == -1:
                    return
                else:
                    return self.byte_nak
            else:
                #set velocity
                if params[0] == -1:
                    return
                else:
                    return self.byte_ack

    def hard_stop(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            byte_par0 = bin(params[2][0])[2:].zfill(8)
            bit7 = byte_par0[0]     #unused
            bit6 = byte_par0[1]     #unused
            bit5 = byte_par0[2]     #I/O2 level
            bit4 = byte_par0[3]     #I/O1 level
            bit3 = byte_par0[4]     #I/O0 level
            bit2 = byte_par0[5]     #I/O2 enabling bit
            bit1 = byte_par0[6]     #I/O1 enabling bit
            bit0 = byte_par0[7]     #I/O0 enabling bit

            #change values accordingly
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def set_positioning_IO(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            byte_par0 = bin(params[2][0])[2:].zfill(8)
            bit7 = byte_par0[0]     #unused
            bit6 = byte_par0[1]     #unused
            bit5 = byte_par0[2]     #I/O2 level
            bit4 = byte_par0[3]     #I/O1 level
            bit3 = byte_par0[4]     #I/O0 level
            bit2 = byte_par0[5]     #I/O2 enabling bit
            bit1 = byte_par0[6]     #I/O1 enabling bit
            bit0 = byte_par0[7]     #I/O0 enabling bit

            #change values accordingly
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def set_home_IO(self, params):
        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            byte_par0 = bin(params[2][0])[2:].zfill(8)
            bit7 = byte_par0[0]     #unused
            bit6 = byte_par0[1]     #unused
            bit5 = byte_par0[2]     #I/O2 level
            bit4 = byte_par0[3]     #I/O1 level
            bit3 = byte_par0[4]     #I/O0 level
            bit2 = byte_par0[5]     #I/O2 enabling bit
            bit1 = byte_par0[6]     #I/O1 enabling bit
            bit0 = byte_par0[7]     #I/O0 enabling bit

            #change values accordingly
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def set_working_mode(self, params):
        if len(params[2]) != 2:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            byte_par0 = bin(params[2][0])[2:].zfill(8)
            bit7 = byte_par0[0]     #unused
            bit6 = byte_par0[1]     #unused
            bit5 = byte_par0[2]     #unused
            bit4 = byte_par0[3]     #unused
            bit3 = byte_par0[4]     #unused
            bit2 = byte_par0[5]     #unused
            bit1 = byte_par0[6]     #unused
            bit0 = byte_par0[7]     # BAUD rate, 0 = 9600, 1 = 19200

            byte_par1 = bin(params[2][0])[2:].zfill(8)  #reserved for future use

            if params[0] == -1:
                return
            else:
                return self.byte_ack

"""if __name__ == '__main__':
    AS = System()

    msg = b''

    while True:
        var = raw_input()

        if var == "c":
            var = utils.checksum(msg)
            msg = b''
        else:
            var = int(var, base=16)
            msg += chr(var)
        try:
            response = AS.parse(chr(var))
            if response is not None:
                if type(response) is bool:
                    print(response)
                    if response is False:
                        msg = b''
                else:
                    print([hex(ord(x)) for x in response])
        except ValueError as ve:
            print(ve.args[0])"""
