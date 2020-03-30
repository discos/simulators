from datetime import datetime, timedelta
from SocketServer import ThreadingTCPServer
from simulators.common import ListeningSystem


servers = [(('0.0.0.0', 12900), (), ThreadingTCPServer, {})]


CMD_SOH = chr(0x01)
CMD_STX = chr(0x02)
CMD_ETX = chr(0x03)
CMD_EOT = chr(0x04)

CMD_ACK = chr(0x00)
CMD_ERR_CMD = chr(0x01)
CMD_ERR_CHKS = chr(0x02)
CMD_ERR_FORM = chr(0x03)
CMD_ERR_DATA = chr(0x04)
CMD_ERR_TOUT = chr(0x05)
CMD_ERR_ADDR = chr(0x06)
CMD_ERR_TIME = chr(0x07)
CMD_ERR_FRAME_SIZE = chr(0x08)
CMD_ERR_DATA_TYPE = chr(0x09)
CMD_ERR_PORT_TYPE = chr(0x0A)
CMD_ERR_PORT_NUMBER = chr(0x0B)
CMD_ERR_DATA_SIZE = chr(0x0C)

CMD_EXT_INQUIRY = chr(0x41)
CMD_EXT_RESET = chr(0x42)
CMD_EXT_VERSION = chr(0x43)
CMD_EXT_SAVE = chr(0x44)
CMD_EXT_RESTORE = chr(0x45)
CMD_EXT_GET_ADDR = chr(0x46)
CMD_EXT_SET_ADDR = chr(0x47)
CMD_EXT_GET_TIME = chr(0x48)
CMD_EXT_SET_TIME = chr(0x49)
CMD_EXT_GET_FRAME = chr(0x4A)
CMD_EXT_SET_FRAME = chr(0x4B)
CMD_EXT_GET_PORT = chr(0x4C)
CMD_EXT_SET_PORT = chr(0x4D)
CMD_EXT_GET_DATA = chr(0x4E)
CMD_EXT_SET_DATA = chr(0x4F)

CMD_EXT_NO_PARAMS = [
    CMD_EXT_INQUIRY,
    CMD_EXT_RESET,
    CMD_EXT_VERSION,
    CMD_EXT_SAVE,
    CMD_EXT_RESTORE,
    CMD_EXT_GET_ADDR,
    CMD_EXT_GET_TIME,
    CMD_EXT_GET_FRAME
]

CMD_EXT_WITH_PARAMS = [
    CMD_EXT_SET_ADDR,
    CMD_EXT_SET_TIME,
    CMD_EXT_SET_FRAME,
    CMD_EXT_GET_PORT,
    CMD_EXT_SET_PORT,
    CMD_EXT_GET_DATA,
    CMD_EXT_SET_DATA
]

CMD_EXT = []
CMD_EXT += CMD_EXT_NO_PARAMS + CMD_EXT_WITH_PARAMS

CMD_ABBR_INQUIRY = chr(0x61)
CMD_ABBR_RESET = chr(0x62)
CMD_ABBR_VERSION = chr(0x63)
CMD_ABBR_SAVE = chr(0x64)
CMD_ABBR_RESTORE = chr(0x65)
CMD_ABBR_GET_ADDR = chr(0x66)
CMD_ABBR_SET_ADDR = chr(0x67)
CMD_ABBR_GET_TIME = chr(0x68)
CMD_ABBR_SET_TIME = chr(0x69)
CMD_ABBR_GET_FRAME = chr(0x6A)
CMD_ABBR_SET_FRAME = chr(0x6B)
CMD_ABBR_GET_PORT = chr(0x6C)
CMD_ABBR_SET_PORT = chr(0x6D)
CMD_ABBR_GET_DATA = chr(0x6E)
CMD_ABBR_SET_DATA = chr(0x6F)

