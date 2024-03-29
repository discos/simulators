# Author:
#   Lorenzo Monti <lorenzo.monti@inaf.it>
from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem

servers = [
    (('0.0.0.0', 13100), (), ThreadingTCPServer, {}),
]


class System(ListeningSystem):

    commands = {
        'set W_home': 'set_w_home',
        'set W_solar_attn': 'set_w_solar_attn',
        'set W_cal': 'set_w_cal',
        'set W_passthrough': 'set_w_passthrough',
        'get W_mode': 'get_w_mod',
    }

    tail = '\r\n'
    ack = 'ACK'
    nack = 'NACK'

    def __init__(self):
        self.mode = ""
        self.home = 1
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

    def set_w_home(self):
        self.home = 1
        return self.ack + self.tail

    def set_w_solar_attn(self):
        self.mode = "Attenuator"
        return self.ack + self.tail

    def set_w_cal(self):
        self.mode = "Calibrator"
        return self.ack + self.tail

    def set_w_passthrough(self):
        self.mode = "Pass-through"
        return self.ack + self.tail

    def get_w_mod(self):
        return self.mode + self.tail
