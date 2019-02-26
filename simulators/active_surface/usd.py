import time
from Queue import Queue
from threading import Thread


class USD(object):
    """This class represents a single USD actuator driver. It is completely
    handled by the active surface System class.
    """

    driver_reset_delay = 0.1  # 100 milliseconds
    standby_delay_step = 0.004096  # 4096 microseconds

    # Resolution denominator, i.e.:
    # 0 -> 1/1, full step
    # 1 -> 1/2, half step
    # ...
    # 7 -> 1/128th of step
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

    # Current reduction percentage
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

    def __init__(self):
        self._set_default()

    def _set_default(self):
        self.reference_position = 0
        self.current_position = 0
        self.position_queue = Queue()
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
        self.stop = False
        self.running = False
        self.move_thread = None
        self.move_to_thread = None

    def soft_reset(self):
        t0 = time.time()

        self._set_default()

        elapsed_time = time.time() - t0
        time.sleep(max(self.driver_reset_delay - elapsed_time, 0))

    def soft_trigger(self, stop):
        if self.ready is True:
            if self.move_to_thread:
                self.running = False
                time.sleep(0.01)
                self.move_to_thread.join()
                self.move_to_thread = None
            next_position = self.position_queue.get()
            self.running = True
            self.move_to_thread = Thread(
                target=self._move_to,
                args=(next_position, stop)
            )
            self.move_to_thread.daemon = True
            self.move_to_thread.start()
            if self.position_queue.empty() is True:
                self.ready = False

    def soft_stop(self):
        t = Thread(target=self._soft_stop)
        t.daemon = True
        t.start()

    def _soft_stop(self):
        self.stop = True
        time.sleep(0.025)
        self.stop = False

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
        self.position_queue = Queue()

    def set_absolute_position(self, position, stop):
        cmd_position = self.reference_position + position
        if self.delayed_execution is True:
            self.position_queue.put(cmd_position)
            self.ready = True
        else:
            t = Thread(target=self._position, args=(cmd_position, stop))
            t.daemon = True
            t.start()

    def set_relative_position(self, position, stop):
        cmd_position = self.current_position + position
        if self.delayed_execution is True:
            self.position_queue.put(cmd_position)
            self.ready = True
        else:
            t = Thread(target=self._position, args=(cmd_position, stop))
            t.daemon = True
            t.start()

    def rotate(self, sign, stop):
        if self.running:
            # Failed command, return False so the parser can return a byte_nak
            return False
        else:
            t = Thread(target=self._rotate, args=(sign, stop))
            t.daemon = True
            t.start()
            return True

    def _rotate(self, sign, stop):
        self.running = True
        if not self.stop:
            self._accel_ramp(sign)
        if not self.stop:
            cmd_position = 2147483647
            if sign < 0:
                cmd_position += 1
            self._move_to(sign * cmd_position, stop)
        self.running = False

    def set_velocity(self, velocity, stop):
        # Start rotating with given velocity without an acceleration ramp
        self.velocity = velocity

        if velocity != 0:
            self.running = True
            if not self.move_thread:
                self.move_thread = Thread(target=self._move, args=(stop,))
                self.move_thread.daemon = True
                self.move_thread.start()
        else:
            self.running = False
            if self.move_thread:
                self.move_thread.join()
                self.move_thread = None
            self._go_standby()

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

    def _position(self, cmd_position, stop):
        self.running = True
        sign = -1 if cmd_position < self.current_position else +1

        if not self.stop:
            self._accel_ramp(sign)
        if not self.stop:
            self._move_to(cmd_position, stop)
        if not self.stop:
            self._go_standby()
        self.running = False

    def _move_to(self, cmd_position, stop):
        sign0 = -1 if cmd_position < self.current_position else +1
        t0 = time.time()
        while not self.stop and self.running and not stop.value:
            t1 = time.time()
            elapsed = t1 - t0
            t0 = t1
            new_position = self.current_position + int(round(
                (self.max_frequency / self.resolution) * elapsed
            ))
            sign1 = -1 if cmd_position < new_position else +1
            if sign0 != sign1:
                self.current_position = cmd_position
                self.running = False
                break
            else:
                self.current_position = new_position
            time.sleep(0.005)

    def _move(self, stop):
        t0 = time.time()
        while not self.stop and self.running and not stop.value:
            t1 = time.time()
            elapsed = t1 - t0
            t0 = t1
            new_position = self.current_position + int(round(
                (self.velocity / self.resolution) * elapsed
            ))
            if new_position <= -2147483648:
                self.current_position = -2147483648
                self.running = False
                break
            elif new_position >= 2147483647:
                self.current_position = 2147483647
                self.running = False
                break
            else:
                self.current_position = new_position
            time.sleep(0.005)

    def _go_standby(self):
        time.sleep(self.standby_delay_multiplier * self.standby_delay_step)
        self.current_percentage = 1.0 - self.standby_mode
        self.standby_status = False if self.standby_mode > 0 else True