CMD_ABBR_NO_PARAMS = [
    CMD_ABBR_INQUIRY,
    CMD_ABBR_RESET,
    CMD_ABBR_VERSION,
    CMD_ABBR_SAVE,
    CMD_ABBR_RESTORE,
    CMD_ABBR_GET_ADDR,
    CMD_ABBR_GET_TIME,
    CMD_ABBR_GET_FRAME
]

CMD_ABBR_WITH_PARAMS = [
    CMD_ABBR_SET_ADDR,
    CMD_ABBR_SET_TIME,
    CMD_ABBR_SET_FRAME,
    CMD_ABBR_GET_PORT,
    CMD_ABBR_SET_PORT,
    CMD_ABBR_GET_DATA,
    CMD_ABBR_SET_DATA
]

CMD_ABBR = []
CMD_ABBR += CMD_ABBR_NO_PARAMS + CMD_ABBR_WITH_PARAMS

CMD_INQUIRY = [CMD_EXT_INQUIRY, CMD_ABBR_INQUIRY]
CMD_RESET = [CMD_EXT_RESET, CMD_ABBR_RESET]
CMD_VERSION = [CMD_EXT_VERSION, CMD_ABBR_VERSION]
CMD_SAVE = [CMD_EXT_SAVE, CMD_ABBR_SAVE]
CMD_RESTORE = [CMD_EXT_RESTORE, CMD_ABBR_RESTORE]
CMD_GET_ADDR = [CMD_EXT_GET_ADDR, CMD_ABBR_GET_ADDR]
CMD_SET_ADDR = [CMD_EXT_SET_ADDR, CMD_ABBR_SET_ADDR]
CMD_GET_TIME = [CMD_EXT_GET_TIME, CMD_ABBR_GET_TIME]
CMD_SET_TIME = [CMD_EXT_SET_TIME, CMD_ABBR_SET_TIME]
CMD_GET_FRAME = [CMD_EXT_GET_FRAME, CMD_ABBR_GET_FRAME]
CMD_SET_FRAME = [CMD_EXT_SET_FRAME, CMD_ABBR_SET_FRAME]
CMD_GET_PORT = [CMD_EXT_GET_PORT, CMD_ABBR_GET_PORT]
CMD_SET_PORT = [CMD_EXT_SET_PORT, CMD_ABBR_SET_PORT]
CMD_GET_DATA = [CMD_EXT_GET_DATA, CMD_ABBR_GET_DATA]
CMD_SET_DATA = [CMD_EXT_SET_DATA, CMD_ABBR_SET_DATA]

ACCEPTED_COMMANDS = []
ACCEPTED_COMMANDS += CMD_EXT_NO_PARAMS
ACCEPTED_COMMANDS += CMD_EXT_WITH_PARAMS
ACCEPTED_COMMANDS += CMD_ABBR_NO_PARAMS
ACCEPTED_COMMANDS += CMD_ABBR_WITH_PARAMS

SLAVE_ADDR_BROADCAST_NO_ANSWER = chr(0x00)
SLAVE_ADDR_BROADCAST_WITH_ANSWER = chr(0x7F)
SLAVE_ADDR_BROADCAST = [
    SLAVE_ADDR_BROADCAST_NO_ANSWER,
    SLAVE_ADDR_BROADCAST_WITH_ANSWER
]
SLAVE_ADDR_ACCEPTED = [chr(addr) for addr in range(0x01, 0x7F)]
SLAVE_ADDRESSES = SLAVE_ADDR_ACCEPTED + SLAVE_ADDR_BROADCAST

MASTER_ADDRESSES = [chr(addr) for addr in range(0x01, 0x7F)]
PROGRESSIVE_IDS = [chr(addr) for addr in range(0x00, 0x80)]

FRAME_SIZE_ACCEPTED = [chr(addr) for addr in range(0x01, 0x7F)]

# Index of the byte that stores the command code
SLAVE_IDX = 1
MASTER_IDX = 2
CMD_IDX = 3
ID_IDX = 4
PAR_LEN_IDX = 5
PAR_LIST_IDX = 6
CHECKSUM_IDX = -2

AD24_LEN = 8

VERSION = '\x00' * 8  # Dummy version


