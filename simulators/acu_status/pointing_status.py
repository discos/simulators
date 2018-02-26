import time
from datetime import datetime, timedelta
from threading import Thread
import numpy as np
from scipy import interpolate
from simulators.acu_status.command_status import (
    ParameterCommandStatus)
from simulators import utils


class PointingStatus(object):

    def __init__(self, azimuth, elevation, cable_wrap):
        self.azimuth = azimuth
        self.elevation = elevation
        self.cable_wrap = cable_wrap

        self.azimuth.pointing = self
        self.elevation.pointing = self
        self.cable_wrap.pointing = self

        self.relative_times = []
        self.azimuth_positions = []
        self.elevation_positions = []

        self.start_time = None
        self.end_time = None

        # confVersion, REAL64, version of the configuration file
        self.confVersion = 0

        # confOk, BOOL
        # 0: pointing not initialized and configured
        # 1: pointing initialized and configured
        self.confOk = 1

        # posEncAz, INT32, actual position of azimuth encoder [microdeg]
        self.posEncAz = 0

        # pointOffsetAz, INT32
        # actual pointing offset of the azimuth axis [microdeg]
        self.pointOffsetAz = 0

        # posCalibChartAz, INT32
        # actual encoder position offset from the calibration chart [microdeg]
        self.posCalibChartAz = 0

        # posCorrTableAz_F_plst_El, INT32
        # actual encoder position offset from
        # the user defined correction table [microdeg]
        self.posCorrTableAz_F_plst_El = 0

        # posCorrTableAzOn, BOOL
        # 0: correction table is not used
        # 1: pos. of the correction table is added onto the encoder pos.
        self.posCorrTableAzOn = 0

        # encAzFault, BOOL
        # 0: position encoder azimuth ok
        # 1: position encoder azimuth reports an error
        self.encAzFault = 0

        # sectorSwitchAz, BOOL, 0: lower sector active, 1: upper sector active
        self.sectorSwitchAz = 0

        # posEncEl, INT32, actual position of elevation encoder [microdeg]
        self.posEncEl = 0

        # pointOffsetEl, INT32
        # actual pointing offset of the elevation axis [microdeg]
        self.pointOffsetEl = 0

        # posCalibChartEl, INT32
        # actual encoder position offset from the calibration chart [microdeg]
        self.posCalibChartEl = 0

        # posCorrTableEl_F_plst_Az, INT32
        # actual encoder position offset from the
        # user defined correction table [microdeg]
        self.posCorrTableEl_F_plst_Az = 0

        # posCorrTableElOn, BOOL
        # 0: correction table is not used
        # 1: pos. of the correction table is added onto the encoder pos.
        self.posCorrTableElOn = 0

        # encElFault, UINT8
        # 0: position encoder elevation ok
        # 1: position encoder elevation reports an error
        self.encElFault = 0

        # posEncCw, INT32
        # actual position of azimuth cable wrap encoder [microdeg]
        self.posEncCw = 0

        # posCalibChartCw, INT32
        # actual encoder position offset from the calibration chart
        self.posCalibChartCw = 0

        # encCwFault, UINT8
        # 0: position encoder cable wrap ok
        # 1: position encoder cable wrap reports an error
        self.encCwFault = 0

        # timeSource, UINT16
        # 1: internal ACU time (computer quartz clock)
        # 2: clock (time read-outs of GPS clock)
        # 3: external time (Time is set by command)
        self.timeSource = 1

        # actTime, REAL64, actual time in format modified julian day
        self.actTime = 0

        self.time_offset = timedelta(0)

        # actTimeOffset, REAL64, actual time offset in fraction of day
        self.actTimeOffset = 0

        # clockOnLine, UINT8
        # 0: GPS receiver doesn't send data
        # 1: GPS receivers send data
        self.clockOnline = 1

        # clockOK, UINT8
        # 0: GPS receiver sends error message
        # 1: GPS receivers sends clock ok
        self.clockOK = 1

        # Actual time
        self.year = 0  # UINT16
        self.month = 0  # UINT16
        self.day = 0  # UINT16
        self.hour = 0  # UINT16
        self.minute = 0  # UINT16
        self.second = 0  # UINT16

        # actPtPos_Azimuth, INT32
        # calculated azimuth position of the program track [microdeg]
        self.actPtPos_Azimuth = 0

        # actPtPos_Elevation, INT32
        # calculated elevation position of the program track [microdeg]
        self.actPtPos_Elevation = 0

        # ptState, UINT16, status of the program track
        # 0: off
        # 1: fault
        # 2: enabled
        # 3: running
        # 4: completed
        self.ptState = 0

        # ptError, WORD, in bit mode coded program track error
        self.Data_Overflow = 0
        self.Time_Distance_Fault = 0
        self.No_Data_Available = 0
        # bits 3:5 = 0, reserved
        # bits 6:15 = 0, not used

        # actPtTimeOffset, INT32
        # actual time offset [milliseconds] for program track
        self.actPtTimeOffset = 0

        # ptInterpolMode, UINT16, actual selected interpolation mode
        # 0: no interpolation mode selected
        # 4: spline
        self.ptInterpolMode = 0

        # ptTrackingType, UINT16, actual type of tracking
        # 1: program track
        self.ptTrackingType = 1  # UINT16

        # ptTrackingMode, UINT16, actual type of program track
        # 1: program track values are azimuth/elevation
        self.ptTrackingMode = 1

        # ptActTableIndex, UINT32
        # actual table entry of the program track table
        self.ptActTableIndex = 0

        # ptEndTableIndex, UINT32, last table entry of the program track table
        self.ptEndTableIndex = 0

        # ptTableLength, UINT32, overall length of the program track table
        self.ptTableLength = 0

        # parameter_command_status, refer to ParameterCommandStatus class
        self.pcs = ParameterCommandStatus()

        self.update_thread = Thread(target=self._update_thread)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _pointing_error(self):
        binary_string = (
            str(self.Data_Overflow)
            + str(self.Time_Distance_Fault)
            + str(self.No_Data_Available)
            + '0' * 3  # reserved
            + '0' * 10  # not used
        )
        return utils.binary_to_bytes(binary_string)

    def get_status(self):
        curr_time = self.actual_time()
        self.year = curr_time.year
        self.month = curr_time.month
        self.day = curr_time.day
        self.hour = curr_time.hour
        self.minute = curr_time.minute
        self.second = curr_time.second
        self.actTime = utils.mjd(curr_time)

        response = (
            utils.real_to_bytes(self.confVersion, 2)
            + chr(self.confOk)
            + utils.int_to_bytes(self.posEncAz)
            + utils.int_to_bytes(self.pointOffsetAz)
            + utils.int_to_bytes(self.posCalibChartAz)
            + utils.int_to_bytes(self.posCorrTableAz_F_plst_El)
            + chr(self.posCorrTableAzOn)
            + chr(self.encAzFault)
            + chr(self.sectorSwitchAz)
            + utils.int_to_bytes(self.posEncEl)
            + utils.int_to_bytes(self.pointOffsetEl)
            + utils.int_to_bytes(self.posCalibChartEl)
            + utils.int_to_bytes(self.posCorrTableEl_F_plst_Az)
            + chr(self.posCorrTableElOn)
            + utils.uint_to_bytes(self.encElFault, 1)
            + utils.int_to_bytes(self.posEncCw)
            + utils.int_to_bytes(self.posCalibChartCw)
            + utils.uint_to_bytes(self.encCwFault, 1)
            + utils.uint_to_bytes(self.timeSource, 2)
            + utils.real_to_bytes(self.actTime, 2)
            + utils.real_to_bytes(self.actTimeOffset, 2)
            + utils.uint_to_bytes(self.clockOnline, 1)
            + utils.uint_to_bytes(self.clockOK, 1)
            + utils.uint_to_bytes(self.year, 2)
            + utils.uint_to_bytes(self.month, 2)
            + utils.uint_to_bytes(self.day, 2)
            + utils.uint_to_bytes(self.hour, 2)
            + utils.uint_to_bytes(self.minute, 2)
            + utils.uint_to_bytes(self.second, 2)
            + utils.int_to_bytes(self.actPtPos_Azimuth)
            + utils.int_to_bytes(self.actPtPos_Elevation)
            + utils.uint_to_bytes(self.ptState, 2)
            + self._pointing_error()
            + utils.int_to_bytes(self.actPtTimeOffset)
            + utils.uint_to_bytes(self.ptInterpolMode, 2)
            + utils.uint_to_bytes(self.ptTrackingType, 2)
            + utils.uint_to_bytes(self.ptTrackingMode, 2)
            + utils.uint_to_bytes(self.ptActTableIndex)
            + utils.uint_to_bytes(self.ptEndTableIndex)
            + utils.uint_to_bytes(self.ptTableLength)
            + self.pcs.get_status()
        )

        self.pcs = ParameterCommandStatus()
        return response

    def _update_thread(self):
        while True:
            if self.ptState == 2 and self.actual_time() >= self.start_time:
                self.ptState = 3
            elif self.ptState == 3:
                current_pt_time = self.actual_time() - self.start_time
                current_pt_time = current_pt_time.total_seconds() * 1000

                pt_index = None

                for index in range(len(self.relative_times)):
                    if current_pt_time < self.relative_times[index]:
                        pt_index = index
                        break

                if pt_index:
                    self.ptActTableIndex = pt_index
                else:
                    self.ptActTableIndex = len(self.relative_times)
                    self.ptState = 4

            time.sleep(0.001)

    def actual_time(self):
        return datetime.utcnow() + self.time_offset

    # -------------------- Parameter Command --------------------

    def parameter_command(self, command):
        cmd_cnt = utils.bytes_to_uint(command[4:8])
        parameter_id = utils.bytes_to_uint(command[8:10])
        parameter_1 = utils.bytes_to_real(command[10:18], 2)
        parameter_2 = utils.bytes_to_real(command[18:26], 2)

        self.pcs.counter = cmd_cnt
        self.pcs.command = parameter_id

        if parameter_id == 50:
            self._time_source(parameter_1, parameter_2)
        elif parameter_id == 51:
            self._time_offset(parameter_1, parameter_2)
        elif parameter_id == 60:
            self._program_track_time_correction(parameter_1)
        else:
            self.pcs.answer = 5

    def _time_source(self, parameter_1, parameter_2):
        parameter_1 = int(parameter_1)

        if parameter_1 not in [1, 2, 3]:
            self.pcs.answer = 5
            return
        elif parameter_1 == 3:
            self.time_offset = (
                utils.mjd_to_date(parameter_2)
                - datetime.utcnow()
            )

        self.timeSource = parameter_1
        self.pcs.answer = 1

    def _time_offset(self, parameter_1, parameter_2):
        parameter_1 = int(parameter_1)

        if parameter_1 == 1:
            # Servo System Time + 1 second
            pass
        elif parameter_1 == 2:
            # Servo System Time - 1 second
            pass
        elif parameter_1 == 3:
            # Set absolute offset
            pass
        elif parameter_1 == 4:
            # Set relative offset
            pass
        else:
            self.pcs.answer = 5

        self.pcs.answer = 1

    def _program_track_time_correction(self, parameter_1):
        # parameter_1 = offset time mode
        self.pcs.answer = 1

    # --------------- Program Track Parameter Command ---------------

    def program_track_parameter_command(self, command):
        cmd_cnt = utils.bytes_to_uint(command[4:8])
        parameter_id = utils.bytes_to_uint(command[8:10])

        self.pcs.counter = cmd_cnt
        self.pcs.command = parameter_id

        if parameter_id != 61:
            self.pcs.answer = 0
            return

        interpolation_mode = utils.bytes_to_uint(command[10:12])

        if interpolation_mode != 4:
            self.pcs.answer = 5
            return

        tracking_mode = utils.bytes_to_uint(command[12:14])

        if tracking_mode != 1:
            self.pcs.answer = 5
            return

        load_mode = utils.bytes_to_uint(command[14:16])

        if load_mode not in [1, 2]:
            self.pcs.answer = 5
            return

        sequence_length = utils.bytes_to_uint(command[16:18])

        if sequence_length > 50:
            self.pcs.answer = 5
            return

        if load_mode == 1 and sequence_length < 5:
            self.pcs.answer = 5
            return

        if load_mode == 2 and not self.relative_times:
            self.pcs.answer = 5
            return

        start_time = utils.mjd_to_date(utils.bytes_to_real(command[18:26], 2))
        start_time += self.time_offset

        if load_mode == 2 and start_time != self.start_time:
            self.pcs.answer = 5
            return

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

        if len(byte_entries) != sequence_length * 20:
            self.pcs.answer = 5
            return

        for i in range(sequence_length):
            offset = i * 20

            relative_time = utils.bytes_to_int(
                byte_entries[offset:offset + 4]
            )

            if i == 0 and last_relative_time == 0 and relative_time != 0:
                self.pcs.answer = 5
                return

            if relative_time < last_relative_time:
                self.pcs.answer = 5
                return

            if not expected_delta and relative_times:
                expected_delta = relative_time - last_relative_time

            if expected_delta:
                if relative_time - last_relative_time != expected_delta:
                    self.pcs.answer = 5
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

        if self.ptState != 3:
            self.ptState = 2
        self.ptInterpolMode = interpolation_mode
        self.ptTableLength = len(relative_times)
        self.ptEndTableIndex = self.ptTableLength - 1

        self.az_tck = interpolate.splrep(
            np.array(relative_times),
            np.array(azimuth_positions)
        )
        self.el_tck = interpolate.splrep(
            np.array(relative_times),
            np.array(elevation_positions)
        )

        self.pcs.answer = 1

    def get_starting_pos(self, subsystem):
        if subsystem is self.azimuth:
            return self.azimuth_positions[0]
        elif subsystem is self.elevation:
            return self.elevation_positions[0]
        else:
            return None

    def get_traj_values(self, subsystem):
        if subsystem is self.azimuth:
            trajectory = self.az_tck
        elif subsystem is self.elevation:
            trajectory = self.el_tck
        else:
            return None

        if not self.start_time:
            return None

        elapsed = (
            (self.actual_time() - self.start_time).total_seconds()
            / 1000
        )

        pos = interpolate.splev(elapsed, trajectory).item(0) * 1000000
        vel = interpolate.splev(elapsed, trajectory, der=1).item(0) * 1000000
        acc = interpolate.splev(elapsed, trajectory, der=2).item(0) * 1000000
        return int(round(pos)), int(round(vel)), int(round(acc))
