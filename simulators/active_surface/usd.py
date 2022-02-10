import time
from Queue import Queue
from simulators import utils


class USD(object):
    """USD actuator driver implementation.

    :param usd_index: the index of the USD on its line.
    :type usd_index: int
    """

    driver_reset_delay = 0.1  # 100 milliseconds
    standby_delay_step = 0.004096  # 4096 microseconds
    min_position = -21000 * 128
    max_position = 21000 * 128
    out_of_scale_position = max_position + 1  # Greater than any accepted pos.

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

    def __init__(self, usd_index):
        self._set_default()
        self.last_movement = None
        self.usd_index = usd_index

    def _set_default(self):
        """Called at initialization or reset phases to restore default
        parameters."""
        self.reference_position = 0
        self.current_position = 0
        self.position_queue = Queue()
        self.delay_multiplier = 5  # x * delay_step. 255: no response
        self.standby_delay_multiplier = 0
        self.standby_mode = self.standby_modes.get(0)
        self.current_percentage = 1.0
        self.version = [1, 3]  # Major, minor
        self.driver_type = 0x20  # 0x20: USD50xxx, 0x21: USD60xxx
        self.slope_delayer = 1
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
        self.full_current = True
        self.auto_resolution = False
        self.resolution = self.resolutions.get(1)
        self.velocity = 0
        self.baud_rate = self.baud_rates.get(0)
        self.cmd_position = None
        self.standby = False

    def soft_reset(self):
        """Resets the USD to it default values. When a reset is performed, the
        USD takes approximately 100ms to boot back up."""
        t0 = time.time()

        self._set_default()

        elapsed_time = time.time() - t0
        time.sleep(max(self.driver_reset_delay - elapsed_time, 0))

    def soft_trigger(self):
        """Implements the TRIGGER event for the delayed execution of USD
        movements. Whenever this command is received, if there is at least
        one position in the queue and the USD status is set to ready, the USD
        starts moving towards the desired position."""
        if self.ready is True:
            next_position, absolute = self.position_queue.get()
            if not self.velocity:
                if absolute:
                    self.cmd_position = next_position
                else:
                    self.cmd_position = self.current_position + next_position
            if self.position_queue.empty() is True:
                self.ready = False

    def get_version(self):
        """Returns the USD software version.

        :return: the software version as [major, minor]
        :rtype: list"""
        return self.version

    def soft_stop(self):
        """Immediate stop. The USD stops even if it did not completed its
        previous positioning movement."""
        self.velocity = None
        self.cmd_position = None

    def get_position(self):
        """Returns the USD current position.

        :return: the current position
        :rtype: int"""
        return self.current_position

    def get_status(self):
        """Returns the USD current status.

        :return: the current status
        :rtype: string
        """
        par0 = 0x00  # Reserved for future use

        par1 = (
            '0'
            + str(self.io_dir[2])
            + str(self.io_dir[1])
            + str(self.io_dir[0])
            + '0'
            + str(self.io_val[2])
            + str(self.io_val[1])
            + str(self.io_val[0])
        )

        for key, val in self.resolutions.iteritems():
            if val == self.resolution:
                res = key
                break

        par2 = (
            str(int(self.running))
            + str(int(self.delayed_execution))
            + str(int(self.ready))
            + str(int(self.full_current))
            + str(int(self.auto_resolution))
            + bin(res)[2:].zfill(3)
        )

        return (
            chr(par0)
            + chr(int(par1, 2))
            + chr(int(par2, 2))
        )

    def get_driver_type(self):
        """Returns the USD type.

        :return: the USD type. 0x20: USD50xxx, 0x21: USD60xxx
        :rtype: byte"""
        return self.driver_type

    def set_min_frequency(self, frequency):
        """Sets the minimum USD rotation frequency. If the desired frequency
        is greater than the current maximum frequency, it is considered wrong
        and the parser will return a `byte_nak`.

        :param frequency: the minimum frequency
        :type frequency: int between 20 and 10000
        :return: a boolean indicating whether the given frequency was accepted
            or not
        :rtype: boolean"""
        if frequency < 20 or frequency > 10000:
            return False
        elif frequency > self.max_frequency:
            return False
        self.min_frequency = frequency
        return True

    def set_max_frequency(self, frequency):
        """Sets the maximum USD rotation frequency. If the desired frequency is
        lower than the current minimum frequency, it is considered wrong and
        the parser will return a `byte_nak`.

        :param frequency: the maximum frequency
        :type frequency: int between 20 and 10000
        :return: a boolean indicating whether the given frequency was accepted
            or not
        :rtype: boolean"""
        if frequency < 20 or frequency > 10000:
            return False
        elif frequency < self.min_frequency:
            return False
        self.max_frequency = frequency
        return True

    def set_slope_delayer(self, delayer):
        """Sets the USD acceleration slope delayer. It means that the higher
        the `delayer` parameter, the slower the acceleration will be.

        :param delayer: the desired slope delayer
        :type delayer: int"""
        self.slope_delayer = delayer

    def set_reference_position(self, position):
        """Sets the received position as the reference position (zero pos).

        :param position: the absolute position to be set as reference
        :type position: int between -2147483648 and 2147483647"""
        self.reference_position = position

    def set_io_pins(self, param):
        """Sets the direction of the I/O pins and their values whenever a pin
        is configured as outbound.

        :param param: a byte containing the configuration of the I/O pins
        :type param: byte"""
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

    def set_resolution(self, resolution):
        """Sets the step resolution of the USD. The resolution could be either
        automatic or fixed.

        :param resolution: the USD resolution denominator. A resolution equal
            to `None` means the automatic change of resolution is enabled
        :type resolution: int from 0 to 7 (included), or `None`"""
        if resolution is None:
            self.auto_resolution = True
            self.resolution = self.resolutions.get(0)
        else:
            self.auto_resolution = False
            self.resolution = self.resolutions.get(resolution)

    def set_current_reduction(self, standby_mode, standby_delay_multiplier):
        """Sets the delay after which and in which way the USD current should
        be reduced.

        :param standby_mode: the desired standby mode
        :param standby_delay_multiplier: the desired standby delay multiplier
        :type standby_mode: int
        :type standby_delay_multiplier: int"""
        self.standby_mode = self.standby_modes.get(standby_mode)
        self.standby_delay_multiplier = standby_delay_multiplier

    def set_response_delay(self, multiplier):
        """Sets the response delay multiplier of the USD.

        :param multiplier: the desired delay multiplier, each unit corresponds
            to 4096 microseconds
        :type multiplier: int"""
        self.delay_multiplier = multiplier

    def set_delayed_execution(self, param):
        """Enables or disables the delayed execution of positioning commands.

        :param param: a byte containing information regarding the I/O lines and
            if the delayed positioning has to be enabled or disabled
        :type param: byte"""
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

    def set_absolute_position(self, position):
        """Receives an absolute position to which the USD will have to move.
        If the positioning strategy is set to immediate and the USD is not
        already moving, it will start moving towards the desired position.
        In case the USD is already moving and the positioning strategy is
        immediate, this command will fail, returning NAK. If the positioning
        strategy is set to delayed instead, the position will be enqueued and
        the USD will wait until it receives a TRIGGER event. It will then move
        to the first enqueued position.

        :param position: the absolute position to move to, expressed in 1/128
            of step
        :type position: int
        :return: a boolean indicating whether the parser has to answer with an
            ACK or a NAK (True or False respectively)
        :rtype: boolean"""
        cmd_position = self.reference_position + position
        if self.delayed_execution is True:
            self.position_queue.put((cmd_position, True))
            self.ready = True
        else:
            if self.running:
                # Driver is already moving, return False
                # so the parser can return a byte_nak
                return False
            self.cmd_position = cmd_position
        return True

    def set_relative_position(self, position):
        """Receives a relative position to which the USD will have to move in
        respect to its current position. If the positioning strategy is set to
        immediate and the USD is not already moving, it will start moving
        towards the resulting position. On the contrary, if the USD is already
        moving and the positioning strategy is immediate, this command will
        fail, returning NAK. If the positioning strategy is set to delayed, the
        resulting position will be enqueued and the USD will wait until it
        receives a TRIGGER event. It will then move to the first enqueued
        position.

        :param position: the position relative to the current one, expressed in
            1/128 of step
        :type position: int
        :return: a boolean indicating whether the parser has to answer with an
            ACK or a NAK (True or False respectively)
        :rtype: boolean"""
        cmd_position = self.current_position + position
        if self.delayed_execution is True:
            self.position_queue.put((cmd_position, False))
            self.ready = True
        else:
            if self.running:
                # Driver is already moving, return False
                # so the parser can return a byte_nak
                return False
            self.cmd_position = cmd_position
        return True

    def rotate(self, sign):
        """Starts moving the USD indefinitely. The direction of the movement
        corresponds is given by the sign parameter. It accounts for
        acceleration, minimum and maximum frequency.

        :param sign: the direction towards the USD will have to start moving
        :type sign: int
        :return: a boolean indicating whether the parser has to answer with an
            ACK or a NAK (True or False respectively)
        :rtype: boolean"""
        if self.running:
            # Driver is already moving, return False
            # so the parser can return a byte_nak
            return False
        else:
            self.cmd_position = sign * self.out_of_scale_position
            return True

    def set_velocity(self, velocity):
        """Starts moving the USD at a given frequency, bypassing the
        acceleration ramp. This is useful whenever the USD has to behave as a
        common servo driver. This command can be sent even when the USD is
        already moving. To stop the USD movement, use either a `stop` command
        or this same command, sending a zero as `velocity` parameter.

        :param velocity: the desired frequency to use for the movement
        :type velocity: int"""
        if not self.auto_resolution and (abs(velocity) < 10 and velocity != 0):
            return False
        elif velocity == 0:
            velocity = None
        # Start rotating with given velocity without an acceleration ramp
        self.cmd_position = None
        self.velocity = velocity
        return True

    def set_stop_io(self, param):
        """Sctivates the execution of a hardware stop whenever the I/O lines
        reach the desired (given) values.

        :param param: a byte containing information regarding the I/O values
            and if the hardware stop has to be enabled or not
        :type param: byte"""
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
        """Sets the logical levels of the I/O lines that have to be set
        whenever the USD reaches the desired position.

        :param param: a byte containing information regarding the I/O values to
            set whenever a commanded movement is completed
        :type param: byte"""
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
        """Sets the logical levels of the I/O lines that are used with the HOME
        function. The HOME function sets to 0 the actuator internal quota and
        stops its movement whenever the I/O lines get to a specific level.

        :param param: a byte containing information regarding the I/O values
            that triggers the HOME function of the USD.
        :type param: byte"""
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
        """Sets the working mode of the USD. For now, the only tweakable
        parameter is the baud rate of the serial communication.

        :param params: a string containing two bytes. The first one contains
            information regarding the desired baud rate for the serial
            communication, the second byte is currently unused.
        :type params: string containing two bytes"""
        binary_string = bin(params[0])[2:].zfill(8)

        # binary_string[0:7] is currently unused
        self.baud_rate = self.baud_rates.get(int(binary_string[7], 2))
        #  params[1] is currently unused

    def calc_position(self, elapsed):
        """Calculates the current position of the USD considering its current
        status and previously set parameters, along with the elapsed time since
        last position calculation.

        :param elapsed: the elapsed time in seconds since last position
            calculation
        :type elapsed: float"""
        velocity = None
        cmd_position = None
        if self.velocity:
            velocity = self.velocity
            self.running = True
        elif self.cmd_position is not None:
            cmd_position = self.cmd_position
            self.running = True
        else:
            self.running = False

        if self.running:
            self.current_percentage = 1.0
            self.full_current = True
            self.standby = False
            self.last_movement = time.time()
            if velocity:
                frequency = abs(velocity)
                sign0 = utils.sign(velocity)
            elif cmd_position is not None:
                # To be replaced with the slope frequency calculation
                frequency = self.max_frequency
                sign0 = utils.sign(cmd_position - self.current_position)

            steps_per_second = frequency * (128 / self.resolution)
            delta = sign0 * int(round(steps_per_second * elapsed))
            new_position = self.current_position + delta
            new_position = max(new_position, self.min_position)
            new_position = min(new_position, self.max_position)

            if cmd_position is not None:
                sign1 = utils.sign(cmd_position - new_position)
                if sign1 != sign0:
                    self.current_position = cmd_position
                    self.cmd_position = None
                    self.running = False
                else:
                    self.current_position = new_position
            else:
                self.current_position = new_position
        if not self.running and not self.standby:
            if self.last_movement:
                elapsed = time.time() - self.last_movement
                standby_delay = (
                    self.standby_delay_multiplier * self.standby_delay_step
                )
                if elapsed >= standby_delay:
                    self.current_percentage = 1.0 - self.standby_mode
                    if self.standby_mode > 0:
                        self.full_current = False
                    else:
                        self.full_current = True
                    self.last_movement = None
                    self.standby = True