# Commands
"""MCB_CMD_DATA_TYPE_B01 = chr(0x03)
MCB_CMD_DATA_TYPE_F32 = chr(0x18)"""


class System(ListeningSystem):

    def __init__(self):
        self.slaves = {
            chr(address): Slave(chr(address)) for address in range(0x01, 0x20)
        }
        self._set_default()

    def _set_default(self):
        self.msg = ''

    @staticmethod
    def checksum(msg):
        chksum = 0
        for char in msg:
            chksum = chksum ^ ord(char)
        return chr(chksum)

    def parse(self, byte):
        if not self.msg:
            if byte == CMD_SOH:
                self.msg += byte
            else:
                self._set_default()
                return False
        elif len(self.msg) in [1, 2, 3, 5]:
            # Length 1: incoming byte is the slave address
            # 2: incoming byte is the master address
            # 3: incoming byte is the command
            # 5: incoming byte is either the checksum or the params list length
            # Whatever byte is received, we check its consistency later on
            self.msg += byte
        elif len(self.msg) == 4:
            self.msg += byte
            if (self.msg[CMD_IDX] in CMD_ABBR_NO_PARAMS or
                    self.msg[CMD_IDX] not in ACCEPTED_COMMANDS):
                # Either a short command without params or an unknown command
                msg = self.msg
                self._set_default()
                return self._parse(msg)
        elif len(self.msg) >= 6:
            self.msg += byte
            if len(self.msg) == 7 and self.msg[CMD_IDX] in CMD_EXT_NO_PARAMS:
                msg = self.msg
                self._set_default()
                return self._parse(msg)
            elif len(self.msg) == 6 + ord(self.msg[PAR_LEN_IDX]):
                if self.msg[CMD_IDX] in CMD_ABBR_WITH_PARAMS:
                    msg = self.msg
                    self._set_default()
                    return self._parse(msg)
            elif len(self.msg) == 8 + ord(self.msg[PAR_LEN_IDX]):
                # Command should be complete, we try to parse it
                msg = self.msg
                self._set_default()
                return self._parse(msg)
        return True

    def _parse(self, msg):
        master_address = msg[MASTER_IDX]
        slave_address = msg[SLAVE_IDX]
        command = msg[CMD_IDX]
        cmd_id = msg[ID_IDX]

        checksum_error = False
        is_extended = False
        if command in CMD_EXT:
            is_extended = True
            if msg[CHECKSUM_IDX] != self.checksum(msg[:CHECKSUM_IDX]):
                checksum_error = True

        params = ''
        if command in CMD_EXT_WITH_PARAMS + CMD_ABBR_WITH_PARAMS:
            params = msg[PAR_LIST_IDX:]
            if is_extended:
                params = params[:CHECKSUM_IDX]

        send_answer = True
        slaves = []
        if slave_address not in SLAVE_ADDR_BROADCAST:
            slaves.append(slave_address)
        else:
            slaves += self.slaves.keys()
            if slave_address == SLAVE_ADDR_BROADCAST_NO_ANSWER:
                send_answer = False

        total_answer = ''
        # Iterate through the desired slaves
        for slave_address in slaves:
            # Parse the command and call the appropriate slave method
            answer = ''
            answer += CMD_STX
            answer += master_address
            answer += slave_address
            answer += command
            answer += cmd_id

            slave = self.slaves.get(slave_address)
            if not slave:
                # Slave is not present, we should not answer
                continue

            if command not in ACCEPTED_COMMANDS:
                # Unknown command. We send back a short error answer
                answer += CMD_ERR_CMD
                total_answer += answer
                continue
            elif checksum_error:
                answer += CMD_ERR_CHKS
            elif command in CMD_INQUIRY:
                ans, data = slave.inquiry()
                answer += ans + chr(len(data)) + data
            elif command in CMD_RESET:
                ans = slave.reset()
                answer += ans
            elif command in CMD_VERSION:
                ans, data = slave.version(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in CMD_SAVE:
                ans = slave.save(cmd_id, is_extended)
                answer += ans
            elif command in CMD_RESTORE:
                ans = slave.restore(cmd_id, is_extended)
                answer += ans
            elif command in CMD_GET_ADDR:
                ans, data = slave.get_address(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in CMD_SET_ADDR:
                ans = slave.set_address(
                    cmd_id,
                    is_extended,
                    params,
                    self.slaves
                )
                if ans == CMD_ACK:
                    self.slaves[params] = self.slaves.pop(slave_address)
                answer += ans
            elif command in CMD_GET_TIME:
                ans, data = slave.get_time(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in CMD_SET_TIME:
                ans = slave.set_time(cmd_id, is_extended, params)
                answer += ans
            elif command in CMD_GET_FRAME:
                ans, data = slave.get_frame(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in CMD_SET_FRAME:
                ans = slave.set_frame(cmd_id, is_extended, params)
                answer += ans
            elif command in CMD_GET_PORT:
                ans, data = slave.get_port(cmd_id, is_extended, params)
                answer += ans
                if ans == CMD_ACK:
                    answer += chr(len(data)) + data
            elif command in CMD_SET_PORT:
                ans = slave.set_port(cmd_id, is_extended, params)
                answer += ans
            elif command in CMD_GET_DATA:
                ans, data = slave.get_data(cmd_id, is_extended, params)
                answer += ans
                if ans == CMD_ACK:
                    answer += chr(len(data)) + data
            elif command in CMD_SET_DATA:
                ans = slave.set_data(cmd_id, is_extended, params)
                answer += ans

            if is_extended:
                answer += self.checksum(answer) + CMD_EOT

            total_answer += answer

        return total_answer if send_answer and total_answer else True


class Slave(object):

    data_types = range(0x00, 0x0A) + [0x3F] + range(0x41, 0x4A) + [0x7F]
    port_types = range(0x80)
    port_numbers = range(0x80)

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

        return [CMD_ACK, data]

    def reset(self):
        self._reset()
        return CMD_ACK

    def version(self, cmd_id, extended):
        self._set_last_cmd(
            CMD_EXT_VERSION if extended else CMD_ABBR_VERSION,
            cmd_id,
            CMD_ACK
        )
        return [CMD_ACK, VERSION]

    def save(self, cmd_id, extended):
        # The configuration should be saved but we ignore this feature for now
        self._set_last_cmd(
            CMD_EXT_SAVE if extended else CMD_ABBR_SAVE,
            cmd_id,
            CMD_ACK
        )
        return CMD_ACK

    def restore(self, cmd_id, extended):
        # Should read the saved configuration and perform a reset
        # Since we don't save any configuration with the same command
        # we leave the configuration as it is, we answer with an ACK
        self._set_last_cmd(
            CMD_EXT_RESTORE if extended else CMD_ABBR_RESTORE,
            cmd_id,
            CMD_ACK
        )
        return CMD_ACK

    def get_address(self, cmd_id, extended):
        self._set_last_cmd(
            CMD_EXT_GET_ADDR if extended else CMD_ABBR_GET_ADDR,
            cmd_id,
            CMD_ACK
        )
        return [CMD_ACK, self.address]

    def set_address(self, cmd_id, extended, address, slaves):
        retval = CMD_ACK
        if len(address) != 1:
            retval = CMD_ERR_FORM
        elif address not in SLAVE_ADDR_ACCEPTED or address in slaves:
            retval = CMD_ERR_DATA
        else:
            self.address = address
        self._set_last_cmd(
            CMD_EXT_SET_ADDR if extended else CMD_ABBR_SET_ADDR,
            cmd_id,
            retval
        )
        return retval

    def get_time(self, cmd_id, extended):
        self._set_last_cmd(
            CMD_EXT_GET_TIME if extended else CMD_ABBR_GET_TIME,
            cmd_id,
            CMD_ACK
        )
        data = self._datetime_to_time(datetime.utcnow() - self.time_offset)
        return [CMD_ACK, data]

    def set_time(self, cmd_id, extended, time):
        retval = CMD_ACK
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
            retval = CMD_ERR_FORM
        except ValueError:
            retval = CMD_ERR_DATA
        self._set_last_cmd(
            CMD_EXT_SET_TIME if extended else CMD_ABBR_SET_TIME,
            cmd_id,
            retval
        )
        return retval

    def get_frame(self, cmd_id, extended):
        self._set_last_cmd(
            CMD_EXT_GET_FRAME if extended else CMD_ABBR_GET_FRAME,
            cmd_id,
            CMD_ACK
        )
        return [CMD_ACK, self.frame_size]

    def set_frame(self, cmd_id, extended, size):
        if len(size) != 1:
            retval = CMD_ERR_FORM
        elif size not in FRAME_SIZE_ACCEPTED:
            retval = CMD_ERR_FRAME_SIZE
        else:
            self.frame_size = size
            retval = CMD_ACK
        self._set_last_cmd(
            CMD_EXT_SET_FRAME if extended else CMD_ABBR_SET_FRAME,
            cmd_id,
            retval
        )
        return retval

    def get_port(self, cmd_id, extended, params):
        data = ''
        if len(params) != 3:
            retval = CMD_ERR_FORM
        else:
            data_type, port_type, port_number = params
            if ord(data_type) not in self.data_types:
                retval = CMD_ERR_DATA_TYPE
            elif ord(port_type) not in self.port_types:
                retval = CMD_ERR_PORT_TYPE
            elif ord(port_number) not in self.port_numbers:
                retval = CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                data += self.port_settings.get(key, '\x00')
                retval = CMD_ACK
        self._set_last_cmd(
            CMD_EXT_GET_PORT if extended else CMD_ABBR_GET_PORT,
            cmd_id,
            retval
        )
        return [retval, data]

    def set_port(self, cmd_id, extended, params):
        if len(params) != 4:
            retval = CMD_ERR_FORM
        else:
            data_type, port_type, port_number, port_setting = params
            if ord(data_type) not in self.data_types:
                retval = CMD_ERR_DATA_TYPE
            elif ord(port_type) not in self.port_types:
                retval = CMD_ERR_PORT_TYPE
            elif ord(port_number) not in self.port_numbers:
                retval = CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                self.port_settings[key] = port_setting
                retval = CMD_ACK
        self._set_last_cmd(
            CMD_EXT_SET_PORT if extended else CMD_ABBR_SET_PORT,
            cmd_id,
            retval
        )
        return retval

    def get_data(self, cmd_id, extended, params):
        data = ''
        if len(params) != 3:
            retval = CMD_ERR_FORM
        else:
            data_type, port_type, port_number = params
            if ord(data_type) not in self.data_types:
                retval = CMD_ERR_DATA_TYPE
            elif ord(port_type) not in self.port_types:
                retval = CMD_ERR_PORT_TYPE
            elif ord(port_number) not in self.port_numbers:
                retval = CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                data += self.port_settings.get(key, '\x00')
                retval = CMD_ACK
        self._set_last_cmd(
            CMD_EXT_GET_DATA if extended else CMD_ABBR_GET_DATA,
            cmd_id,
            retval
        )
        return [retval, data]

    def set_data(self, cmd_id, extended, params):
        if len(params) != 4:
            retval = CMD_ERR_FORM
        else:
            data_type, port_type, port_number, port_setting = params
            if ord(data_type) not in self.data_types:
                retval = CMD_ERR_DATA_TYPE
            elif ord(port_type) not in self.port_types:
                retval = CMD_ERR_PORT_TYPE
            elif ord(port_number) not in self.port_numbers:
                retval = CMD_ERR_PORT_NUMBER
            else:
                key = (data_type, port_type, port_number)
                self.port_settings[key] = port_setting
                retval = CMD_ACK
        self._set_last_cmd(
            CMD_EXT_SET_DATA if extended else CMD_ABBR_SET_DATA,
            cmd_id,
            retval
        )
        return retval
