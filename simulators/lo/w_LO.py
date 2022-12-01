from simulators.common import ListeningSystem


class System(ListeningSystem):

    commands = {
        'set W_LO_freq_PolH': 'set_w_LO_freq_PolH',
        'set W_LO_freq_PolV': 'set_w_LO_freq_PolV',
        'get W_LO_PolH': 'get_w_LO_PolH',
        'get W_LO_PolV': 'get_w_LO_PolV',
        'get W_LO': 'get_w_LO',
        'get W_LO_status': 'get_w_LO_status',
        'set LO_att_PolH': 'set_LO_att_PolH',
        'set LO_att_PolV': 'set_LO_att_PolV',
        'get LO_att_PolH': 'get_LO_att_PolH',
        'get LO_att_PolV': 'get_LO_att_PolV',
        'get LO_att': 'get_LO_att',
    }

    tail = '\r\n'

    def __init__(self):
        self.status_W_LO_PolH = "Unlocked"
        self.status_W_LO_PolV = "Unlocked"
        self.w_lo_freq_polH = 0.0
        self.w_lo_freq_polV = 0.0
        self.lo_att_polH = 0.0
        self.lo_att_polV = 0.0
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
            args = command.split('=')
            if len(args) >= 2:  # set methods
                cmd_name = self.commands.get(args[0])
                method = getattr(self, cmd_name)
                ans = method(float(args[1]))
            else:  # get methods (without params)
                cmd_name = self.commands.get(args[0][:-1])
                method = getattr(self, cmd_name)
                ans = method()
            if isinstance(ans, str):
                answer += ans + ';'
        answer = answer[:-1]
        return answer

    def set_w_LO_freq_PolH(self, params):
        self.w_lo_freq_polH = params
        return f'W_LO_freq_PolH={self.w_lo_freq_polH} Mhz'

    def set_w_LO_freq_PolV(self, params):
        self.w_lo_freq_polV = params
        return f'W_LO_freq_PolV={self.w_lo_freq_polV} Mhz'

    def get_w_LO_PolH(self):
        return f'W_LO_freq_PolH={self.w_lo_freq_polH} Mhz'

    def get_w_LO_PolV(self):
        return f'W_LO_freq_PolV={self.w_lo_freq_polV} Mhz'

    def get_w_LO(self):
        return (f'W_LO_freq_PolH={self.w_lo_freq_polH} Mhz,'
        f'\n W_LO_freq_PolV={self.w_lo_freq_polV} Mhz')

    def get_w_LO_status(self):
        return (f'W_LO_PolH={self.status_W_LO_PolH} Mhz'
        f'\nW_LO_PolV={self.status_W_LO_PolV} Mhz')

    def set_LO_att_PolH(self, params):
        self.lo_att_polH = params
        return f'LO_att_PolH={self.lo_att_polH}'

    def set_LO_att_PolV(self, params):
        self.lo_att_polV = params
        return f'LO_att_PolV={self.lo_att_polV}'

    def get_LO_att_PolH(self):
        return f'LO_att_PolH={self.lo_att_polH}'

    def get_LO_att_PolV(self):
        return f'LO_att_PolV={self.lo_att_polV}'

    def get_LO_att(self):
        return (f'LO_att_PolH={self.lo_att_polH},'
        f'\nLO_att_PolV={self.lo_att_polV}')
