# Authors:
#   Marco Buttu <marco.buttu@inaf.it>
#   Giuseppe Carboni <giuseppe.carboni@inaf.it>
from multiprocessing import Value
from SocketServer import ThreadingTCPServer
from simulators.common import ListeningSystem
from simulators.mscu import servo
from simulators.mscu.parameters import headers, closers, app_nr

servers = [(('0.0.0.0', 10000), (), ThreadingTCPServer, ())]


class System(ListeningSystem):

    def __init__(self):
        self.servos = {}
        for address in app_nr:
            self.servos[address] = servo.Servo(address)
        self.setpos_NAK = [Value('i', False)] * len(app_nr)
        self._set_default()

    def __del__(self):
        self.system_stop()

    def system_stop(self):
        for servo in self.servos.values():
            servo.stop()
        return '$server_shutdown%'

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
            header, body = msg[0], msg[1:].rstrip()
            whole_cmd, params_str = body.split('=')
            # Retrieve the command and the command number
            cmd, cmd_num = whole_cmd.split(':')
            cmd_num = int(cmd_num)
            # Retrieve the command parameters
            all_params = [eval(param.strip()) for param in params_str.split(',')]
            address, params = all_params[0], all_params[1:]
        except Exception:
            raise ValueError("Invalid message: %s" % msg)

        srvo = self.servos[address]
        if self.setpos_NAK[address].value:
            srvo.setpos_NAK = True
        else:
            srvo.setpos_NAK = False
        # Print a general error message if we received an invalid command
        if header not in headers or not hasattr(srvo, cmd):
            raise ValueError("Invalid message: %s" % msg)

        method = getattr(srvo, cmd)
        if not method:
            raise ValueError('Command %s unknown!' % cmd)

        # Call the appropriate command whose name is the string cmd
        answers = method(cmd_num, *params)
        return ''.join(answers)

    def system_setpos_NAK(self):
        self.setpos_NAK[1].value = True  # The SRP address

    def system_setpos_ACK(self):
        self.setpos_NAK[1].value = False  # The SRP address
