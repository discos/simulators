from simulators.common import ListeningSystem


class System(ListeningSystem):

    commands = {
        'POWER': 'setPower',
        'POWER?': 'getPower',
        'FREQ': 'setFrequency',
        'FREQ?': 'getFrequency',
        'OUTP:STAT': 'setRf',
        'OUTP:STAT?': 'getRf',
        'SYST:ERR?': 'readStatus'
    }

    status = '0,\"No error\"'

    def __init__(self):
        self.power = 0
        self.frequency = 0.0
        self.rf_status = False  # Start as off
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
            if len(args) < 1:
                continue
            cmd_name = self.commands.get(args[0])
            if not cmd_name:
                continue
            method = getattr(self, cmd_name)
            ans = method(args[1:])
            if isinstance(ans, str):
                answer += ans + ';'
        if answer:
            answer = answer[:-1]
            answer += '\n'
            return answer
        else:
            return True

    def setPower(self, params):
        # 'POWER <power> dBm\n'
        if len(params) != 2:
            return False
        elif params[1] != 'dBm':
            return False
        try:
            self.power = int(params[0])
            return True
        except ValueError:
            return False

    def getPower(self, _):
        # 'POWER?\n'
        return str(self.power)

    def setFrequency(self, params):
        # 'FREQ <frequency> MHZ\n'
        if len(params) != 2:
            return False
        elif params[1] != 'MHZ':
            return False
        try:
            self.frequency = float(params[0])
            return True
        except ValueError:
            return False

    def getFrequency(self, _):
        # 'FREQ?\n'
        return str(int(self.frequency) * 1000000)

    def setRf(self, params):
        # 'OUTP:STAT ON\n'
        # 'OUTP:STAT OFF\n'
        if len(params) != 1:
            return False
        elif params[0] != 'ON' and params[0] != 'OFF':
            return False
        self.rf_status = params[0] == 'ON'
        return True

    def getRf(self, _):
        # 'OUTP:STAT?\n'
        return str(int(self.rf_status))

    def readStatus(self, _):
        # 'SYST:ERR?\n'
        return self.status
