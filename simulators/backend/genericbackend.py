import time
import random
import re
from threading import Timer
from simulators.backend import grammar
from simulators.common import ListeningSystem
from simulators.utils import ACS_TO_UNIX_TIME


PROTOCOL_VERSION = '1.2'


class BackendError(Exception):
    pass


class GenericBackendSystem(ListeningSystem):

    commands = {
        'status': 'do_status',
        'version': 'do_version',
        'get-configuration': 'do_get_configuration',
        'set-configuration': 'do_set_configuration',
        'set-integration': 'do_set_integration',
        'get-integration': 'do_get_integration',
        'set-section': 'do_set_section',
        'get-tpi': 'do_getTpi',
        'get-tp0': 'do_getTp0',
        'cal-on': 'do_cal_on',
        'set-enable': 'do_set_enable',
        'time': 'do_time',
        'start': 'do_start',
        'stop': 'do_stop',
        'set-filename': 'do_set_filename',
        'get-filename': 'do_get_filename',
        'convert-data': 'do_convert_data',  # New in version 1.2
    }

    def __init__(self):
        self.status_string = "ok"
        self.acquiring = False
        self._waiting_for_start_time = False
        self._startID = None
        self._waiting_for_stop_time = False
        self._stopID = None
        self._filename = ""
        self.configuration_string = "unconfigured"
        self._set_default()
        self.integration = 0
        self._sections = {}
        self.max_sections = 14
        self.max_bandwidth = 2000
        self.interleave = 0
        self.current_sections = range(0, self.max_sections)
        self._valid_conf_re = re.compile("^[a-z0-9]")
        self.failure = False

    def system_stop(self):
        if self._startID:
            self._startID.cancel()
            self._startID.join()
        if self._stopID:
            self._stopID.cancel()
            self._stopID.join()
        return super().system_stop()

    def _set_default(self):
        self.msg = ''

    def parse(self, byte):
        self.msg += byte
        if self.msg.endswith(grammar.TAIL):
            msg = self.msg.strip(grammar.TAIL)
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
                arguments=[f"syntax error: {ge}"]
            )
            return str(reply_message)

        if message.is_request():
            try:
                reply_message = grammar.Message(
                    message_type=grammar.REPLY,
                    name=message.name
                )
                if message.name not in self.commands:
                    raise BackendError(f"invalid command '{message.name}'")
                method = getattr(self, self.commands[message.name])
                reply_arguments = method(message.arguments)
                if reply_arguments:
                    reply_message.arguments = map(str, reply_arguments)
                if self.failure:
                    reply_message.code = grammar.FAIL
                else:
                    reply_message.code = grammar.OK
                return str(reply_message)
            except BackendError as he:
                return self._send_fail_reply(message, str(he))
        else:
            return True

    @staticmethod
    def system_greet():
        connection_reply = grammar.Message(
            message_type=grammar.REPLY,
            name="version",
            code=grammar.OK,
            arguments=[PROTOCOL_VERSION]
        )
        return str(connection_reply)

    def do_status(self, _):
        return (
            self._get_time(),
            self.status_string,
            1 if self.acquiring else 0
        )

    @staticmethod
    def do_version(_):
        return [PROTOCOL_VERSION]

    def do_start(self, args):
        if len(args) < 1:
            self._start_now()
        else:
            try:
                timestamp = float(args[0]) / ACS_TO_UNIX_TIME
                self._start_at(timestamp)
            except ValueError as ex:
                raise BackendError(f"wrong timestamp '{args[0]}'") from ex

    def do_stop(self, args):
        if len(args) < 1:
            self._stop_now()
        else:
            try:
                timestamp = float(args[0]) / ACS_TO_UNIX_TIME
                self._stop_at(timestamp)
            except ValueError as ex:
                raise BackendError(f"wrong timestamp '{args[0]}'") from ex

    def do_set_configuration(self, args):
        if len(args) < 1:
            raise BackendError("missing argument: configuration")
        conf_name = str(args[0])
        if not self._is_valid_configuration(conf_name):
            raise BackendError("invalid configuration")
        # Here you should perform actual hardware configuration
        self.configuration_string = conf_name

    def do_get_configuration(self, _):
        return [self.configuration_string]

    def do_get_integration(self, _):
        return [self.integration]

    def do_set_integration(self, args):
        if len(args) < 1:
            raise BackendError("missing argument: integration time")
        try:
            _integration = int(args[0])
            if _integration < 0:
                raise ValueError
        except ValueError as ex:
            raise BackendError(
                "integration time must be an integer number"
            ) from ex
        self.integration = _integration

    def do_set_filename(self, args):
        if len(args) < 1:
            raise BackendError("command needs <filename> as argument")
        self._filename = args[0]

    def do_get_filename(self, _):
        return [self._filename]

    def do_time(self, _):
        return [self._get_time()]

    def do_convert_data(self, _):
        # Added in version 1.2
        pass

    @staticmethod
    def _send_fail_reply(request, fail_message):
        reply = grammar.Message(
            message_type=grammar.REPLY,
            name=request.name,
            code=grammar.FAIL,
            arguments=[fail_message]
        )
        return str(reply)

    @staticmethod
    def _get_time():
        # Should ask the backend hardware clock
        return f'{time.time():.7f}'

    def _is_valid_configuration(self, configuration_name):
        return self._valid_conf_re.match(configuration_name)

    def _start_now(self):
        if self.acquiring:
            raise BackendError("already acquiring")
        self._waiting_for_start_time = False
        self.acquiring = True

    def _start_at(self, timestamp):
        if timestamp < time.time():
            raise BackendError("starting time already elapsed")
        if self._waiting_for_start_time:
            self._startID.cancel()
        self._waiting_for_start_time = True
        start_in = timestamp - time.time()
        self._startID = Timer(start_in, self._start_now)
        self._startID.start()

    def _stop_now(self):
        if not self.acquiring:
            raise BackendError("not acquiring")
        self._waiting_for_start_time = False
        self._waiting_for_stop_time = False
        self.acquiring = False

    def _stop_at(self, timestamp):
        if timestamp < time.time():
            raise BackendError("stop time already elapsed")
        if self._waiting_for_stop_time:
            self._stopID.cancel()
        self._waiting_for_stop_time = True
        stop_in = timestamp - time.time()
        self._stopID = Timer(stop_in, self._stop_now)
        self._stopID.start()

    @staticmethod
    def do_getTpi(_):
        return [random.random() * 100, random.random() * 100]

    @staticmethod
    def do_getTp0(_):
        return [0, 0]

    def do_set_section(self, args):
        def _get_param(p, _type_converter=str):
            if p == "*":
                return p
            return _type_converter(p)

        if len(args) < 7:
            raise BackendError("set-section needs 7 arguments")
        try:
            section = _get_param(args[0], int)
            start_freq = _get_param(args[1], float)
            bandwidth = _get_param(args[2], float)
            feed = _get_param(args[3], int)
            mode = _get_param(args[4])
            sample_rate = _get_param(args[5], float)
            bins = _get_param(args[6], int)
        except ValueError as ex:
            raise BackendError("wrong parameter format") from ex

        if section != "*" and section > self.max_sections:
            raise BackendError(
                f"backend supports {self.max_sections} sections"
            )
        if bandwidth != "*" and bandwidth > self.max_bandwidth:
            raise BackendError(
                f"backend maximum bandwidth is {self.max_bandwidth:0.6f}"
            )
        self._sections[section] = (
            start_freq,
            bandwidth,
            feed,
            mode,
            sample_rate,
            bins
        )

    def do_cal_on(self, args):
        if len(args) < 1:
            interleave = 0
        else:
            try:
                interleave = int(args[0])
                if interleave < 0:
                    raise ValueError
            except ValueError as ex:
                raise BackendError(
                    "interleave samples must be a positive int"
                ) from ex
        self.interleave = interleave

    def do_set_enable(self, args):
        if len(args) < 2:
            raise BackendError("set-enable needs 2 arguments")
        try:
            feed1 = int(args[0])
            feed2 = int(args[1])
        except ValueError as ex:
            raise BackendError("wrong parameter format") from ex

        if feed1 not in range(int(self.max_sections / 2)):
            raise BackendError("feed1 out of range")
        if feed2 not in range(int(self.max_sections / 2)):
            raise BackendError("feed2 out of range")
        self.current_sections = [
            feed1 * 2,
            feed1 * 2 + 1,
            feed2 * 2,
            feed2 * 2 + 1
        ]
