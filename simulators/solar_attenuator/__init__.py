# Author:
#   Lorenzo Monti <lorenzo.monti@inaf.it>
from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem

servers = [
    (('0.0.0.0', 13100), (), ThreadingTCPServer, {}),
]


class System(ListeningSystem):

    commands = {
        'set W_solar_attn': 'set_w_solar_attn',
        'set W_cal': 'set_w_cal',
        'set W_passthrough': 'set_w_passthrough',
        'get W_cal_temp': 'get_w_cal_temp',
        'get W_mode': 'get_w_mod',
    }

    tail = '\r\n'

    def __init__(self):
        self.mode = ""
        self.cal_temp = 21.0
        self._set_default()

    def _set_default(self):
        self.msg = ''

    def parse(self, byte):
        if byte == '\n':  # Ending char
            msg = self.msg
            self._set_default()
            return self._parse(msg)
        else:
            self.msg += byte
            return True

    def _parse(self, msg):
        commandList = msg.split(';')
        answer = ''
        for command in commandList:
            args = command.split()
            if len(args) < 2:
                continue
            cmd_name = self.commands.get(args[0] + " " + args[1])
            method = getattr(self, cmd_name)
            ans = method()
            if isinstance(ans, str):
                answer += ans + ';'
        if answer:
            answer = answer[:-1]
            return answer
        else:
            return True

    def set_w_solar_attn(self):
        self.mode = "attenuator"
        return self.mode + self.tail

    def set_w_cal(self):
        self.mode = "calibrator"
        return self.mode + self.tail

    def set_w_passthrough(self):
        self.mode = "pass-through"
        return self.mode + self.tail

    def get_w_cal_temp(self):
        return str(self.cal_temp) + self.tail

    def get_w_mod(self):
        return self.mode + self.tail
