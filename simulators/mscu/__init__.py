# Authors:
#   Marco Buttu <marco.buttu@inaf.it>
#   Giuseppe Carboni <giuseppe.carboni@inaf.it>
from multiprocessing import Value
from SocketServer import ThreadingTCPServer
from simulators.common import ListeningSystem
from simulators.mscu.servo import Servo
from simulators.mscu.parameters import headers, closers, app_nr

servers = [(('0.0.0.0', 10000), (), ThreadingTCPServer, ())]


class System(ListeningSystem):

    def __init__(self):
        self.servos = {}
        for address in app_nr:
            self.servos[address] = Servo(address)
        self.setpos_NAK = [Value('i', False)] * len(app_nr)
        self._set_default()

    def __del__(self):
        self.system_stop()

    def system_stop(self):
        for servo in self.servos.values():
            servo.stop()
        return '$server_shutdown%'

    def system_setpos_NAK(self):
        self.setpos_NAK[1].value = True  # The SRP address

    def system_setpos_ACK(self):
        self.setpos_NAK[1].value = False  # The SRP address

    def _set_default(self):
        self.msg = ''

    def parse(self, byte):
        self.msg = byte if byte in headers else self.msg + byte
        if self.msg.startswith(headers):
            if self.msg.endswith(closers):
                msg = self.msg
                self._set_default()
                return self._parse(msg)
            else:
                return True
        else:
            self._set_default()
            return False

    def _parse(self, msg):
        try:
            # Retrieve the message header
            body = msg[1:].rstrip()
            whole_cmd, params_str = body.split('=')
            # Retrieve the command and the command number
            cmd, cmd_num = whole_cmd.split(':')
            cmd_num = int(cmd_num)
            # Retrieve the command parameters
            all_params = []
            for param in params_str.split(','):
                param = param.strip()
                if 'x' in param:
                    param = int(param, 16)
                elif '.' in param:
                    param = float(param)
                else:
                    param = int(param.strip())
                all_params.append(param)
            address, params = all_params[0], all_params[1:]
        except Exception:
            raise ValueError("Invalid message: %s" % msg)

        servo = self.servos[address]
        if self.setpos_NAK[address].value:
            servo.setpos_NAK = True
        else:
            servo.setpos_NAK = False

        try:
            method = getattr(servo, cmd)
        except AttributeError:
            # Print a general error message if we received an unknown command
            raise ValueError('Command %s unknown!' % cmd)

        # Call the appropriate command whose name is the string cmd
        answers = method(cmd_num, *params)
        return ''.join(answers)
