from datetime import datetime, timedelta
from simulators import utils
from simulators.receiver import DEFINITIONS as DEF


class Slave(object):

    def __init__(self, address):
        self.address = address
        self.port_settings = {}
        self.frame_size = chr(126)
        self.time_offset = timedelta(0)
        self._reset()

    def _reset(self):
        self.last_cmd_date = None
        self.last_cmd = '\x00'
        self.last_cmd_id = '\x00'
        self.last_cmd_answer = '\x00'

    @staticmethod
    def _datetime_to_time(date):
        answer = chr(int(str(date.year)[:2]))
        answer += chr(int(str(date.year)[2:]))
        answer += chr(int(str(date.month)))
        answer += chr(int(str(date.day)))
        answer += chr(int(str(date.hour)))
        answer += chr(int(str(date.minute)))
        answer += chr(int(str(date.second)))
        answer += chr(int(str(int(round(date.microsecond / 10000.)))))
        return answer

    def _set_last_cmd(self, cmd, cmd_id, answer):
        self.last_cmd = cmd
        self.last_cmd_id = cmd_id
        self.last_cmd_answer = answer
        self.last_cmd_date = datetime.utcnow()

    def inquiry(self):
        data = ''
        data += self.last_cmd
        data += self.last_cmd_id
        data += self.last_cmd_answer

        if self.last_cmd_date is None:
            data += '\x00' * 8
        else:
            data += self._datetime_to_time(
                self.last_cmd_date - self.time_offset
            )

        return [DEF.CMD_ACK, data]

    def reset(self):
        self._reset()
        return DEF.CMD_ACK

    def version(self, cmd_id, extended):
        self._set_last_cmd(
            DEF.CMD_EXT_VERSION if extended else DEF.CMD_ABBR_VERSION,
            cmd_id,
            DEF.CMD_ACK
        )
        return [DEF.CMD_ACK, DEF.VERSION]

    def save(self, cmd_id, extended):
        # The configuration should be saved but we ignore this feature for now
        self._set_last_cmd(
            DEF.CMD_EXT_SAVE if extended else DEF.CMD_ABBR_SAVE,
            cmd_id,
            DEF.CMD_ACK
        )
        return DEF.CMD_ACK

    def restore(self, cmd_id, extended):
        # Should read the saved configuration and perform a reset
        # Since we don't save any configuration with the same command
        # we leave the configuration as it is, we answer with an ACK
        self._set_last_cmd(
            DEF.CMD_EXT_RESTORE if extended else DEF.CMD_ABBR_RESTORE,
            cmd_id,
            DEF.CMD_ACK
        )
        return DEF.CMD_ACK

    def get_address(self, cmd_id, extended):
        self._set_last_cmd(
            DEF.CMD_EXT_GET_ADDR if extended else DEF.CMD_ABBR_GET_ADDR,
            cmd_id,
            DEF.CMD_ACK
        )
        return [DEF.CMD_ACK, self.address]

    def set_address(self, cmd_id, extended, address, slaves):
        retval = DEF.CMD_ACK
        if len(address) != 1:
            retval = DEF.CMD_ERR_FORM
        elif address not in DEF.SLAVE_ADDR_ACCEPTED or address in slaves:
            retval = DEF.CMD_ERR_DATA
        else:
            self.address = address
        self._set_last_cmd(
            DEF.CMD_EXT_SET_ADDR if extended else DEF.CMD_ABBR_SET_ADDR,
            cmd_id,
            retval
        )
        return retval

    def get_time(self, cmd_id, extended):
        self._set_last_cmd(
            DEF.CMD_EXT_GET_TIME if extended else DEF.CMD_ABBR_GET_TIME,
            cmd_id,
            DEF.CMD_ACK
        )
        data = self._datetime_to_time(datetime.utcnow() - self.time_offset)
        return [DEF.CMD_ACK, data]

    def set_time(self, cmd_id, extended, time):
        retval = DEF.CMD_ACK
        try:
            if len(time) != 8:
                raise IndexError
            date = datetime(
                int('%.2d%.2d' % (ord(time[0]), ord(time[1]))),
                ord(time[2]),
                ord(time[3]),
                ord(time[4]),
                ord(time[5]),
                ord(time[6]),
                min(ord(time[7]) * 10000, 999999),
            )
            self.time_offset = datetime.utcnow() - date
        except IndexError:
            retval = DEF.CMD_ERR_FORM
        except ValueError:
            retval = DEF.CMD_ERR_DATA
        self._set_last_cmd(
            DEF.CMD_EXT_SET_TIME if extended else DEF.CMD_ABBR_SET_TIME,
            cmd_id,
            retval
        )
        return retval

    def get_frame(self, cmd_id, extended):
        self._set_last_cmd(
            DEF.CMD_EXT_GET_FRAME if extended else DEF.CMD_ABBR_GET_FRAME,
            cmd_id,
            DEF.CMD_ACK
        )
        return [DEF.CMD_ACK, self.frame_size]

    def set_frame(self, cmd_id, extended, size):
        if len(size) != 1:
            retval = DEF.CMD_ERR_FORM
        elif size not in DEF.FRAME_SIZE_ACCEPTED:
            retval = DEF.CMD_ERR_FRAME_SIZE
        else:
            self.frame_size = size
            retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_SET_FRAME if extended else DEF.CMD_ABBR_SET_FRAME,
            cmd_id,
            retval
        )
        return retval

    def get_port(self, cmd_id, extended, params):
        data = ''
        if len(params) != 3:
            retval = DEF.CMD_ERR_FORM
        else:
            data_type, port_type, port_number = params
            if data_type not in DEF.DATA_TYPES:
                retval = DEF.CMD_ERR_DATA_TYPE
            elif port_type not in DEF.PORT_TYPES:
                retval = DEF.CMD_ERR_PORT_TYPE
            elif ord(port_number) not in DEF.PORT_NUMBERS:
                retval = DEF.CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                data += self.port_settings.get(key, '\x00')
                retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_GET_PORT if extended else DEF.CMD_ABBR_GET_PORT,
            cmd_id,
            retval
        )
        return [retval, data]

    def set_port(self, cmd_id, extended, params):
        if len(params) != 4:
            retval = DEF.CMD_ERR_FORM
        else:
            data_type, port_type, port_number, port_setting = params
            if data_type not in DEF.DATA_TYPES:
                retval = DEF.CMD_ERR_DATA_TYPE
            elif port_type not in DEF.PORT_TYPES:
                retval = DEF.CMD_ERR_PORT_TYPE
            elif ord(port_number) not in DEF.PORT_NUMBERS:
                retval = DEF.CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                self.port_settings[key] = port_setting
                retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_SET_PORT if extended else DEF.CMD_ABBR_SET_PORT,
            cmd_id,
            retval
        )
        return retval

    def get_data(self, cmd_id, extended, params):
        data = ''
        if len(params) != 3:
            retval = DEF.CMD_ERR_FORM
        else:
            data_type, port_type, port_number = params
            if data_type not in DEF.DATA_TYPES:
                retval = DEF.CMD_ERR_DATA_TYPE
            elif port_type not in DEF.PORT_TYPES:
                retval = DEF.CMD_ERR_PORT_TYPE
            elif ord(port_number) not in DEF.PORT_NUMBERS:
                retval = DEF.CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                data += self.port_settings.get(key, '\x00')
                retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_GET_DATA if extended else DEF.CMD_ABBR_GET_DATA,
            cmd_id,
            retval
        )
        return [retval, data]

    def set_data(self, cmd_id, extended, params):
        if len(params) != 4:
            retval = DEF.CMD_ERR_FORM
        else:
            data_type, port_type, port_number, port_setting = params
            if data_type not in DEF.DATA_TYPES:
                retval = DEF.CMD_ERR_DATA_TYPE
            elif port_type not in DEF.PORT_TYPES:
                retval = DEF.CMD_ERR_PORT_TYPE
            elif ord(port_number) not in DEF.PORT_NUMBERS:
                retval = DEF.CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                self.port_settings[key] = port_setting
                retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_SET_DATA if extended else DEF.CMD_ABBR_SET_DATA,
            cmd_id,
            retval
        )
        return retval


