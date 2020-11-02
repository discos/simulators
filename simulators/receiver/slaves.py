import itertools
from random import random
from datetime import datetime, timedelta
from simulators import utils
from simulators.receiver import DEFINITIONS as DEF


class Slave(object):

    def __init__(self, address):
        self.AD_PORTS = [[0] * 4] * 8
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
                # Generate random temperature values between 0K and 5K
                for port in range(len(self.AD_PORTS)):
                    p = []
                    p[:0] = utils.real_to_bytes(random() * 5)
                    self.AD_PORTS[port] = p
                data += ''.join(
                    list(itertools.chain.from_iterable(self.AD_PORTS))
                )
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


class LNA(Slave):

    def __init__(self, address, feeds=1):
        # The following STAGES values represents:
        # Drain Voltage, left
        # Drain Current, left
        # Gate Voltage, left
        # Drain Voltage, right
        # Drain Current, right
        # Gate Voltage, right
        self.STAGES = [[0, 0, 0, 0, 0, 0]] * 5
        # Prova assegnazione valori
        self.STAGES = []
        for i in range(5):
            stage = [
                i * 6,
                i * 6 + 1,
                i * 6 + 2,
                i * 6 + 3,
                i * 6 + 4,
                i * 6 + 5
            ]
            self.STAGES.append(stage)
        self.feeds = feeds
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
                    data_type == DEF.DATA_TYPE_AD24):
                data += list(itertools.chain.from_iterable(self.AD_PORTS))
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
                if (port_type == DEF.PORT_TYPE_DIO and
                        data_type == DEF.DATA_TYPE_U08):
                    pass

                key = (data_type, port_type, port_number)
                self.port_settings[key] = port_setting
                retval = DEF.CMD_ACK
        self._set_last_cmd(
            DEF.CMD_EXT_SET_DATA if extended else DEF.CMD_ABBR_SET_DATA,
            cmd_id,
            retval
        )
        return retval
