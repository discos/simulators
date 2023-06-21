from simulators.common import ListeningSystem


class System(ListeningSystem):

    commands = {
        'enable USB_devs': 'enable_USB_devs',
        'disable USB_devs': 'disable_USB_devs',
        'set W_LO_freq_PolH': 'set_w_LO_freq_PolH',
        'set W_LO_freq_PolV': 'set_w_LO_freq_PolV',
        'get W_LO_PolH': 'get_w_LO_PolH',
        'get W_LO_PolV': 'get_w_LO_PolV',
        'get W_LO_Pols': 'get_w_LO_Pols',
        'get W_LO_Synths_Temp': 'get_w_LO_Synths_Temp',
        'get W_LO_HKP_Temp': 'get_w_LO_HKP_Temp',
        'set W_LO_RefH': 'set_W_LO_RefH',
        'set W_LO_RefV': 'set_W_LO_RefV',
        'get W_LO_RefH': 'get_W_LO_RefH',
        'get W_LO_RefV': 'get_W_LO_RefV',
        'get W_LO_status': 'get_w_LO_status',
        'set LO_att_PolH': 'set_LO_att_PolH',
        'set LO_att_PolV': 'set_LO_att_PolV',
        'get LO_att_PolH': 'get_LO_att_PolH',
        'get LO_att_PolV': 'get_LO_att_PolV',
        'get LO_atts': 'get_LO_atts',
    }

    tail = '\r\n'
    ack = 'ACK'
    nack = 'NACK'

    def __init__(self):
        self.w_USB_devs = 0
        self.w_LO_Synths_Temp = [0., 0.]
        self.w_LO_HKP_Temp = [0., 0., 0., 0.]
        self.w_LO_refH = ''
        self.w_LO_refV = ''
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
                try:
                    ans = method(float(args[1]))
                except ValueError:
                    ans = method(args[1][:-1])
            else:  # get methods (without params)
                cmd_name = self.commands.get(args[0][:-1])
                method = getattr(self, cmd_name)
                ans = method()
            if isinstance(ans, str):
                answer += ans + ';'
        answer = answer[:-1]
        return answer

    def enable_USB_devs(self):
        self.w_USB_devs = 1
        return self.ack + self.tail

    def disable_USB_devs(self):
        self.w_USB_devs = 0
        return self.ack + self.tail

    def set_w_LO_freq_PolH(self, params):
        self.w_lo_freq_polH = params
        return self.ack + self.tail

    def set_w_LO_freq_PolV(self, params):
        self.w_lo_freq_polV = params
        return self.ack + self.tail

    def get_w_LO_PolH(self):
        return f'{self.w_lo_freq_polH}MHz' + self.tail

    def get_w_LO_PolV(self):
        return f'{self.w_lo_freq_polV}MHz' + self.tail

    def get_w_LO_Pols(self):
        return (f'{self.w_lo_freq_polH}MHz,'
        f'{self.w_lo_freq_polV}MHz' + self.tail)

    def get_w_LO_Synths_Temp(self):
        return (f'{self.w_LO_Synths_Temp[0]}C,'
        f'{self.w_LO_Synths_Temp[1]}C' + self.tail)

    def get_w_LO_HKP_Temp(self):
        return (f'{self.w_LO_HKP_Temp[0]}C,'
        f'{self.w_LO_HKP_Temp[1]}C' f'{self.w_LO_HKP_Temp[2]}C'
        f'{self.w_LO_HKP_Temp[3]}C' + self.tail)

    def set_W_LO_RefH(self, params):
        self.w_LO_refH = params
        return self.ack + self.tail

    def set_W_LO_RefV(self, params):
        self.w_LO_refV = params
        return self.ack + self.tail

    def get_W_LO_RefH(self):
        return f'{self.w_LO_refH.capitalize()}.{self.tail}'

    def get_W_LO_RefV(self):
        return f'{self.w_LO_refV.capitalize()}.{self.tail}'

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
        return f'{self.lo_att_polH}dB' + self.tail

    def get_LO_att_PolV(self):
        return f'{self.lo_att_polV}dB' + self.tail

    def get_LO_atts(self):
        return (f'{self.lo_att_polH}dB,'
        f'{self.lo_att_polV}dB' + self.tail)