class Dewar(Slave):

    def __init__(self, address):
        self.AD_PORTS = [['\x00'] * 4] * 8
        Slave.__init__(self, address)

    def get_data(self, cmd_id, extended, params):
        data = ''
        if len(params) != 3:
            retval = DEF.CMD_ERR_FORM
        else:
            data_type, port_type, port_number = params
            if data_type not in DEF.DATA_TYPES:
                retval = DEF.CMD_ERR_DATA_TYPE
            elif port_type not in DEF.PORT_TYPES:
                retval = DEF.CMD_ERR_PORT_TYPE
            elif ord(port_number) not in DEF.PORT_NUMBERS:
                retval = DEF.CMD_ERR_PORT_NUMBER
            elif (port_type == DEF.PORT_TYPE_AD24 and
                    data_type == DEF.DATA_TYPE_F32):
                data += '\x00' * 4 * 8
                retval = DEF.CMD_ACK
            else:
                key = (data_type, port_type, port_number)
                data += self.port_settings.get(key, '\x00')
                retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_GET_DATA if extended else DEF.CMD_ABBR_GET_DATA,
            cmd_id,
            retval
        )
        return [retval, data]


class Feed(object):

    def __init__(self):
        # The following lists represent:
        # Drain Voltage, left
        # Drain Current, left
        # Gate Voltage, left
        # Drain Voltage, right
        # Drain Current, right
        # Gate Voltage, right
        # For each one of the 5 stages

        self.VDL = [0] * 5
        self.IDL = [0] * 5
        self.VGL = [0] * 5
        self.VDR = [0] * 5
        self.IDR = [0] * 5
        self.VGR = [0] * 5


