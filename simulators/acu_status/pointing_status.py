from datetime import datetime
from simulators.acu_status import parameter_command_status as pcs
from simulators import utils


class PointingStatus(object):
    def __init__(self, azimuth, elevation):
        self.azimuth = azimuth
        self.elevation = elevation
        self.program_track_queue = []

        # confVersion, REAL64, version of the configuration file
        self.confVersion = 0

        # confOk, BOOL
        # 0: pointing not initialized and configured
        # 1: pointing initialized and configured
        self.confOk = 0

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
        self.timeSource = 0

        # actTime, REAL64, actual time in format modified julian day
        self.actTime = 0

        # actTimeOffset, REAL64, actual time offset in fraction of day
        self.actTimeOffset = 0

        # clockOnLine, UINT8
        # 0: GPS receiver doesn't send data
        # 1: GPS receivers send data
        self.clockOnline = 0

        # clockOK, UINT8
        # 0: GPS receiver sends error message
        # 1: GPS receivers sends clock ok
        self.clockOK = 0

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

        # actTimeOffset, INT32
        # actual time offset [milliseconds] for program track
        self.actTimeOffset = 0

        # ptInterpolMode, UINT16, actual selected interpolation mode
        # 0: no interpolation mode selected
        # 4: spline
        self.ptInterpolMode = 0

        # ptTrackingType, UINT16, actual type of tracking
        # 1: program track
        self.ptTrackingType = 0  # UINT16

        # ptTrackingMode, UINT16, actual type of program track
        # 1: program track values are azimuth/elevation
        self.ptTrackingMode = 0

        # ptActTableIndex, UINT32
        # actual table entry of the program track table
        self.ptActTableIndex = 0

        # ptEndTableIndex, UINT32, last table entry of the program track table
        self.ptEndTableIndex = 0

        # ptTableLength, UINT32, overall length of the program track table
        self.ptTableLength = 0

        # parameter_command_status, refer to ParameterCommandStatus class
        self.parameter_command_status = pcs.ParameterCommandStatus()

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
        time = datetime.utcnow()
        self.year = time.year
        self.month = time.month
        self.day = time.day
        self.hour = time.hour
        self.minute = time.minute
        self.second = time.second
        self.actTime = utils.mjd(time)
        return (utils.real_to_bytes(self.confVersion, 2)
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
                + utils.int_to_bytes(self.actTimeOffset)
                + utils.uint_to_bytes(self.ptInterpolMode, 2)
                + utils.uint_to_bytes(self.ptTrackingType, 2)
                + utils.uint_to_bytes(self.ptTrackingMode, 2)
                + utils.uint_to_bytes(self.ptActTableIndex)
                + utils.uint_to_bytes(self.ptEndTableIndex)
                + utils.uint_to_bytes(self.ptTableLength)
                + self.parameter_command_status.get_status())

    def parameter_command(self, command):
        pass

    def program_track_parameter_command(self, command):
        parameter_id = utils.bytes_to_uint(command[8:10])

        if parameter_id != 61:
            raise ValueError('Unknown parameter_id %d.' % parameter_id)

        interpolation_mode = utils.bytes_to_uint(command[10:12])

        if interpolation_mode != 4:
            raise ValueError(
                'Unknown interpolation_mode %d.'
                % interpolation_mode
            )

        tracking_mode = utils.bytes_to_uint(command[12:14])

        if tracking_mode != 1:
            raise ValueError('Unknown tracking_mode %d.' % tracking_mode)

        load_mode = utils.bytes_to_uint(command[14:16])

        if load_mode not in [1, 2]:
            raise ValueError('Unknown load_mode %d.' % load_mode)

        sequence_length = utils.bytes_to_uint(command[16:18])

        if sequence_length > 50:
            raise ValueError('Sequence too long.')

        if load_mode == 1 and sequence_length < 5:
            raise ValueError('Sequence too short.')

        start_time = utils.mjd_to_date(utils.bytes_to_real(command[18:26], 2))
        azimuth_max_rate = utils.bytes_to_real(command[26:34], 2)
        elevation_max_rate = utils.bytes_to_real(command[34:42], 2)

        byte_entries = command[42:]
        azimuth_entries = []
        elevation_entries = []

        if len(byte_entries) != sequence_length * 20:
            raise ValueError('Malformed sequence.')

        for i in range(sequence_length):
            offset = i * 20

            relative_time = utils.bytes_to_int(
                byte_entries[offset:offset + 4]
            )
            azimuth_position = utils.bytes_to_real(
                byte_entries[offset + 4:offset + 12],
                2
            )
            elevation_position = utils.bytes_to_real(
                byte_entries[offset + 12:offset + 20],
                2
            )

            azimuth_entries.append((relative_time, azimuth_position))
            elevation_entries.append((relative_time, elevation_position))

        if load_mode == 1:
            self.azimuth.load_program_track_table(
                start_time,
                azimuth_max_rate,
                azimuth_entries
            )
            self.elevation.load_program_track_table(
                start_time,
                elevation_max_rate,
                elevation_entries
            )
        else:
            self.azimuth.add_program_track_entries(
                start_time,
                azimuth_max_rate,
                azimuth_entries
            )
            self.elevation.add_program_track_entries(
                start_time,
                elevation_max_rate,
                elevation_entries
            )
