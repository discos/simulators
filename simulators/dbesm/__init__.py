import codecs
from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem


servers = [(('0.0.0.0', 11111), (), ThreadingTCPServer, {})]


class System(ListeningSystem):
    # tail = ['\x0A', '\x0D']  # NEWLINE and CR
    header = '#'
    tail = '\x0D'
    ack = 'ack\x0D'
    nak = 'nak\x0D'
    max_msg_length = 15

    commands = {
        'ALLMODE': '_set_allmode',
    }

    errors = {
        1000: 'ERROR_ARGS_NOT_VALID',
        1001: 'ERROR_COMMAND_UNKNOWN',
    }

    def __init__(self):
        self.msg = ''
        self.cmd_id = ''
    
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
        print ("aaa")
        args = [x.strip() for x in msg.split(' ')]
        print (args)
        print ("cmd")
        cmd = self.commands.get(args[0])
        if not cmd:
            print ("not cmd")
            return self._error(1001)

        print (cmd)

        cmd = getattr(self, cmd)
        args = args[1:]

        params = []
        try:
            for param in args:
                params.append(int(param))
        except ValueError:
            return self.nak
        return cmd(params)

    def _set_allmode(self, params):
        print("allmode")
        print (params)
        return self.ack

    def _error(self, error_code):
        error_string = self.errors.get(error_code)
        print (error_string)
        hex_string = codecs.encode(
            error_string.encode('raw_unicode_escape'),
            'hex'
        )
        retval = f'{self.header}ERROR({error_code})[{error_string}]'
        retval += f'({hex_string}) {self.cmd_id}{self.tail}'
        print (retval)

        return retval