class LNA(Slave):

    def __init__(self, address, feeds=1):
        self.feeds = [Feed()] * feeds

        self.AD = 0
        self.EN = 0
        self.L_ON = 0
        self.R_ON = 0
        Slave.__init__(self, address)

    def get_data(self, cmd_id, extended, params):
        data = ''
        if len(params) != 3:
            retval = DEF.CMD_ERR_FORM
        else:
            data_type, port_type, port_number = params
            if data_type not in DEF.DATA_TYPES:
                retval = DEF.CMD_ERR_DATA_TYPE
            elif port_type not in DEF.PORT_TYPES:
                retval = DEF.CMD_ERR_PORT_TYPE
            elif ord(port_number) not in DEF.PORT_NUMBERS:
                retval = DEF.CMD_ERR_PORT_NUMBER
            elif (port_type == DEF.PORT_TYPE_AD24 and
                    data_type == DEF.DATA_TYPE_F32):
                data = ''
                STAGE = int(self.AD / 3)
                VALUE = int(self.AD % 3)
                EN = max(self.EN - 1, 0)
                if self.EN > 2:
                    EN += 6
                for i in range(4):
                    index = EN + 2 * i
                    try:
                        if VALUE == 0:
                            # VD
                            data += utils.real_to_bytes(
                                self.feeds[index].VDL[STAGE],
                                little_endian=False
                            )
                            data += utils.real_to_bytes(
                                self.feeds[index].VDR[STAGE],
                                little_endian=False
                            )
                        elif VALUE == 1:
                            # ID
                            data += utils.real_to_bytes(
                                self.feeds[index].IDL[STAGE],
                                little_endian=False
                            )
                            data += utils.real_to_bytes(
                                self.feeds[index].IDR[STAGE],
                                little_endian=False
                            )
                        elif VALUE == 2:
                            # VG
                            data += utils.real_to_bytes(
                                self.feeds[index].VGL[STAGE],
                                little_endian=False
                            )
                            data += utils.real_to_bytes(
                                self.feeds[index].VGR[STAGE],
                                little_endian=False
                            )
                    except IndexError:
                        data += '\x00' * 8
                retval = DEF.CMD_ACK
            else:
                key = (data_type, port_type, port_number)
                data += self.port_settings.get(key, '\x00')
                retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_GET_DATA if extended else DEF.CMD_ABBR_GET_DATA,
            cmd_id,
            retval
        )
        return [retval, data]

    def set_data(self, cmd_id, extended, params):
        retval = DEF.CMD_ACK
        if len(params) < 4:
            retval = DEF.CMD_ERR_FORM
        else:
            data_type, port_type, port_number = params[:3]
            port_setting = params[3:]
            if data_type not in DEF.DATA_TYPES:
                retval = DEF.CMD_ERR_DATA_TYPE
            elif port_type not in DEF.PORT_TYPES:
                retval = DEF.CMD_ERR_PORT_TYPE
            elif ord(port_number) not in DEF.PORT_NUMBERS:
                retval = DEF.CMD_ERR_PORT_NUMBER
            else:
                if port_type == DEF.PORT_TYPE_DIO:
                    if data_type == DEF.DATA_TYPE_U08:
                        if len(port_setting) != 1:
                            retval = DEF.CMD_ERR_DATA
                    elif data_type == DEF.DATA_TYPE_U16:
                        if len(port_setting) != 2:
                            retval = DEF.CMD_ERR_DATA
                    else:
                        retval = DEF.CMD_ERR_DATA
                    if retval == DEF.CMD_ACK:
                        port_setting = utils.bytes_to_binary(
                            port_setting,
                            little_endian=False
                        )
                        self.AD = int(port_setting[:4], 2)
                        self.EN = int(port_setting[4:8], 2)
                        if data_type == DEF.DATA_TYPE_U16:
                            self.L_ON = int(port_setting[8], 2)
                            self.R_ON = int(port_setting[9], 2)
                else:
                    key = (data_type, port_type, port_number)
                    self.port_settings[key] = port_setting
                    retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_SET_DATA if extended else DEF.CMD_ABBR_SET_DATA,
            cmd_id,
            retval
        )
        return retval
