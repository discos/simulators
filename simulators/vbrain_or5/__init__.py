# Authors 
# Sergio Poppi <sergio.poppi@inaf.it>


from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem


class System(ListeningSystem):


    commands = {
        'SETPOSITION': 'setPosition',
        'RUNMD': 'runMd',
        'UPDATERUNMD': 'updateRunMd',
        'RUNMDSTREAM': 'runMdStream',
        'STOPMDSTREAM': 'stopMdStream',
        'GETLASTRESULTMD': 'getLastResultMd',
        'GETSTATUSMD': 'getStatusMd',
        'REQSUBOFFSET': 'reqSubOffset'
    }
    def __init__(self):
        pass


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
