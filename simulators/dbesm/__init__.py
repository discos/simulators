import random
from socketserver import ThreadingTCPServer
import numpy
from simulators.common import ListeningSystem

servers = [(('0.0.0.0', 11111), (), ThreadingTCPServer, {})]


class System(ListeningSystem):
    tail = '\x0A'
    ack = 'ACK'
    nak = 'NAK'
    max_msg_length = 15

    devices = {
        0: 'DBE',
        1: 'FBCB',
    }

    commands = {
        'DBE SETALLMODE': '_set_allmode',
        'DBE MODE': '_set_mode',
        'DBE STOREALLMODE': '_store_allmode',
        'DBE DELETEFILE': '_delete_file',
        'DBE GETSTATUS': '_get_status',
        'DBE SETATT': '_set_att',
        'DBE SETAMP': '_set_amp',
        'DBE SETEQ': '_set_eq',
        'DBE SETBPF': '_set_bpf',
        'DBE ReadALLDIAG': '_all_diag',
        'DBE ReadDIAG': '_diag',
        'DBE SETSTATUS': '_set_status',
        'DBE GETCOMP': '_get_comp',
        'DBE GETCFG': '_get_cfg',
        'DBE SETDBEATT': '_set_dbeatt',
        'DBE GETDBEATT': '_get_dbeatt',
        'DBE GETFIRM': '_get_firm',
        'DBE SETDBEAMP': '_set_dbeamp',
        'DBE GETDBEAMP': '_get_dbeamp',
        'DBE SETDBEEQ': '_set_dbeeq',
        'DBE GETDBEEQ': '_get_dbeeq',
        'DBE SETDBEBPF': '_set_dbebpf',
        'DBE GETDBEBPF': '_get_dbebpf'
    }

    errors = {
        1001: 'unknown command',
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
        1015: 'Output not existing',
    }

    obs_mode = [
        'MF20_1s',
        'MF10_2s',
        'DF_8s',
        '3-Band_1s',
        '3-Band',
        'MFS_7',
    ]

    out_boards = ['0', '0', '0', '1', '1', '2', '2', '3', '3']
    out_dbe = ['1_DBBC2', 'prova', 'SARDA_01', 'prova',
        'prova2', 'Space_Debris', 'prova', 'prova2', 'SARDA_14']
    outputs = list(zip(out_boards, out_dbe))
    out_att = [11, 3, 2, 1, 8, 1, 5, 16, 7]
    atts_in_boards = list(zip(out_boards, out_att))

    def __init__(self):
        self.msg = ''

        # Status -1 -> board not available
        self.boards = [
            {
                'Address': '3',
                "Status": 0,
                "Configuration": "default",
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
                "EQ": [1, 1, 1, 1, 0, 0, 0, 0, 0, 1],
                "BPF": [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
                "5V": 1.11,
                "3V3": 0.11,
                "T0": 05.10,
                "FIRM": "0.116_NEW_win"
            },
            {
                'Address': '2',
                "Status": 0,
                "Configuration": "default",
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                "EQ": [1, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                "BPF": [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                "5V": 0.00,
                "3V3": 0.01,
                "T0": 50.51,
                "FIRM": "0.116_NEW_win"
            },
            {
                'Address': '1',
                "Status": 0,
                "Configuration": "default",
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                "EQ": [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                "BPF": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                "5V": 1.00,
                "3V3": 0.10,
                "T0": 15.50,
                "FIRM": "0.116_NEW_win"
            },
            {
                'Address': '0',
                "Status": 0,
                "Configuration": "default",
                "REG": self._init_reg(),
                "ATT": self._init_att(),
                "AMP": [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                "EQ": [0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
                "BPF": [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
                "5V": 0.01,
                "3V3": 1.00,
                "T0": 05.05,
                "FIRM": "0.116_NEW_win"
            },
        ]

    def _init_reg(self):
        reg = random.sample(range(0, 255), 10)
        return reg

    def _init_att(self):
        att = [round(elem * 2) / 2 for elem
               in numpy.random.uniform(0.0, 31.5, 17)]
        return att

    def parse(self, byte):
        print(byte)
        if byte == self.tail:
            msg = self.msg[:-1]
            self.msg = ''
            return self._execute(msg)
        self.msg += byte

        return True

    def _execute(self, msg):
        """This method parses and executes a command the moment it is
        completely received.

        :param msg: the received command, comprehensive of its header and tail.
        """
        print(msg)
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

        for param in args:
            params.append(param)

        return cmd(params)

    def _set_allmode(self, params):
        retval = ''
        if len(params) != 2:
            return self._error(params[0], 1001)
        elif params[1] not in self.obs_mode:
            return self._error(params[0], 1003)
        for key in self.boards:
            if key['Status'] != 0:
                retval += f'BOARD {key["Address"]} ERR DBE BOARD unreachable\n'
            else:
                key["Configuration"] = params[1]
                retval += f'BOARD {key["Address"]} ACK\n'
        return retval[:-1] + '\x0D\x0A'

    def _set_mode(self, params):
        if len(params) != 4 or params[1] != 'BOARD':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[2])), None)
        except ValueError:
            return self._error(params[0], 1001)

        if selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif params[3] not in self.obs_mode:
            return self._error(params[0], 1003)
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        else:
            selected_board["Configuration"] = params[3]
            return self.ack + '\x0D\x0A'

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
            return self.ack + '\x0D\x0A'

    def _delete_file(self, params):
        if len(params) != 2:
            return self._error(params[0], 1001)
        elif params[1] not in self.obs_mode:
            return self._error(params[0], 1003)
        else:
            self.obs_mode.remove(params[1])
            return self.ack + '\x0D\x0A'

    def _get_status(self, params):
        if len(params) != 3 or params[1] != 'BOARD':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[2])), None)
        except ValueError:
            return self._error(params[0], 1001)

        if selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        retval = self.ack + '\n'
        retval += f'BOARD {selected_board["Address"]}\n\n'
        retval += f'REG=[ {" ".join(map(str,selected_board["REG"]))} ]\n\n'
        retval += f'ATT=[ {"  ".join(map(str,selected_board["ATT"])) } ]'
        return retval + '\x0D\x0A'

    def _set_att(self, params):
        if len(params) != 6 or params[2] != 'BOARD' or params[4] != 'VALUE':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[3])), None)
            if selected_board is None:
                return self._error(params[0], 1007, params[3])
            elif int(params[1]) not in list(range(0, 17)):
                return self._error(params[0], 1010, params[1])
            elif float(params[5]) not in list(numpy.arange(0, 32, 0.5)):
                return self._error(params[0], 1011, selected_board["Address"])
            elif selected_board["Status"] != 0:
                return self._error(params[0], 1005, params[3])
            else:
                selected_board["ATT"][int(params[1])] = float(params[5])
                return self.ack + '\x0D\x0A'
        except ValueError:
            return self._error(params[0], 1001)

    def _set_amp(self, params):
        if len(params) != 6 or params[2] != 'BOARD' or params[4] != 'VALUE':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[3])), None)
            if selected_board is None:
                return self._error(params[0], 1007, params[3])
            elif int(params[1]) not in list(range(1, 11)):
                return self._error(params[0], 1012, params[1])
            elif float(params[5]) not in [0, 1]:
                return self._error(params[0], 1011, selected_board["Address"])
            elif selected_board["Status"] != 0:
                return self._error(params[0], 1005, params[3])
            else:
                selected_board["AMP"][int(params[1]) - 1] = params[5]
                return self.ack + '\x0D\x0A'
        except ValueError:
            return self._error(params[0], 1001)

    def _set_eq(self, params):
        if len(params) != 6 or params[2] != 'BOARD' or params[4] != 'VALUE':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[3])), None)
            if selected_board is None:
                return self._error(params[0], 1007, params[3])
            elif int(params[1]) not in list(range(1, 11)):
                return self._error(params[0], 1013, params[1])
            elif float(params[5]) not in [0, 1]:
                return self._error(params[0], 1011, selected_board["Address"])
            elif selected_board["Status"] != 0:
                return self._error(params[0], 1005, params[3])
            else:
                selected_board["EQ"][int(params[1]) - 1] = params[5]
                return self.ack + '\x0D\x0A'
        except ValueError:
            return self._error(params[0], 1001)

    def _set_bpf(self, params):
        channels = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '1a', '1b']
        if len(params) != 6 or params[2] != 'BOARD' or params[4] != 'VALUE':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[3])), None)
            if selected_board is None:
                return self._error(params[0], 1007, params[3])
            elif params[1] not in channels:  # accept 1, 1a NOT a1, 1aa, a, 1a2
                chars = 0
                for char in params[1]:
                    if char.isalpha():
                        chars += 1
                if params[1][0].isalpha() or chars > 1:
                    return self._error(params[0], 1001)
                elif not params[1].isnumeric():
                    if params[1][-1].isalpha():
                        return self._error(params[0], 1014, params[1])
                    else:
                        return self._error(params[0], 1001)
                else:
                    return self._error(params[0], 1014, params[1])
            elif float(params[5]) not in [0, 1]:
                return self._error(params[0], 1011, selected_board["Address"])
            elif selected_board["Status"] != 0:
                return self._error(params[0], 1005, params[3])
            else:
                channel = -1
                if params[1] == '1a':
                    channel = 0
                elif params[1] == '1b':
                    channel = 1
                else:
                    channel = int(params[1])
                selected_board["BPF"][channel] = params[5]
                return self.ack + '\x0D\x0A'
        except ValueError:
            return self._error(params[0], 1001)

    def _all_diag(self, params):
        retval = ''
        if len(params) != 1:
            return self._error(params[0], 1001)
        else:
            for board in self.boards:
                retval += f'BOARD {board["Address"]} '
                if board['Status'] == 0:
                    retval += self.ack + '\n'
                    retval += f'5V {board["5V"]} 3V3 {board["3V3"]}\n'
                    retval += f'T0 {board["T0"]}\n\n'
                else:
                    retval += 'ERR DBE BOARD unreachable\n\n'
            return retval[:-2] + '\x0D\x0A'

    def _diag(self, params):
        if len(params) != 3 or params[1] != 'BOARD':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[2])), None)
        except ValueError:
            return self._error(params[0], 1001)

        if selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        else:
            retval = self.ack + '\n'
            retval += f'BOARD {selected_board["Address"]}\n\n'
            retval += f'5V {selected_board["5V"]}'
            retval += f' 3V3 {selected_board["3V3"]}\n'
            retval += f'T0 {selected_board["T0"]}'
        return retval + '\x0D\x0A'

    def _set_status(self, params):
        if len(params) != 5:
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                              if int(sub['Address']) == int(params[2])), None)

            if selected_board is None:
                return self._error(params[0], 1007, params[2])
            else:
                selected_board["Status"] = int(params[4])
                return self.ack + '\x0D\x0A'
        except ValueError:
            return self._error(params[0], 1001)

    def _get_comp(self, params):
        if len(params) != 3 or params[1] != 'BOARD':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                              if int(sub['Address']) == int(params[2])), None)
        except ValueError:
            return self._error(params[0], 1001)

        if selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        else:
            retval = 'ACK\n'
            retval += f'BOARD {params[2]}\n\n'
            retval += f'AMP=[ {" ".join(map(str,selected_board["AMP"]))} ]\n'
            retval += f'EQ=[ {" ".join(map(str,selected_board["EQ"]))} ]\n'
            retval += f'BPF=[ {" ".join(map(str,selected_board["BPF"])) } ]'
            return retval + '\x0D\x0A'

    def _get_cfg(self, params):
        retval = ''
        if len(params) != 1:
            return self._error(params[0], 1001)
        else:
            retval += self.ack + '\n'
            for board in self.boards:
                retval += f'BOARD {board["Address"]} '
                if board['Status'] == 0:
                    retval += f'{board["Configuration"]}\n\n'
                else:
                    retval += 'ERR DBE BOARD unreachable\n\n'
        return retval[:-2] + '\x0D\x0A'

    def _set_dbeatt(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 3:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.atts_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["ATT"])
                print(board["ATT"][a[out_idx[b_idx]]])
                if ((params[2] == '+3' or params[2] == '-3') and
                        not (0 <= (float(board["ATT"][a[out_idx[b_idx]]]) +
                        float(params[2])) <= 31.5)):
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} value out of range\n')
                elif (params[2] != '+3' and params[2] != '-3'
                        and float(params[2]) not in
                        list(numpy.arange(0, 32, 0.5))):
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} value out of range\n')
                elif board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    if params[2] == '+3' or params[2] == '-3':
                        board["ATT"][a[out_idx[b_idx]]] += float(params[2])
                    else:
                        board["ATT"][a[out_idx[b_idx]]] = float(params[2])
                    retval += f'DBE {params[1]} BOARD {board["Address"]} ACK\n'
        return retval[:-1] + '\x0D\x0A'

    def _get_dbeatt(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 2:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.atts_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["ATT"])
                print(board["ATT"][a[out_idx[b_idx]]])

                if board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    retval += (f'ACK {params[1]} BOARD {board["Address"]} '
                    f'ATT {a[out_idx[b_idx]]} VALUE '
                    f'{board["ATT"][a[out_idx[b_idx]]]}\n')
        return retval[:-1] + '\x0D\x0A'

    def _get_firm(self, params):
        if len(params) != 3 or params[1] != 'BOARD':
            return self._error(params[0], 1001)
        try:
            selected_board = next((sub for sub in self.boards
                               if int(sub['Address']) == int(params[2])), None)
        except ValueError:
            return self._error(params[0], 1001)

        if selected_board is None:
            return self._error(params[0], 1007, params[2])
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005, params[2])
        else:
            retval = self.ack + '\n'
            retval += f'BOARD {selected_board["Address"]} '
            retval += f'Prog=DBESM, Rev=rev {selected_board["FIRM"]}'
        return retval + '\x0D\x0A'

    def _set_dbeamp(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 3:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.amps_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["AMP"])
                print(board["AMP"][a[out_idx[b_idx]]])
                if (float(params[2]) not in [0,1]):
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} value out of range\n')
                elif board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    board["AMP"][a[out_idx[b_idx]]] = float(params[2])
                    retval += f'DBE {params[1]} BOARD {board["Address"]} ACK\n'
        return retval[:-1] + '\x0D\x0A'

    def _get_dbeamp(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 2:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.amps_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["AMP"])
                print(board["AMP"][a[out_idx[b_idx]]])

                if board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    retval += (f'ACK {params[1]} BOARD {board["Address"]} '
                    f'AMP {a[out_idx[b_idx]]} VALUE '
                    f'{board["AMP"][a[out_idx[b_idx]]]}\n')
        return retval[:-1] + '\x0D\x0A'


    def _set_dbeeq(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 3:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.eqs_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["EQ"])
                print(board["EQ"][a[out_idx[b_idx]]])
                if (float(params[2]) not in [0,1]):
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} value out of range\n')
                elif board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    board["EQ"][a[out_idx[b_idx]]] = float(params[2])
                    retval += f'DBE {params[1]} BOARD {board["Address"]} ACK\n'
        return retval[:-1] + '\x0D\x0A'

    def _get_dbeeq(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 2:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.eqs_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["EQ"])
                print(board["EQ"][a[out_idx[b_idx]]])

                if board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    retval += (f'ACK {params[1]} BOARD {board["Address"]} '
                    f'EQ {a[out_idx[b_idx]]} VALUE '
                    f'{board["EQ"][a[out_idx[b_idx]]]}\n')
        return retval[:-1] + '\x0D\x0A'


    def _set_dbebpf(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 3:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.bpfs_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["BPF"])
                print(board["BPF"][a[out_idx[b_idx]]])
                if (float(params[2]) not in [0,1]):
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} value out of range\n')
                elif board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    board["BPF"][a[out_idx[b_idx]]] = float(params[2])
                    retval += f'DBE {params[1]} BOARD {board["Address"]} ACK\n'
        return retval[:-1] + '\x0D\x0A'

    def _get_dbebpf(self, params):
        retval = ''
        boardx = {}
        selected_boards = []
        out_idx = []
        if len(params) != 2:
            return self._error(params[0], 1001)
        b, d = zip(*self.outputs)
        for i, v in enumerate(d):
            if v == params[1]:
                out_idx.append(i)
                boardx = next((sub for sub in self.boards
                        if int(sub['Address']) == int(b[i])), None)
                selected_boards.append(boardx)
        if len(selected_boards) == 0:
            return self._error(params[0], 1015)
        else:
            brd, a = zip(*self.bpfs_in_boards)
            for board in selected_boards:
                b_idx = selected_boards.index(board)
                print(brd)
                print(board["BPF"])
                print(board["BPF"][a[out_idx[b_idx]]])

                if board["Status"] != 0:
                    retval += (f'ERR DBE {params[1]} BOARD '
                    f'{board["Address"]} unreachable\n')
                else:
                    retval += (f'ACK {params[1]} BOARD {board["Address"]} '
                    f'BPF {a[out_idx[b_idx]]} VALUE '
                    f'{board["BPF"][a[out_idx[b_idx]]]}\n')
        return retval[:-1] + '\x0D\x0A'

    def _error(self, device_code, error_code, board_address=None):
        error_string = self.errors.get(error_code)
        if error_code == 1001:
            retval = f'NAK {error_string}'
        elif error_code in [1005, 1007, 1010, 1011, 1012, 1013, 1014]:
            device_string = self.devices.get(device_code)
            retval = f'ERR {device_string} '\
                f'{error_string.replace("X", board_address)}'
        else:
            device_string = self.devices.get(device_code)
            retval = f'ERR {device_string} {error_string}'
        return retval + '\x0D\x0A'
