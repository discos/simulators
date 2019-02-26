from bisect import bisect_left
from multiprocessing import Array
from ctypes import c_char
from datetime import datetime, timedelta
import numpy as np
from scipy import interpolate
from simulators import utils


class PointingStatus(object):
    """This class handles the trajectory generation for the antenna axes.

    :param azimuth: a reference to the azimuth status object
    :param elevation: a reference to the elevation status object
    :param cable_wrap: a reference to the cable wrap status object
    """

    def __init__(self, azimuth, elevation, cable_wrap):
        self.azimuth = azimuth
        self.elevation = elevation
        self.cable_wrap = cable_wrap

        self.relative_times = []
        self.azimuth_positions = []
        self.elevation_positions = []

        self.start_time = None
        self.end_time = None

        self.time_source_offset = timedelta(0)
        self.time_offset = timedelta(0)

        self.status = Array(c_char, 129)
        self.confVersion = 0
        self.confOk = True
        self.posEncAz = 0
        self.pointOffsetAz = 0
        self.posCalibChartAz = 0
        self.posCorrTableAz_F_plst_El = 0
        self.posCorrTableAzOn = False
        self.encAzFault = False
        self.sectorSwitchAz = False
        self.posEncEl = 0
        self.pointOffsetEl = 0
        self.posCalibChartEl = 0
        self.posCorrTableEl_F_plst_Az = 0
        self.posCorrTableElOn = False
        self.encElFault = False
        self.posEncCw = 0
        self.posCalibChartCw = 0
        self.encCwFault = False
        self.timeSource = 1
        self.actTime = utils.mjd()
        self.actTimeOffset = 0
        self.clockOnline = True
        self.clockOK = True
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.actPtPos_Azimuth = 0
        self.actPtPos_Elevation = 0
        self.ptState = 0
        self.azimuth.ptState = 0
        self.elevation.ptState = 0

        # ptError
        self.Data_Overflow = False
        self.Time_Distance_Fault = False
        self.No_Data_Available = False

        self.actPtTimeOffset = 0
        self.ptInterpolMode = 0
        self.ptTrackingType = 1
        self.ptTrackingMode = 1
        self.ptActTableIndex = 0
        self.ptEndTableIndex = 0
        self.ptTableLength = 0
        self.parameter_command_counter = 0
        self.parameter_command = 0
        self.parameter_command_answer = 0

        # Counter relative to the load table command
        self.pt_command_id = None
        self.azimuth.pt_command_id = None
        self.elevation.pt_command_id = None

    def update_status(self):
        """This method updates some attributes (I.e. the ACU time and tracking
        status)."""
        curr_time = self.actual_time()
        self.year = curr_time.year
        self.month = curr_time.month
        self.day = curr_time.day
        self.hour = curr_time.hour
        self.minute = curr_time.minute
        self.second = curr_time.second
        self.actTime = utils.mjd(curr_time)

        self.posEncAz = self.azimuth.p_Ist
        self.pointOffsetAz = self.azimuth.p_Offset
        self.posEncEl = self.elevation.p_Ist
        self.pointOffsetEl = self.elevation.p_Offset

        if self.ptState not in [0, 4]:
            start_time = (
                self.start_time
                + timedelta(milliseconds=self.actPtTimeOffset)
            )
            elapsed = (curr_time - start_time).total_seconds() * 1000

            if self.ptState == 2:
                if curr_time < start_time:
                    if self.azimuth_positions:
                        self.azimuth.p_Bahn = int(
                            round(self.azimuth_positions[0] * 1000000)
                        )
                    if self.elevation_positions:
                        self.elevation.p_Bahn = int(
                            round(self.elevation_positions[0] * 1000000)
                        )
                else:
                    self.ptState = 3
                    self.azimuth.ptState = 3
                    self.elevation.ptState = 3

            if self.ptState == 3:
                pt_index = None

                pt_index = bisect_left(self.relative_times, elapsed)
                if pt_index == len(self.relative_times):
                    pt_index = None

                if pt_index is None:
                    self.ptState = 4
                    self.azimuth.ptState = 4
                    self.elevation.ptState = 4
                    self.azimuth.p_Bahn = int(
                        round(self.azimuth_positions[-1] * 1000000)
                    )
                    self.elevation.p_Bahn = int(
                        round(self.elevation_positions[-1] * 1000000)
                    )
                    self.ptTableLength = 0
                    self.ptActTableIndex = 0
                    self.ptEndTableIndex = 0
                    return
                else:
                    if self.az_tck:
                        self.azimuth.p_Bahn = int(round(
                            1000000 *
                            interpolate.splev(
                                elapsed,
                                self.az_tck
                            ).item(0)
                        ))
                        self.azimuth.v_Bahn = int(round(
                            1000000 *
                            interpolate.splev(
                                elapsed,
                                self.az_tck,
                                der=1
                            ).item(0)
                        ))
                        self.azimuth.a_Bahn = int(round(
                            1000000 *
                            interpolate.splev(
                                elapsed,
                                self.az_tck,
                                der=2
                            ).item(0)
                        ))
                    if self.el_tck:
                        self.elevation.p_Bahn = int(round(
                            1000000 *
                            interpolate.splev(
                                elapsed,
                                self.el_tck
                            ).item(0)
                        ))
                        self.elevation.v_Bahn = int(round(
                            1000000 *
                            interpolate.splev(
                                elapsed,
                                self.el_tck,
                                der=1
                            ).item(0)
                        ))
                        self.elevation.a_Bahn = int(round(
                            1000000 *
                            interpolate.splev(
                                elapsed,
                                self.el_tck,
                                der=2
                            ).item(0)
                        ))

                    self.ptActTableIndex = pt_index
                    self.relative_times = \
                        self.relative_times[pt_index:]
                    self.azimuth_positions = \
                        self.azimuth_positions[pt_index:]
                    self.elevation_positions = \
                        self.elevation_positions[pt_index:]
                    self.ptTableLength = len(self.relative_times)
                    self.ptEndTableIndex = max(self.ptTableLength - 1, 0)

            if self.azimuth_positions:
                self.azimuth.next_pos = int(round(
                    self.azimuth_positions[0] * 1000000
                ))
            if self.elevation_positions:
                self.elevation.next_pos = int(round(
                    self.elevation_positions[0] * 1000000
                ))

    def actual_time(self):
        """This method returns the actual ACU time, which is equal to the
        current UTC time plus an arbitrary offset."""
        return (
            datetime.utcnow()
            + self.time_source_offset
            + self.time_offset
        )

    # -------------------- Parameter Command --------------------

    def _parameter_command(self, command, _):
        """This method parses and executes the received parameter command.

        :param command: the received command.
        """
        cmd_cnt = utils.bytes_to_uint(command[4:8])
        parameter_id = utils.bytes_to_uint(command[8:10])
        parameter_1 = utils.bytes_to_real(command[10:18], 2)
        parameter_2 = utils.bytes_to_real(command[18:26], 2)

        self.parameter_command_counter = cmd_cnt
        self.parameter_command = parameter_id

        if parameter_id == 50:
            self._time_source(parameter_1, parameter_2)
        elif parameter_id == 51:
            self._time_offset(parameter_1, parameter_2)
        elif parameter_id == 60:
            self._program_track_time_correction(parameter_1)
        else:
            self.parameter_command_answer = 5

    def _time_source(self, parameter_1, parameter_2):
        """This method is called when a time source parameter command is
        received. It will set the ACU time offset according to the given time
        source.

        :param parameter_1: the desired time source
        :param parameter_2: the absolute time set via host computer (only for
            time source = 1)
        """
        parameter_1 = int(parameter_1)

        if parameter_1 not in [1, 2, 3]:
            self.parameter_command_answer = 5
            return
        elif parameter_1 == 1:
            self.time_source_offset = timedelta(0)
        elif parameter_1 == 2:
            pass
        elif parameter_1 == 3:
            self.time_source_offset = (
                utils.mjd_to_date(parameter_2)
                - datetime.utcnow()
            )

        self.timeSource = int(parameter_1)
        self.parameter_command_answer = 1

    def _time_offset(self, parameter_1, parameter_2):
        """This method is called when a time offset parameter command is
        received. It is used to add a time offset onto the actual servo control
        system time.

        :param parameter_1: offset time mode
        :param parameter_2: offset time [s]
        """
        parameter_1 = int(parameter_1)

        if not (1 <= parameter_1 <= 4) or abs(parameter_2) > 86400000:
            self.parameter_command_answer = 5
            return
        if parameter_1 == 1:
            # Servo System Time + 1 second
            offset = timedelta(seconds=1)
            self.time_offset += offset
            self.actTimeOffset += utils.day_percentage(timedelta(seconds=1))
        elif parameter_1 == 2:
            # Servo System Time - 1 second
            offset = timedelta(seconds=1)
            self.time_offset -= offset
            self.actTimeOffset -= utils.day_percentage(timedelta(seconds=1))
        elif parameter_1 == 3:
            # Set absolute offset
            self.time_offset = timedelta(seconds=parameter_2)
            self.actTimeOffset = utils.day_percentage(self.time_offset)
        elif parameter_1 == 4:
            # Set relative offset
            offset = timedelta(seconds=parameter_2)
            self.time_offset += offset
            self.actTimeOffset += utils.day_percentage(offset)

        self.parameter_command_answer = 1

    def _program_track_time_correction(self, time_offset):
        """This method is called when a program track time offset parameter
        command is received. It is used to chift the start time of program
        tracks.

        :param time_offset: the offset time added to start time of the program
            track
        """
        # time_offset = offset time [s]

        if abs(time_offset) > 86400000:
            self.parameter_command_answer = 5
            return

        self.actPtTimeOffset = int(round(time_offset * 1000))
        self.parameter_command_answer = 1

    # --------------- Program Track Parameter Command ---------------

    def _program_track_parameter_command(self, command, _):
        """This method parses the received program track parameter command.
        It interpolates the received tracking points and stores the generated
        trajectories in order for the axes to use them while tracking some
        celestial source.

        :param command: the received program track parameter command.
        """
        cmd_cnt = utils.bytes_to_uint(command[4:8])
        parameter_id = utils.bytes_to_uint(command[8:10])

        self.parameter_command_counter = cmd_cnt
        self.parameter_command = parameter_id

        if parameter_id != 61:
            self.parameter_command_answer = 0
            return

        interpolation_mode = utils.bytes_to_uint(command[10:12])

        if interpolation_mode != 4:
            self.parameter_command_answer = 5
            return

        tracking_mode = utils.bytes_to_uint(command[12:14])

        if tracking_mode != 1:
            self.parameter_command_answer = 5
            return

        load_mode = utils.bytes_to_uint(command[14:16])

        if load_mode not in [1, 2]:
            self.parameter_command_answer = 5
            return

        sequence_length = utils.bytes_to_uint(command[16:18])

        if sequence_length > 50:
            self.parameter_command_answer = 5
            return

        if load_mode == 1 and sequence_length < 5:
            self.parameter_command_answer = 5
            return

        if load_mode == 2 and not self.ptTableLength:
            self.parameter_command_answer = 5
            return

        start_time = utils.mjd_to_date(utils.bytes_to_real(command[18:26], 2))
        start_time += self.time_source_offset

        if load_mode == 2 and start_time != self.start_time:
            self.parameter_command_answer = 5
            return

        if load_mode == 1:
            self.relative_times = []
            self.azimuth_positions = []
            self.elevation_positions = []

        azimuth_max_rate = utils.bytes_to_real(command[26:34], 2)
        elevation_max_rate = utils.bytes_to_real(command[34:42], 2)

        byte_entries = command[42:]
        relative_times = self.relative_times
        azimuth_positions = self.azimuth_positions
        elevation_positions = self.elevation_positions

        if relative_times:
            expected_delta = relative_times[1] - relative_times[0]
            last_relative_time = relative_times[-1]
        else:
            expected_delta = None
            last_relative_time = 0

        for i in range(sequence_length):
            offset = i * 20

            relative_time = utils.bytes_to_int(
                byte_entries[offset:offset + 4]
            )

            if i == 0 and last_relative_time == 0 and relative_time != 0:
                self.parameter_command_answer = 5
                return

            if relative_time < last_relative_time:
                self.parameter_command_answer = 5
                return

            if not expected_delta and relative_times:
                expected_delta = relative_time - last_relative_time

            if expected_delta:
                if relative_time - last_relative_time != expected_delta:
                    self.parameter_command_answer = 5
                    return

            relative_times.append(relative_time)
            last_relative_time = relative_time

            azimuth_position = utils.bytes_to_real(
                byte_entries[offset + 4:offset + 12],
                2
            )
            azimuth_positions.append(azimuth_position)

            elevation_position = utils.bytes_to_real(
                byte_entries[offset + 12:offset + 20],
                2
            )
            elevation_positions.append(elevation_position)

        self.parameter_command_answer = 1

        self.relative_times = relative_times

        self.start_time = start_time
        self.end_time = (
            start_time
            + timedelta(milliseconds=relative_times[-1])
        )
        self.azimuth_max_rate = azimuth_max_rate
        self.elevation_max_rate = elevation_max_rate
        self.azimuth_positions = azimuth_positions
        self.elevation_positions = elevation_positions

        if load_mode == 1:
            self.pt_command_id = cmd_cnt
            self.azimuth.pt_command_id = cmd_cnt
            self.elevation.pt_command_id = cmd_cnt
            self.ptEndTableIndex = 0
            self.ptState = 2
            self.azimuth.ptState = 2
            self.elevation.ptState = 2
        elif self.ptState != 3:
            self.ptState = 2
            self.azimuth.ptState = 2
            self.elevation.ptState = 2

        self.ptInterpolMode = interpolation_mode
        self.ptTableLength = sequence_length
        self.ptEndTableIndex += sequence_length

        self.az_tck = interpolate.splrep(
            np.array(relative_times),
            np.array(azimuth_positions)
        )
        self.el_tck = interpolate.splrep(
            np.array(relative_times),
            np.array(elevation_positions)
        )

    @property
    def confVersion(self):
        return utils.bytes_to_real(self.status[0:8], precision=2)

    @confVersion.setter
    def confVersion(self, value):
        # REAL64, Version of the configuration file
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[0:8] = utils.real_to_bytes(value, precision=2)

    @property
    def confOk(self):
        return bool(utils.bytes_to_uint(self.status[8]))

    @confOk.setter
    def confOk(self, value):
        # BOOL
        # False: pointing not initialized and configured
        # True: initialization of pointing completed
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[8] = chr(int(value))

    @property
    def posEncAz(self):
        return utils.bytes_to_int(str(self.status[9:13]))

    @posEncAz.setter
    def posEncAz(self, value):
        # INT32, actual position of azimuth encoder [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[9:13] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def pointOffsetAz(self):
        return utils.bytes_to_int(str(self.status[13:17]))

    @pointOffsetAz.setter
    def pointOffsetAz(self, value):
        # INT32, actual pointing offset of the azimuth axis [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[13:17] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def posCalibChartAz(self):
        return utils.bytes_to_int(str(self.status[17:21]))

    @posCalibChartAz.setter
    def posCalibChartAz(self, value):
        # INT32, actual encoder position offset from the calibration chart
        # [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[17:21] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def posCorrTableAz_F_plst_El(self):
        return utils.bytes_to_int(str(self.status[21:25]))

    @posCorrTableAz_F_plst_El.setter
    def posCorrTableAz_F_plst_El(self, value):
        # INT32, actual encoder position offset from the user-defined
        # correction table [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[21:25] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def posCorrTableAzOn(self):
        return bool(utils.bytes_to_uint(self.status[25]))

    @posCorrTableAzOn.setter
    def posCorrTableAzOn(self, value):
        # BOOL
        # False: correction table is not used
        # True: pos. of the correction table is added onto the encoder pos.
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[25] = chr(int(value))

    @property
    def encAzFault(self):
        return bool(utils.bytes_to_uint(self.status[26]))

    @encAzFault.setter
    def encAzFault(self, value):
        # BOOL
        # False: position encoder azimuth ok
        # True: position encoder azimuth reports an error
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[26] = chr(int(value))

    @property
    def sectorSwitchAz(self):
        return bool(utils.bytes_to_uint(self.status[27]))

    @sectorSwitchAz.setter
    def sectorSwitchAz(self, value):
        # BOOL
        # False: lower sector active
        # True: upper sector active
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[27] = chr(int(value))

    @property
    def posEncEl(self):
        return utils.bytes_to_int(str(self.status[28:32]))

    @posEncEl.setter
    def posEncEl(self, value):
        # INT32, actual position of elevation encoder [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[28:32] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def pointOffsetEl(self):
        return utils.bytes_to_int(str(self.status[32:36]))

    @pointOffsetEl.setter
    def pointOffsetEl(self, value):
        # INT32, actual pointing offset of the elevation axis [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[32:36] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def posCalibChartEl(self):
        return utils.bytes_to_int(str(self.status[36:40]))

    @posCalibChartEl.setter
    def posCalibChartEl(self, value):
        # INT32, actual encoder position offset from the calibration chart
        # [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[36:40] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def posCorrTableEl_F_plst_Az(self):
        return utils.bytes_to_int(str(self.status[40:44]))

    @posCorrTableEl_F_plst_Az.setter
    def posCorrTableEl_F_plst_Az(self, value):
        # INT32, actual encoder position offset from the user-defined
        # correction table [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[40:44] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def posCorrTableElOn(self):
        return bool(utils.bytes_to_uint(self.status[44]))

    @posCorrTableElOn.setter
    def posCorrTableElOn(self, value):
        # BOOL
        # False: correction table is not used
        # True: pos. of the correction table is added onto the encoder pos.
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[44] = chr(int(value))

    @property
    def encElFault(self):
        return bool(utils.bytes_to_uint(self.status[45]))

    @encElFault.setter
    def encElFault(self, value):
        # BOOL
        # False: position encoder elevation ok
        # True: position encoder elevation reports an error
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[45] = chr(int(value))

    @property
    def posEncCw(self):
        return utils.bytes_to_int(str(self.status[46:50]))

    @posEncCw.setter
    def posEncCw(self, value):
        # INT32, actual position of azimuth cable wrap encoder [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[46:50] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def posCalibChartCw(self):
        return utils.bytes_to_int(str(self.status[50:54]))

    @posCalibChartCw.setter
    def posCalibChartCw(self, value):
        # INT32, actual encoder position offset from the calibration chart
        # [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[50:54] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def encCwFault(self):
        return bool(utils.bytes_to_uint(self.status[54]))

    @encCwFault.setter
    def encCwFault(self, value):
        # BOOL
        # False: position encoder cable wrap ok
        # True: position encoder cable wrap reports an error
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[54] = chr(int(value))

    @property
    def timeSource(self):
        return utils.bytes_to_uint(str(self.status[55:57]))

    @timeSource.setter
    def timeSource(self, value):
        # UINT16
        # 1: internal ACU time (computer quartz clock)
        # 2: clock (time read-outs of GPS clock)
        # 3: external time (time is set by command)
        if not isinstance(value, int) or value not in range(1, 4):
            raise ValueError('Provide an integer between 1 and 3!')
        self.status[55:57] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def actTime(self):
        return utils.bytes_to_real(self.status[57:65], precision=2)

    @actTime.setter
    def actTime(self, value):
        # REAL64, Actial time in format modified julian day
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[57:65] = utils.real_to_bytes(value, precision=2)

    @property
    def actTimeOffset(self):
        return utils.bytes_to_real(self.status[65:73], precision=2)

    @actTimeOffset.setter
    def actTimeOffset(self, value):
        # REAL64, Actial time offset in fraction of day
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[65:73] = utils.real_to_bytes(value, precision=2)

    @property
    def clockOnline(self):
        return bool(utils.bytes_to_uint(self.status[73]))

    @clockOnline.setter
    def clockOnline(self, value):
        # BOOL
        # False: GPS receiver doesn't send data
        # True: GPS receiver sends data
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[73] = chr(int(value))

    @property
    def clockOK(self):
        return bool(utils.bytes_to_uint(self.status[74]))

    @clockOK.setter
    def clockOK(self, value):
        # BOOL
        # False: GPS receiver sends error message
        # True: GPS receiver sends clock ok
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        self.status[74] = chr(int(value))

    @property
    def year(self):
        return utils.bytes_to_uint(str(self.status[75:77]))

    @year.setter
    def year(self, value):
        # UINT16
        if not isinstance(value, int) or value < 0:
            raise ValueError('Provide an unsigned integer!')
        self.status[75:77] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def month(self):
        return utils.bytes_to_uint(str(self.status[77:79]))

    @month.setter
    def month(self, value):
        # UINT16
        if not isinstance(value, int) or value < 0:
            raise ValueError('Provide an unsigned integer!')
        self.status[77:79] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def day(self):
        return utils.bytes_to_uint(str(self.status[79:81]))

    @day.setter
    def day(self, value):
        # UINT16
        if not isinstance(value, int) or value < 0:
            raise ValueError('Provide an unsigned integer!')
        self.status[79:81] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def hour(self):
        return utils.bytes_to_uint(str(self.status[81:83]))

    @hour.setter
    def hour(self, value):
        # UINT16
        if not isinstance(value, int) or value < 0:
            raise ValueError('Provide an unsigned integer!')
        self.status[81:83] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def minute(self):
        return utils.bytes_to_uint(str(self.status[83:85]))

    @minute.setter
    def minute(self, value):
        # UINT16
        if not isinstance(value, int) or value < 0:
            raise ValueError('Provide an unsigned integer!')
        self.status[83:85] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def second(self):
        return utils.bytes_to_uint(str(self.status[85:87]))

    @second.setter
    def second(self, value):
        # UINT16
        if not isinstance(value, int) or value < 0:
            raise ValueError('Provide an unsigned integer!')
        self.status[85:87] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def actPtPos_Azimuth(self):
        return utils.bytes_to_int(str(self.status[87:91]))

    @actPtPos_Azimuth.setter
    def actPtPos_Azimuth(self, value):
        # INT32, calculated azimuth position of the program track [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[87:91] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def actPtPos_Elevation(self):
        return utils.bytes_to_int(str(self.status[91:95]))

    @actPtPos_Elevation.setter
    def actPtPos_Elevation(self, value):
        # INT32, calculated elevation position of the program track [microdeg]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[91:95] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def ptState(self):
        return utils.bytes_to_uint(str(self.status[95:97]))

    @ptState.setter
    def ptState(self, value):
        # UINT16, status of the program track
        # 0: off
        # 1: fault
        # 2: enabled
        # 3: running
        # 4: completed
        if not isinstance(value, int) or value not in range(5):
            raise ValueError('Provide an integer between 0 and 4!')
        self.status[95:97] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def ptError(self):
        return utils.bytes_to_binary(str(self.status[97:99]))[::-1]

    @property
    def Data_Overflow(self):
        return bool(int(str(self.ptError)[0]))

    @Data_Overflow.setter
    def Data_Overflow(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        ptError = bytearray(self.ptError)
        ptError[0] = str(int(value))
        self.status[97:99] = utils.binary_to_bytes(str(ptError)[::-1])

    @property
    def Time_Distance_Fault(self):
        return bool(int(str(self.ptError)[1]))

    @Time_Distance_Fault.setter
    def Time_Distance_Fault(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        ptError = bytearray(self.ptError)
        ptError[1] = str(int(value))
        self.status[97:99] = utils.binary_to_bytes(str(ptError)[::-1])

    @property
    def No_Data_Available(self):
        return bool(int(str(self.ptError)[2]))

    @No_Data_Available.setter
    def No_Data_Available(self, value):
        if not isinstance(value, bool):
            raise ValueError('Provide a boolean!')
        ptError = bytearray(self.ptError)
        ptError[2] = str(int(value))
        self.status[97:99] = utils.binary_to_bytes(str(ptError)[::-1])

    @property
    def actPtTimeOffset(self):
        return utils.bytes_to_int(str(self.status[99:103]))

    @actPtTimeOffset.setter
    def actPtTimeOffset(self, value):
        # INT32, actual time offset for program tracks [milliseconds]
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[99:103] = utils.int_to_bytes(value, n_bytes=4)

    @property
    def ptInterpolMode(self):
        return utils.bytes_to_uint(str(self.status[103:105]))

    @ptInterpolMode.setter
    def ptInterpolMode(self, value):
        # UINT16, actual selected interpolation mode
        # 0: no interpolation mode selected
        # 4: spline
        if not isinstance(value, int) or value not in [0, 4]:
            raise ValueError(
                'You can provide only an integer equal to 0 or 4!'
            )
        self.status[103:105] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def ptTrackingType(self):
        return utils.bytes_to_uint(str(self.status[105:107]))

    @ptTrackingType.setter
    def ptTrackingType(self, value):
        # UINT16, actual type of tracking
        # 1: program track
        if not isinstance(value, int) or value != 1:
            raise ValueError('You can provide only an integer equal to 1!')
        self.status[105:107] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def ptTrackingMode(self):
        return utils.bytes_to_uint(str(self.status[107:109]))

    @ptTrackingMode.setter
    def ptTrackingMode(self, value):
        # UINT16, actual type of program track
        # 1: program track values are azimuth/elevation
        if not isinstance(value, int) or value != 1:
            raise ValueError('You can provide only an integer equal to 1!')
        self.status[107:109] = utils.uint_to_bytes(value, n_bytes=2)

    @property
    def ptActTableIndex(self):
        return utils.bytes_to_uint(str(self.status[109:113]))

    @ptActTableIndex.setter
    def ptActTableIndex(self, value):
        # UINT32, actual table entry of the program track table
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[109:113] = utils.uint_to_bytes(value, n_bytes=4)

    @property
    def ptEndTableIndex(self):
        return utils.bytes_to_uint(str(self.status[113:117]))

    @ptEndTableIndex.setter
    def ptEndTableIndex(self, value):
        # UINT32, last table entry of the program track table
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[113:117] = utils.uint_to_bytes(value, n_bytes=4)

    @property
    def ptTableLength(self):
        return utils.bytes_to_uint(str(self.status[117:121]))

    @ptTableLength.setter
    def ptTableLength(self, value):
        # UINT32, overall length of the program track table
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        self.status[117:121] = utils.uint_to_bytes(value, n_bytes=4)

    @property
    def parameter_command_status(self):
        return self.status[121:129]

    @property
    def parameter_command_counter(self):
        return utils.bytes_to_uint(str(self.parameter_command_status[0:4]))

    @parameter_command_counter.setter
    def parameter_command_counter(self, value):
        # UINT32, command serial number
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        parameter_command_status = bytearray(self.parameter_command_status)
        parameter_command_status[0:4] = utils.uint_to_bytes(value, n_bytes=4)
        self.status[121:129] = str(parameter_command_status)

    @property
    def parameter_command(self):
        return utils.bytes_to_uint(str(self.parameter_command_status[4:6]))

    @parameter_command.setter
    def parameter_command(self, value):
        # UINT16, parameter command
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        parameter_command_status = bytearray(self.parameter_command_status)
        parameter_command_status[4:6] = utils.uint_to_bytes(value, n_bytes=2)
        self.status[121:129] = str(parameter_command_status)

    @property
    def parameter_command_answer(self):
        return utils.bytes_to_uint(str(self.parameter_command_status[6:8]))

    @parameter_command_answer.setter
    def parameter_command_answer(self, value):
        # UINT16, parameter command answer
        if not isinstance(value, int):
            raise ValueError('Provide an integer number!')
        parameter_command_status = bytearray(self.parameter_command_status)
        parameter_command_status[6:8] = utils.uint_to_bytes(value, n_bytes=2)
        self.status[121:129] = str(parameter_command_status)
