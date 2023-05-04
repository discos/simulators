from simulators.common import ListeningSystem


class System(ListeningSystem):

    commands = {
        'enable W_LO_Inter': 'enable_w_LO_Inter',
        'disable W_LO_Inter': 'disable_w_LO_Inter',
        'set W_LO_freq_PolH': 'set_w_LO_freq_PolH',
        'set W_LO_freq_PolV': 'set_w_LO_freq_PolV',
        'get W_LO_PolH': 'get_w_LO_PolH',
        'get W_LO_PolV': 'get_w_LO_PolV',
        'get W_LO_Pols': 'get_w_LO_Pols',
        'get W_LO_Synths_Temp': 'get_w_LO_Synths_Temp',
        'get W_LO_HKP_Temp': 'get_w_LO_HKP_Temp',
        'get W_LO_status': 'get_w_LO_status',
        'set LO_att_PolH': 'set_LO_att_PolH',
        'set LO_att_PolV': 'set_LO_att_PolV',
        'get LO_att_PolH': 'get_LO_att_PolH',
        'get LO_att_PolV': 'get_LO_att_PolV',
        'get LO_atts': 'get_LO_atts',
    }

    tail = '\r\n'
    ack = 'ack'
    nack = 'nack'

    def __init__(self):
        self.w_LO_Inter = 0
        self.w_LO_Synths_Temp = [0., 0.]
        self.w_LO_HKP_Temp = [0., 0., 0., 0.]
        self.status_W_LO_PolH = 0
        self.status_W_LO_PolV = 0
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

    def enable_w_LO_Inter(self):
        self.w_LO_Inter = 1
        return self.ack + self.tail

    def disable_w_LO_Inter(self):
        self.w_LO_Inter = 0
        return self.ack + self.tail

    def set_w_LO_freq_PolH(self, params):
        self.w_lo_freq_polH = params
        return self.ack + self.tail

    def set_w_LO_freq_PolV(self, params):
        self.w_lo_freq_polV = params
        return self.ack + self.tail

    def get_w_LO_PolH(self):
        return f'{self.w_lo_freq_polH}' + self.tail

    def get_w_LO_PolV(self):
        return f'{self.w_lo_freq_polV}' + self.tail

    def get_w_LO_Pols(self):
        return (f'{self.w_lo_freq_polH},'
        f'{self.w_lo_freq_polV}' + self.tail)

    def get_w_LO_Synths_Temp(self):
        return (f'C1={self.w_LO_Synths_Temp[0]},'
        f'C2={self.w_LO_Synths_Temp[1]}' + self.tail)

    def get_w_LO_HKP_Temp(self):
        return (f'C1={self.w_LO_HKP_Temp[0]},'
        f'C2={self.w_LO_HKP_Temp[1]}' f'C3={self.w_LO_HKP_Temp[2]}'
        f'C4={self.w_LO_HKP_Temp[3]}' + self.tail)

    def get_w_LO_status(self):
        return (f'{self.status_W_LO_PolH},'
        f'{self.status_W_LO_PolV}' + self.tail)

    def set_LO_att_PolH(self, params):
        self.lo_att_polH = params
        return self.ack + self.tail

    def set_LO_att_PolV(self, params):
        self.lo_att_polV = params
        return self.ack + self.tail

    def get_LO_att_PolH(self):
        return f'{self.lo_att_polH}' + self.tail

    def get_LO_att_PolV(self):
        return f'{self.lo_att_polV}' + self.tail

    def get_LO_atts(self):
        return (f'{self.lo_att_polH},'
        f'{self.lo_att_polV}' + self.tail)
