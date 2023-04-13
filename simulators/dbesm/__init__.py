import random
from socketserver import ThreadingTCPServer
import numpy
from simulators.common import ListeningSystem

servers = [(('0.0.0.0', 11111), (), ThreadingTCPServer, {})]


class System(ListeningSystem):
    header = '#'
    tail = '\x0D'
    ack = 'ACK\x0D\x0A'
    nak = 'NAK\x0D\x0A'
    max_msg_length = 15

    devices = {
        0: 'DBE',
        1: 'FBCB',
    }

    commands = {
        'DBE SETALLMODE': '_set_allmode',
        'DBE MODE': '_set_mode',
        'DBE STOREALLMODE': '_store_allmode',
        'DBE CLRMODE': '_clr_mode',
        'DBE STATUS': '_status',
        'DBE SETATT': '_set_att',
        'DBE SETAMP': '_set_amp',
        'DBE SETEQ': '_set_eq',
        'DBE SETBPF': '_set_bpf',
        'DBE ALLDIAG': '_all_diag',
        'DBE DIAG': '_diag',
        'DBE': '_not_implemented',
        'FBCB': '_not_implemented',
    }

    errors = {
        9999: 'NOT_IMPLEMENTED',
        1000: 'ERROR_ARGS_NOT_VALID',
        1001: 'unknow command',
        1002: 'ERROR_DEVICE_UNKNOWN',
        1003: 'CFG file not existing',
        1004: 'reading cfg file',
        1005: 'BOARD X unreachable',
        1006: 'BOARD 1 2 3 4 unreachable',
        1007: 'BOARD X not existing',
        1008: 'writing cfg file',
        1009: 'deleting cfg file',
        1010: 'ATT X not existing',
        1011: 'value out of range',
        1012: 'AMP X not existing',
        1013: 'EQ X not existing',
        1014: 'BPF X not existing',
    }

    obs_mode = [
        'MF20_1s',
        'MF10_2s',
        'DF_8s',
        '3-Band_1s',
        '3-Band',
        'MFS_7',
    ]

    def __init__(self):
        self.msg = ''
        self.cmd_id = ''

        # Status -1 -> board not available
        self.boards = [
            {
                'Address': '12',
                "Status": 0,
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "EQ": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "BPF": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "5V": 0.00,
                "3V3": 0.00,
                "T0": 00.00
            },
            {
                'Address': '13',
                "Status": 0,
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "EQ": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "BPF": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "5V": 0.00,
                "3V3": 0.00,
                "T0": 00.00
            },
            {
                'Address': '14',
                "Status": 0,
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "EQ": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "BPF": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "5V": 0.00,
                "3V3": 0.00,
                "T0": 00.00
            },
            {
                'Address': '15',
                "Status": 0,
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "EQ": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "BPF": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                "5V": 0.00,
                "3V3": 0.00,
                "T0": 00.00
            },
        ]

    def _init_reg(self):
        reg = random.sample(range(0, 255), 10)
        return reg

    def _init_att(self):
        att = [round(elem * 2) / 2 for elem
               in numpy.random.uniform(0.0, 31.5, 17)]
        return att

    def _set_default(self):
        self.msg = ''

    def parse(self, byte):
        self.msg += byte

        if byte == self.tail:
            msg = self.msg[:-1]
            self.msg = ''
            return self._execute(msg)
        return True

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, comprehensive of its header and tail.
        """
        args = [x.strip() for x in msg.split(' ')]
        try:
            device_code = list(self.devices.keys())[
                list(self.devices.values()).index(args[0])]
        except ValueError:
            return self._error(-1, 1001)

        params = [device_code]

        if len(args) == 1:
            cmd = self.commands.get(args[0])
            args = args[1:]
        else:
            cmd = self.commands.get(args[0] + ' ' + args[1])
            args = args[2:]

        if not cmd:
            return self._error(params[0], 1001)
        cmd = getattr(self, cmd)
        try:
            for param in args:
                params.append(param)
        except ValueError:
            return self.nak
        return cmd(params)

    def _set_allmode(self, params):
        err = []
        if len(params) != 2:
            return self._error(params[0], 1001)
        elif params[1] not in self.obs_mode:
            return self._error(params[0], 1003)
        for key in self.boards:
            if key['Status'] != 0:
                err.append(key['Address'])
        if len(err) > 0:
            if len(err) == 1:
                return self._error(params[0], 1005, err[0])
            else:
                return self._error(params[0], 1005, ' '.join(map(str, err)))
        else:
            return self.ack

    def _set_mode(self, params):
        selected_board = next((sub for sub in self.boards
                               if sub['Address'] == params[2]), None)
        if len(params) != 4:
            return self._error(params[0], 1001)
        elif selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif params[3] not in self.obs_mode:
            return self._error(params[0], 1003)
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        else:
            return self.ack

    def _store_allmode(self, params):
        err = []
        if len(params) != 2:
            return self._error(params[0], 1001)
        elif params[1] in self.obs_mode:
            return self._error(params[0], 1008)
        for key in self.boards:
            if key['Status'] != 0:
                err.append(key['Address'])
        if len(err) > 0:
            if len(err) == 1:
                return self._error(params[0], 1005, err[0])
            else:
                return self._error(params[0], 1005, ' '.join(map(str, err)))
        else:
            self.obs_mode.append(params[1])
            return self.ack

    def _clr_mode(self, params):
        if len(params) != 2:
            return self._error(params[0], 1001)
        elif params[1] not in self.obs_mode:
            return self._error(params[0], 1003)
        else:
            self.obs_mode.remove(params[1])
            return self.ack

    def _status(self, params):
        if len(params) != 3:
            return self._error(params[0], 1001)

        selected_board = next((sub for sub in self.boards
                               if sub['Address'] == params[2]), None)
        if selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        retval = f'ACK\nREG=[{" ".join(map(str,selected_board["REG"]))}]\n\n'\
            f'ATT=[{" ".join(map(str,selected_board["ATT"])) }]\x0A'
        return retval

    def _set_att(self, params):
        if len(params) != 6:
            return self._error(params[0], 1001)
        selected_board = next((sub for sub in self.boards
                               if sub['Address'] == params[3]), None)
        if selected_board is None:
            return self._error(params[0], 1007, params[3])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[3])
        elif int(params[1]) not in list(range(0, 17)):
            return self._error(params[0], 1010, params[1])
        elif float(params[5]) not in list(numpy.arange(0, 31.5, 0.5)):
            return self._error(params[0], 1011, selected_board["Address"])
        else:
            selected_board["ATT"][int(params[1])] = float(params[5])
            return self.ack

    def _set_amp(self, params):
        if len(params) != 6:
            return self._error(params[0], 1001)
        selected_board = next((sub for sub in self.boards
                               if sub['Address'] == params[3]), None)
        if selected_board is None:
            return self._error(params[0], 1007, params[3])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[3])
        elif int(params[1]) not in list(range(1, 11)):
            return self._error(params[0], 1012, params[1])
        elif int(params[5]) not in [0, 1]:
            return self._error(params[0], 1011, selected_board["Address"])
        else:
            selected_board["AMP"][int(params[1])-1] = params[5]
            return self.ack

    def _set_eq(self, params):
        if len(params) != 6:
            return self._error(params[0], 1001)
        selected_board = next((sub for sub in self.boards
                               if sub['Address'] == params[3]), None)
        if selected_board is None:
            return self._error(params[0], 1007, params[3])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[3])
        elif int(params[1]) not in list(range(1, 11)):
            return self._error(params[0], 1013, params[1])
        elif float(params[5]) not in [0, 1]:
            return self._error(params[0], 1011, selected_board["Address"])
        else:
            selected_board["EQ"][int(params[1])-1] = params[5]
            return self.ack

    def _set_bpf(self, params):
        channels = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '1a', '1b']
        if len(params) != 6:
            return self._error(params[0], 1001)
        selected_board = next((sub for sub in self.boards
                               if sub['Address'] == params[3]), None)
        if selected_board is None:
            return self._error(params[0], 1007, params[3])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[3])
        elif params[1] not in channels:
            return self._error(params[0], 1014, params[1])
        elif float(params[5]) not in [0, 1]:
            return self._error(params[0], 1011, selected_board["Address"])
        else:
            channel = -1
            if params[1] == '1a':
                channel = 0
            elif params[1] == '1b':
                channel = 1
            else:
                channel = int(params[1])-1
            selected_board["BPF"][channel] = params[5]
            return self.ack

    def _all_diag(self, params):
        retval = ''
        if len(params) != 1:
            return self._error(params[0], 1001)
        else:
            for board in self.boards:
                retval += f'BOARD {board["Address"]} '
                if board['Status'] == 0:
                    retval += self.ack
                    retval += f'5V {board["5V"]} 3V3 {board["3V3"]}\n'
                    retval += f'T0 {board["T0"]}\n\n'
                else:
                    retval += 'ERR DBE BOARD unreachable\n\n'
            return retval

    def _diag(self, params):
        if len(params) != 3:
            return self._error(params[0], 1001)
        selected_board = next((sub for sub in self.boards
                               if sub['Address'] == params[2]), None)
        if selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        else:
            retval = self.ack+'\n'
            retval += f'BOARD {selected_board["Address"]}\n'
            retval += f'5V {selected_board["5V"]} 3V3 {selected_board["3V3"]}\n'
            retval += f'T0 {selected_board["T0"]}\n'
        return retval

    def _not_implemented(self, params):
        return self._error(params[0], 9999)

    def _error(self, device_code, error_code, board_address=None):
        error_string = self.errors.get(error_code)
        if error_code == 1001:
            retval = f'NAK {error_string}\x0A'
        elif error_code in [1005, 1007, 1010, 1011, 1014]:
            device_string = self.devices.get(device_code)
            retval = f'ERR {device_string} '\
                f'{error_string.replace("X", board_address)}{self.tail}\x0A'
        else:
            device_string = self.devices.get(device_code)
            retval = f'ERR {device_string} {error_string}{self.tail}\x0A'
        return retval
