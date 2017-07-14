from common import BaseSystem
import time

class as_driver(object):

    def __init__(self):

        self.current_position = 0

        self.delay_multiplier = 0

        self.version = [1, 3]               # Major, minor

        self.slope_multiplier = 1

        self.driver_type = 0x20             # 0x20 for USD50xxx, 0x21 for USD60xxx

        self.reference_position = 0

        self.min_frequency = 20
        self.max_frequency = 10000

        self.IO_pins = 0x00

    def soft_reset(self):

        self.__init__()

    def set_absolute_position(self, position):

        self.current_position = self.reference_position + position

    def set_relative_position(self, position):

        self.current_position += position

class System(BaseSystem):

    functions = {
        0x01: "soft_reset",
        0x02: "soft_trigger",
        0x10: "get_version",
        0x11: "stop",
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
    #protocol_header = [chr(0xFA), chr(0xFC)]

    delay_step = 0.000512
    slope_time = 10             # msec

    drivers = [as_driver() for x in xrange(32)]

    def __init__(self):

        #parsing operation variables
        self.msg = b''
        self.msg_to_all = False
        self.expected_bytes = 0

    def checksum(self, msg):

        return int(bin(sum([ord(x) for x in msg]))[2:].zfill(8)[-8:], base = 2) ^ 0xFF

    def twos_complement(self, binary_string):

        val = int(binary_string, base = 2)
        if (val & (1 << (len(binary_string) - 1))) != 0:
            val = val - (1 << len(binary_string))
        return val

    def parse(self, byte):

        #Return None or the response.  Raise a ValueError in case of unexpected data
        self.msg += chr(byte)

        if len(self.msg) == 1:
            if ord(self.msg[0]) != 0xFA and ord(self.msg[0]) != 0xFC:
                self.__init__()
                return False
            return True
        elif len(self.msg) == 2:
            if ord(self.msg[1]) == 0x00:
                self.msg_to_all = True
            else:
                binary = bin(ord(self.msg[1]))[2:].zfill(8)

                self.expected_bytes = int(binary[:3], base = 2)

                if self.expected_bytes > 7:
                    self.__init__()
                    return False
            return True
        elif len(self.msg) == 3:
            if self.msg_to_all == True:
                self.expected_bytes = ord(self.msg[2])
                if self.expected_bytes > 7:
                    self.__init__()
                    return False
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

        self.__init__()

        checksum = self.checksum(msg[:-1])

        if checksum != ord(msg[-1]):
            return True

        byte_start = ord(msg[0])

        if msg[1] == self.byte_switchall:
            driver = -1
            nparams = ord(msg[2])

            if nparams + 4 != len(msg):
                return True

            cparams = msg[4:(4 + nparams - 1)]

            command = ord(msg[3])
        else:
            binary = bin(ord(msg[1]))[2:].zfill(8)

            driver = int(binary[3:], base = 2)
            nparams = int(binary[:3], base = 2)

            if nparams + 3 != len(msg):
                return True

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
                    time.sleep(self.drivers[driver].delay_multiplier * self.delay_step)
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

        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            #TRIGGER event
            return self.byte_ack

    def get_version(self, params):

        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])
            if params[1] == 0xFA:
                retval += chr((self.drivers[params[0]].version[0] + 0xF) + self.params[0].version[1])
            elif params[1] == 0xFC:
                byte_nbyte_address = int(bin(1)[2:].zfill(3) + bin(params[0])[2:].zfill(5), base = 2)
                retval += chr(byte_nbyte_address) + chr((self.drivers[params[0]].version[0] + 0xF) + self.params[0].version[1])
            else:
                return self.byte_nak
            checksum = self.checksum(retval)
            return retval + chr(checksum)

    def stop(self, params):

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
            byte_pos_0 = 0x00
            byte_pos_1 = 0x01
            byte_pos_2 = 0x02
            byte_pos_3 = 0x03
            if params[1] == 0xFA:
                retval += chr(byte_pos_0) + chr(byte_pos_1) + chr(byte_pos_2) + chr(byte_pos_3)
            elif params[1] == 0xFC:
                byte_nbyte_address = int(bin(4)[2:].zfill(3) + bin(params[0])[2:].zfill(5), base = 2)
                retval += chr(byte_nbyte_address) + chr(byte_pos_0) + chr(byte_pos_1) + chr(byte_pos_2) + chr(byte_pos_3)
            else:
                return self.byte_nak
            checksum = self.checksum(retval)
            return retval + chr(checksum)

    def get_status(self, params):

        if params[0] == -1:
            return
        if len(params[2]) != 0:
            return self.byte_nak
        else:
            retval = self.byte_ack + chr(params[1])

            byte_par0 = 0x00    #reserved for future use

            byte1_bit7 = '0'    #unused
            byte1_bit6 = '0'    #direction of I/O pin 2. 0 = input, 1 = output
            byte1_bit5 = '0'    #direction of I/O pin 1
            byte1_bit4 = '0'    #direction of I/O pin 0
            byte1_bit3 = '0'    #unused
            byte1_bit2 = '0'    #I/O pin 2
            byte1_bit1 = '0'    #I/O pin 1
            byte1_bit0 = '0'    #I/O pin 0
            byte_par1 = int(byte1_bit7 + byte1_bit6 + byte1_bit5 + byte1_bit4 + byte1_bit3 + byte1_bit2 + byte1_bit1 + byte1_bit0, base = 2)

            byte2_bit7 = '0'    # 1 = motor in movement, 0 = motor not in movement
            byte2_bit6 = '0'    # 1 = delayed execution
            byte2_bit5 = '0'    # 1 = ready
            byte2_bit4 = '0'    # standby status: 1 = full current, 0 = fractioned current
            byte2_bit3 = '0'    # resolution: 1 = auto, 0 = fixed
            byte2_bit2 = '0'    # bits 2 to 0 show the selected resolution (available only when bit3 = 0, fixed resolution)
            byte2_bit1 = '0'    # 000 = full step
            byte2_bit0 = '0'    # 111 = 1/128 step, in between combinations decrease by a factor of 2 each step (001 = 1/2, 010 = 1/4, ...)
            byte_par2 = int(byte2_bit7 + byte2_bit6 + byte2_bit5 + byte2_bit4 + byte2_bit3 + byte2_bit2 + byte2_bit1 + byte2_bit0, base = 2)
            if params[1] == 0xFA:
                retval += chr(byte_par0) + chr(byte_par1) + chr(byte_par2)
            elif params[1] == 0xFC:
                byte_nbyte_address = int(bin(3)[2:].zfill(3) + bin(params[0])[2:].zfill(5), base = 2)
                retval += chr(byte_nbyte_address) + chr(byte_par0) + chr(byte_par1) + chr(byte_par2)
            else:
                return self.byte_nak
            checksum = self.checksum(retval)
            return retval + chr(checksum)

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
                byte_nbyte_address = int(bin(1)[2:].zfill(3) + bin(params[0])[2:].zfill(5), base = 2)
                retval += chr(byte_nbyte_address) + chr(self.drivers[params[0]].driver_type)
            else:
                return self.byte_nak
            checksum = self.checksum(retval)
            return retval + chr(checksum)

    def set_min_frequency(self, params):

        if len(params[2]) != 2:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            frequency = params[2][0] * 0x100 + params[2][1]

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
            frequency = params[2][0] * 0x100 + params[2][1]

            if frequency >= 20 and frequency <= 10000:
                if params[0] == -1:
                    for x in range(len(self.drivers)):
                        if frequency >= self.drivers[x].min_frequency:
                            self.drivers[x].max_frequency = frequency
                    return
                else:
                    if frequency <= self.drivers[params[0]].min_frequency:
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
            reference_position = self.twos_complement(bin(params[2][0] * 0x1000000 + params[2][1] * 0x10000 + params[2][2] * 0x100 + params[2][3])[2:].zfill(32))

            if params[0] == -1:
                for x in range(len(self.drivers)):
                    drivers[x].reference_position = reference_position
                return
            else:
                drivers[params[0]].reference_position = reference_position
                return self.byte_ack

    def set_IO_pins(self, params):

        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            byte_par0 = bin(params[2][0])[2:].zfill(8)
            bit7 = byte_par0[0]     #unused
            bit6 = byte_par0[1]     #direction of I/O line 2, 1 = input, 0 = output
            bit5 = byte_par0[2]     #direction of I/O line 1
            bit4 = byte_par0[3]     #direction of I/O line 0
            bit3 = byte_par0[4]     #unused
            bit2 = byte_par0[5]     #I/O line 2, if bit 6 = 1 it is ignored, otherwise it sets the output value of I/O line 2 
            bit1 = byte_par0[6]     #I/O line 1, if bit 5 = ...
            bit0 = byte_par0[7]     #I/O line 0, if bit 4 = ...

            #change values accordingly
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def set_resolution(self, params):

        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            byte_par0 = bin(params[2][0])[2:].zfill(4)

            auto_resolution = int(byte_par0[4])     # resolution: 1 = auto, 0 = fixed
            if auto_resolution == 0:
                resolution = int(byte_par0[5:], base = 2)

            #change values accordingly
            if params[0] == -1:
                return
            else:
                return self.byte_ack

    def reduce_current(self, params):

        if len(params[2]) != 1:
            if params[0] == -1:
                return
            else:
                return self.byte_nak
        else:
            binary = bin(params[2][0])[2:].zfill(8)

            current_demultiplier = int(binary[0:2], base = 2)
            delay_multiplier = int(binary[2:], base = 2)

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
            bit7 = byte_par0[0]     #toggle delayed execution, 1 = enabled, 0 = disabled
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
            absolute_position = self.twos_complement(bin(params[2][0] * 0x1000000 + params[2][1] * 0x10000 + params[2][2] * 0x100 + params[2][3])[2:].zfill(32))

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
            relative_position = self.twos_complement(bin(params[2][0] * 0x1000000 + params[2][1] * 0x10000 + params[2][2] * 0x100 + params[2][3])[2:].zfill(32))

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
            speed = self.twos_complement(bin(params[2][0])[2:].zfill(8))

            #rotate according to speed, speed variable sign = direction of rotation
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
            velocity = self.twos_complement(bin(params[2][0] * 0x10000 + params[2][1] * 0x100 + params[2][2])[2:].zfill(24))
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

            byte_par1 = bin(params[2][0])[2:].zfill(8)      #currently unused, reserved for future use

            if params[0] == -1:
                return
            else:
                return self.byte_ack

"""if __name__ == '__main__':

    byte_start = 0xFD

    byte_nbyte_address = 0x25

    byte_command = 0x01
    byte_par0 = 0xFF
    byte_par1 = 0xFF
    byte_par2 = 0xFF
    byte_par3 = 0xFF
    byte_par4 = 0x04
    byte_par5 = 0x05

    AS = System()

    msg = b''

    while True:
        var = raw_input()
        
        if var == "c":
            var = int(bin(sum([ord(x) for x in msg]))[2:].zfill(8)[-8:], base = 2) ^ 0xFF   #checksum
            msg = b''
        else:
            var = int(var, base=16)
            msg += chr(var)
        try:
            response = AS.parse(var)
            if response is not None:
                if type(response) is bool:
                    print(response)
                    if response is False:
                        msg = b''
                else:
                    print([hex(ord(x)) for x in response])
        except ValueError as ve:
            print(ve.args[0])"""
