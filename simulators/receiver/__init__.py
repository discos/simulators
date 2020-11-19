from SocketServer import ThreadingTCPServer
from simulators.common import ListeningSystem
from simulators.receiver import DEFINITIONS as DEF
from simulators.receiver.slaves import Slave, Dewar, LNA


servers = []
servers.append((
    ('0.0.0.0', 12900),
    (),
    ThreadingTCPServer,
    {'slave_type': Dewar, 'min_index': 1, 'max_index': 1}
))
servers.append((
    ('0.0.0.0', 12901),
    (),
    ThreadingTCPServer,
    {'slave_type': LNA, 'min_index': 1, 'max_index': 1, 'feeds': 1}
))
servers.append((
    ('0.0.0.0', 12902),
    (),
    ThreadingTCPServer,
    {'slave_type': Dewar, 'min_index': 1, 'max_index': 1}
))
servers.append((
    ('0.0.0.0', 12903),
    (),
    ThreadingTCPServer,
    {'slave_type': LNA, 'min_index': 1, 'max_index': 1, 'feeds': 7}
))


class System(ListeningSystem):

    def __init__(self, slave_type=Slave, min_index=1, max_index=1, **kwargs):
        max_index += 1
        rng = range(min_index, max_index)
        self.slaves = {
            chr(address): slave_type(chr(address), **kwargs) for address in rng
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
            if byte == DEF.CMD_SOH:
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
            if (self.msg[DEF.CMD_IDX] in DEF.CMD_ABBR_NO_PARAMS or
                    self.msg[DEF.CMD_IDX] not in DEF.ACCEPTED_COMMANDS):
                # Either a short command without params or an unknown command
                msg = self.msg
                self._set_default()
                return self._parse(msg)
        elif len(self.msg) >= 6:
            self.msg += byte
            if (len(self.msg) == 7 and
                    self.msg[DEF.CMD_IDX] in DEF.CMD_EXT_NO_PARAMS):
                msg = self.msg
                self._set_default()
                return self._parse(msg)
            elif len(self.msg) == 6 + ord(self.msg[DEF.PAR_LEN_IDX]):
                if self.msg[DEF.CMD_IDX] in DEF.CMD_ABBR_WITH_PARAMS:
                    msg = self.msg
                    self._set_default()
                    return self._parse(msg)
            elif len(self.msg) == 8 + ord(self.msg[DEF.PAR_LEN_IDX]):
                # Command should be complete, we try to parse it
                msg = self.msg
                self._set_default()
                return self._parse(msg)
        return True

    def _parse(self, msg):
        master_address = msg[DEF.MASTER_IDX]
        slave_address = msg[DEF.SLAVE_IDX]
        command = msg[DEF.CMD_IDX]
        cmd_id = msg[DEF.ID_IDX]

        checksum_error = False
        is_extended = False
        if command in DEF.CMD_EXT:
            is_extended = True
            if msg[DEF.CHECKSUM_IDX] != self.checksum(msg[:DEF.CHECKSUM_IDX]):
                checksum_error = True

        params = ''
        if command in DEF.CMD_EXT_WITH_PARAMS + DEF.CMD_ABBR_WITH_PARAMS:
            params = msg[DEF.PAR_LIST_IDX:]
            if is_extended:
                params = params[:DEF.CHECKSUM_IDX]

        send_answer = True
        slaves = []
        if slave_address not in DEF.SLAVE_ADDR_BROADCAST:
            slaves.append(slave_address)
        else:
            slaves += self.slaves.keys()
            if slave_address == DEF.SLAVE_ADDR_BROADCAST_NO_ANSWER:
                send_answer = False

        total_answer = ''
        # Iterate through the desired slaves
        for slave_address in slaves:
            slave = self.slaves.get(slave_address)
            if not slave:
                # Slave is not present, we should not answer
                continue

            # Parse the command and call the appropriate slave method
            answer = ''
            answer += DEF.CMD_STX
            answer += master_address
            answer += slave_address
            answer += command
            answer += cmd_id

            if command not in DEF.ACCEPTED_COMMANDS:
                # Unknown command. We send back a short error answer
                answer += DEF.CMD_ERR_CMD
                total_answer += answer
                continue
            elif checksum_error:
                answer += DEF.CMD_ERR_CHKS
            elif command in DEF.CMD_INQUIRY:
                ans, data = slave.inquiry()
                answer += ans + chr(len(data)) + data
            elif command in DEF.CMD_RESET:
                ans = slave.reset()
                answer += ans
            elif command in DEF.CMD_VERSION:
                ans, data = slave.version(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in DEF.CMD_SAVE:
                ans = slave.save(cmd_id, is_extended)
                answer += ans
            elif command in DEF.CMD_RESTORE:
                ans = slave.restore(cmd_id, is_extended)
                answer += ans
            elif command in DEF.CMD_GET_ADDR:
                ans, data = slave.get_address(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in DEF.CMD_SET_ADDR:
                ans = slave.set_address(
                    cmd_id,
                    is_extended,
                    params,
                    self.slaves
                )
                if ans == DEF.CMD_ACK:
                    self.slaves[params] = self.slaves.pop(slave_address)
                answer += ans
            elif command in DEF.CMD_GET_TIME:
                ans, data = slave.get_time(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in DEF.CMD_SET_TIME:
                ans = slave.set_time(cmd_id, is_extended, params)
                answer += ans
            elif command in DEF.CMD_GET_FRAME:
                ans, data = slave.get_frame(cmd_id, is_extended)
                answer += ans + chr(len(data)) + data
            elif command in DEF.CMD_SET_FRAME:
                ans = slave.set_frame(cmd_id, is_extended, params)
                answer += ans
            elif command in DEF.CMD_GET_PORT:
                ans, data = slave.get_port(cmd_id, is_extended, params)
                answer += ans
                if ans == DEF.CMD_ACK:
                    data = params[:3] + data
                    answer += chr(len(data)) + data
            elif command in DEF.CMD_SET_PORT:
                ans = slave.set_port(cmd_id, is_extended, params)
                answer += ans
            elif command in DEF.CMD_GET_DATA:
                ans, data = slave.get_data(cmd_id, is_extended, params)
                answer += ans
                if ans == DEF.CMD_ACK:
                    data = params[:3] + data
                    answer += chr(len(data)) + data
            elif command in DEF.CMD_SET_DATA:
                ans = slave.set_data(cmd_id, is_extended, params)
                answer += ans

            if is_extended:
                answer += self.checksum(answer) + DEF.CMD_EOT

            total_answer += answer

        return total_answer if send_answer and total_answer else True
