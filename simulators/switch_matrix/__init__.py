# Author:
#   Lorenzo Monti <lorenzo.monti@inaf.it>
import re
from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem

servers = [
    (('0.0.0.0', 13200), (), ThreadingTCPServer, {}),
]


class System(ListeningSystem):

    commands = {
        'set IF_switch_config': 'set_IF_switch_config',
        'get IF_switch_config': 'get_IF_switch_config',
    }

    tail = '\r\n'
    ack = 'ack'
    nack = 'nack'

    def __init__(self):
        self._set_default()
        self.sw_matrix = SwitchMatrix()

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
        commandList = msg.replace("\r", "").split(';')
        answer = ''
        for command in commandList:
            args = re.split(r'\W+', command)
            if len(args) < 2:
                continue
            cmd_name = self.commands.get(args[0] + " " + args[1])
            if len(args) > 2:  # set methods
                answer = getattr(self, cmd_name)(args[2])
                return answer
            method = getattr(self, cmd_name)  # get methods
            ans = method()
            if isinstance(ans, str):
                answer += ans + ';'
        if answer:
            answer = answer[:-1]
            return answer
        else:
            return True

    def set_IF_switch_config(self, params):
        self.sw_matrix.switch_matrix = int(params)
        return self.ack + self.tail

    def get_IF_switch_config(self):
        return self.sw_matrix.switch_matrix


class SwitchMatrix:

    def __init__(self):
        self._switch_matrix = 1
        self._matrix = {
            1: [False, True, False, "H LSB", "H USB", "HBS"],
            2: [False, False, True, "V LSB", "V USB", "VBS"],
            3: [True, True, False, "H LSB", "V LSB", "LBP"],
            4: [True, False, True, "H USB", "V USB", "UBP"],
        }

    @property
    def switch_matrix(self):
        return f'{self._switch_matrix}:{self._matrix[self._switch_matrix][-1]}'

    @switch_matrix.setter
    def switch_matrix(self, value):
        self._switch_matrix = value
