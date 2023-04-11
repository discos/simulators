from socketserver import ThreadingTCPServer
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
        'DBE STOREALLMODE': '_not_implemented',
        'DBE CLRMODE': '_not_implemented',
        'DBE STATUS': '_not_implemented',
        'DBE DIAG': '_not_implemented',
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
        1007: 'BOARD not existing',
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
    
        # -1 -> board not available  
        self.boards =[
            {'Address': '12', "Status":-1},
            {'Address': '13', "Status": 0},
            {'Address': '14', "Status": 0},
            {'Address': '15', "Status":-1},
        ]
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
            return self._error(-1,1001)
        
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
        err=[]
        if len(params) != 2:
            return self._error(params[0], 1001)
        elif params[1] not in self.obs_mode:
            return self._error(params[0], 1003)
        for key in self.boards:
            if key['Status']!=0:
                err.append(key['Address'])
        if len(err)>0:
            if len(err)==1:
                return self._error(params[0], 1005, err[0])
            else:
                return self._error(params[0], 1005,' '.join(map(str, err)))

        else:
            return self.ack

    def _set_mode(self, params):
        selected_board = next((sub for sub in self.boards if sub['Address'] == params [2]), None)
        if len(params) != 4:
            return self._error(params[0], 1001)
        elif selected_board == None:
            return self._error(params[0], 1007)
        elif params[3] not in self.obs_mode:
            return self._error(params[0], 1003)
        elif selected_board["Status"] != 0:
            return self._error(params[0], 1005,params[2])
        else:
            return self.ack


    def _not_implemented(self, params):
        return self._error(params[0], 9999)

    def _error(self, device_code, error_code,board_address=None):
        error_string = self.errors.get(error_code)
        if error_code == 1001:
            retval = f'NAK {error_string}\x0A'
        elif error_code == 1005:
            device_string = self.devices.get(device_code)
            retval = f'ERR {device_string} {error_string.replace("X",board_address)}{self.tail}\x0A'
        else:
            device_string = self.devices.get(device_code)
            retval = f'ERR {device_string} {error_string}{self.tail}\x0A'
        return retval
