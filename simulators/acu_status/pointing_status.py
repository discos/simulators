from simulators.acu_status import parameter_command_status as pcs
from simulators import utils


class PointingStatus(object):

    # confVersion, REAL64, version of the configuration file
    confVersion = 0

    # confOk, BOOL
    # 0: pointing not initialized and configured, 1: initialized and configured
    confOk = 0

    # posEncAz, INT32, actual position of azimuth encoder [microdeg]
    posEncAz = 0

    # pointOffsetAz, INT32
    # actual pointing offset of the azimuth axis [microdeg]
    pointOffsetAz = 0

    # posCalibChartAz, INT32
    # actual encoder position offset from the calibration chart [microdeg]
    posCalibChartAz = 0

    # posCorrTableAz_F_plst_El, INT32
    # actual encoder position offset from
    # the user defined correction table [microdeg]
    posCorrTableAz_F_plst_El = 0

    # posCorrTableAzOn, BOOL
    # 0: correction table is not used
    # 1: position of the correction table is added onto the encoder position
    posCorrTableAzOn = 0

    # encAzFault, BOOL
    # 0: position encoder azimuth ok
    # 1: position encoder azimuth reports an error
    encAzFault = 0

    # sectorSwitchAz, BOOL, 0: lower sector active, 1: upper sector active
    sectorSwitchAz = 0

    # posEncEl, INT32, actual position of elevation encoder [microdeg]
    posEncEl = 0

    # pointOffsetEl, INT32
    # actual pointing offset of the elevation axis [microdeg]
    pointOffsetEl = 0

    # posCalibChartEl, INT32
    # actual encoder position offset from the calibration chart [microdeg]
    posCalibChartEl = 0

    # posCorrTableEl_F_plst_Az, INT32
    # actual encoder position offset from the
    # user defined correction table [microdeg]
    posCorrTableEl_F_plst_Az = 0

    # posCorrTableElOn, BOOL
    # 0: correction table is not used
    # 1: position of the correction table is added onto the encoder position
    posCorrTableElOn = 0

    # encElFault, UINT8
    # 0: position encoder elevation ok
    # 1: position encoder elevation reports an error
    encElFault = 0

    # posEncCw, INT32
    # actual position of azimuth cable wrap encoder [microdeg]
    posEncCw = 0

    # posCalibChartCw, INT32
    # actual encoder position offset from the calibration chart
    posCalibChartCw = 0

    # encCwFault, UINT8
    # 0: position encoder cable wrap ok
    # 1: position encoder cable wrap reports an error
    encCwFault = 0

    # timeSource, UINT16
    # 1: internal ACU time (computer quartz clock)
    # 2: clock (time read-outs of GPS clock)
    # 3: ecternal time (Time is set by command)
    timeSource = 0

    # actTime, REAL64, actual time in format modified julian day
    actTime = 0

    # actTimeOffset, REAL64, actual time offset in fraction of day
    actTimeOffset = 0

    # clockOnLine, UINT8
    # 0: GPS receiver doesn't send data
    # 1: GPS receivers send data
    clockOnline = 0

    # clockOK, UINT8
    # 0: GPS receiver sends error message
    # 1: GPS receivers sends clock ok
    clockOK = 0

    # Actual time
    year = 0  # UINT16
    month = 0  # UINT16
    day = 0  # UINT16
    hour = 0  # UINT16
    minute = 0  # UINT16
    second = 0  # UINT16

    # actPtPos_Azimuth, INT32
    # calculated azimuth position of the program track [microdeg]
    actPtPos_Azimuth = 0

    # actPtPos_Elevation, INT32
    # calculated elevation position of the program track [microdeg]
    actPtPos_Elevation = 0

    # ptState, UINT16, status of the program track
    # 0: off
    # 1: fault
    # 2: enabled
    # 3: running
    # 4: completed
    ptState = 0

    # ptError, WORD, in bit mode coded program track error
    Data_Overflow = 0
    Time_Distance_Fault = 0
    No_Data_Available = 0
    # bits 3:5 = 0, reserved
    # bits 6:15 = 0, not used

    def _pointing_error(self):
        binary_string = (
            str(self.Data_Overflow)
            + str(self.Time_Distance_Fault)
            + str(self.No_Data_Available)
            + '0' * 3  # reserved
            + '0' * 10  # not used
        )
        return utils.binary_to_bytes(binary_string)

    # actTimeOffset, INT32, actual time offset [milliseconds] for program track
    actTimeOffset = 0

    # ptInterpolMode, UINT16, actual selected interpolation mode
    # 0: no interpolation mode selected
    # 4: spline
    ptInterpolMode = 0

    # ptTrackingType, UINT16, actual type of tracking
    # 1: program track
    ptTrackingType = 0  # UINT16

    # ptTrackingMode, UINT16, actual type of program track
    # 1: program track values are azimuth/elevation
    ptTrackingMode = 0

    # ptActTableIndex, UINT32, actual table entry of the program track table
    ptActTableIndex = 0

    # ptEndTableIndex, UINT32, last table entry of the program track table
    ptEndTableIndex = 0

    # ptTableLength, UINT32, overall length of the program track table
    ptTableLength = 0

    # parameter_command_status, refer to ParameterCommandStatus class
    parameter_command_status = pcs.ParameterCommandStatus()

    def get_status(self):
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
