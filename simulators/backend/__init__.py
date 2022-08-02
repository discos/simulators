from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem
from simulators.backend import grammar
from simulators.backend.genericbackend import GenericBackend, BackendException
from simulators.backend.sardara import Sardara
from simulators.utils import ACS_TO_UNIX_TIME


servers = [
    (('0.0.0.0', 12800), (), ThreadingTCPServer, {'backend_type': Sardara})
]

PROTOCOL_VERSION = '1.2'
headers = ('!', '?')
closers = ('\r\n')


class System(ListeningSystem):

    commands = {
        'status': 'do_status',
        'get-tpi': 'do_getTpi',
        'get-tp0': 'do_getTp0',
        'version': 'do_version',
        'get-configuration': 'do_get_configuration',
        'set-configuration': 'do_set_configuration',
        'set-integration': 'do_set_integration',
        'get-integration': 'do_get_integration',
        'time': 'do_time',
        'start': 'do_start',
        'stop': 'do_stop',
        'set-section': 'do_set_section',
        'cal-on': 'do_cal_on',
        'set-filename': 'do_set_filename',
        'convert-data': 'do_convert_data',  # New in version 1.2
        'set-enable': 'do_set_enable'
    }

    def __init__(self, backend_type=GenericBackend):
        self.backend = backend_type()
        self._set_default()

    def __del__(self):
        self.system_stop()

    def system_stop(self):
        self.backend.system_stop()
        return ListeningSystem.system_stop()

    def _set_default(self):
        self.msg = ''

    @staticmethod
    def system_greet():
        connection_reply = grammar.Message(
            message_type=grammar.REPLY,
            name="version",
            code=grammar.OK,
            arguments=[PROTOCOL_VERSION]
        )
        return str(connection_reply)

    def parse(self, byte):
        self.msg += byte
        if self.msg.endswith(closers):
            msg = self.msg.strip('\n\r')
            self._set_default()
            return self._parse(msg)
        return True

    def _parse(self, msg):
        try:
            message = grammar.parse_message(msg)
        except grammar.GrammarException as ge:
            reply_message = grammar.Message(
                message_type=grammar.REPLY,
                name="undefined",
                code=grammar.INVALID,
                arguments=["syntax error: %s" % (str(ge),)]
            )
            return str(reply_message)
        if message.is_request():
            try:
                reply_message = grammar.Message(
                    message_type=grammar.REPLY,
                    name=message.name
                )
                if message.name not in self.commands.keys():
                    raise BackendException(
                        "invalid command '%s'" % (message.name,)
                    )
                method = getattr(self, self.commands[message.name])
                reply_arguments = method(message.arguments)
                if reply_arguments:
                    reply_message.arguments = map(str, reply_arguments)
                reply_message.code = grammar.OK
                return str(reply_message)
            except BackendException as he:
                return self._send_fail_reply(message, str(he))
        else:
            return True

    @staticmethod
    def _send_fail_reply(request, fail_message):
        reply = grammar.Message(
            message_type=grammar.REPLY,
            name=request.name,
            code=grammar.FAIL,
            arguments=[fail_message]
        )
        return str(reply)

    def do_status(self, _):
        return self.backend.status()

    def do_getTpi(self, _):
        return self.backend.get_tpi()

    def do_getTp0(self, _):
        return self.backend.get_tp0()

    @staticmethod
    def do_version(_):
        return [PROTOCOL_VERSION]

    def do_get_configuration(self, _):
        return self.backend.get_configuration()

    def do_set_configuration(self, args):
        if len(args) < 1:
            raise BackendException("missing argument: configuration")
        return self.backend.set_configuration(str(args[0]))

    def do_get_integration(self, _):
        return self.backend.get_integration()

    def do_set_integration(self, args):
        if len(args) < 1:
            raise BackendException("missing argument: integration time")
        try:
            _integration = int(args[0])
            if _integration < 0:
                raise ValueError
        except ValueError:
            raise BackendException(
                "integration time must be an integer number"
            )
        return self.backend.set_integration(_integration)

    def do_time(self, _):
        return self.backend.time()

    def do_start(self, args):
        if len(args) < 1:
            return self.backend.start()
        try:
            timestamp = float(args[0]) / ACS_TO_UNIX_TIME
        except ValueError:
            raise BackendException("wrong timestamp '%s'" % (args[0],))
        return self.backend.start(timestamp)

    def do_stop(self, args):
        if len(args) < 1:
            return self.backend.stop()
        try:
            timestamp = float(args[0]) / ACS_TO_UNIX_TIME
        except ValueError:
            raise BackendException("wrong timestamp '%s'" % (args[0],))
        return self.backend.stop(timestamp)

    def do_set_section(self, args):
        def _get_param(p, _type_converter=str):
            if p == "*":
                return p
            else:
                return _type_converter(p)

        if len(args) < 7:
            raise BackendException("set-section needs 7 arguments")
        try:
            section = _get_param(args[0], int)
            start_freq = _get_param(args[1], float)
            bandwidth = _get_param(args[2], float)
            feed = _get_param(args[3], int)
            mode = _get_param(args[4])
            sample_rate = _get_param(args[5], float)
            bins = _get_param(args[6], int)
        except ValueError:
            raise BackendException("wrong parameter format")
        reply = self.backend.set_section(
            section,
            start_freq,
            bandwidth,
            feed,
            mode,
            sample_rate,
            bins
        )
        return reply

    def do_cal_on(self, args):
        if len(args) < 1:
            _interleave = 0
        else:
            try:
                _interleave = int(args[0])
                if _interleave < 0:
                    raise ValueError
            except ValueError:
                raise BackendException(
                    "interleave samples must be a positive int"
                )
        return self.backend.cal_on(_interleave)

    def do_set_filename(self, args):
        if len(args) < 1:
            raise BackendException("command needs <filename> as argument")
        else:
            return self.backend.set_filename(args[0])

    def do_convert_data(self, _):
        # Added in version 1.2
        return self.backend.convert_data()

    def do_set_enable(self, args):
        if len(args) < 2:
            raise BackendException("set-enable needs 2 arguments")
        try:
            _feed1 = int(args[0])
            _feed2 = int(args[1])
        except ValueError:
            raise BackendException("wrong parameter format")
        return self.backend.set_enable(_feed1, _feed2)
