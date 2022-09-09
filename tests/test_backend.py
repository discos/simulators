import unittest
import time
from simulators.utils import ACS_TO_UNIX_TIME
from simulators.backend import System
from simulators.backend.sardara import System as Sardara
from simulators.backend.mistral import System as Mistral
from simulators.backend.genericbackend import (
    grammar,
    PROTOCOL_VERSION,
    GenericBackendSystem,
)


class TestGenericBackend(unittest.TestCase):

    def setUp(self):
        self.system = GenericBackendSystem()

    def tearDown(self):
        self.system.system_stop()

    def test_empty_message(self):
        msg = '\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!undefined')
        self.assertEqual(answer, 'invalid')
        self.assertEqual(reason, "syntax error: empty message is not valid")

    def test_invalid_command(self):
        command = 'unknown'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, "invalid command 'unknown'")

    def test_invalid_header(self):
        command = 'status'
        msg = f'&{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!undefined')
        self.assertEqual(answer, 'invalid')
        self.assertEqual(reason, "syntax error: invalid message type '&'")

    def test_invalid_separator(self):
        command = 'set-enable'
        msg = f'?{command} foo bar\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!undefined')
        self.assertEqual(answer, 'invalid')
        self.assertEqual(reason, 'syntax error: invalid syntax')

    def test_greet_message(self):
        msg = self.system.system_greet()
        expected = f'!version,ok,{PROTOCOL_VERSION}\r\n'
        self.assertEqual(msg, expected)

    def test_send_reply_instead_of_request(self):
        command = 'status'  # We use an existing command
        msg = f'!{command},ok\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_status(self):
        command = 'status'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, timestamp, status_code, acquiring = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')
        try:
            timestamp = float(timestamp)
        except ValueError:
            self.fail('Time should be a floating point number!')
        self.assertAlmostEqual(timestamp, time.time(), places=3)
        self.assertEqual(status_code, 'ok')
        self.assertEqual(acquiring, '0')

    def test_version(self):
        command = 'version'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, version = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')
        self.assertEqual(version, PROTOCOL_VERSION)

    def test_get_configuration(self):
        command = 'get-configuration'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, configuration = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')
        self.assertEqual(configuration, 'unconfigured')

    def test_set_valid_configuration(self):
        command = 'set-configuration'
        configuration = 'valid'
        msg = f'?{command},{configuration}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_set_invalid_configuration(self):
        command = 'set-configuration'
        configuration = 'Invalid'
        msg = f'?{command},{configuration}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'invalid configuration')

    def test_set_no_configuration(self):
        command = 'set-configuration'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'missing argument: configuration')

    def test_get_integration(self):
        command = 'get-integration'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, integration = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')
        self.assertEqual(integration, '0')

    def test_set_valid_integration(self):
        command = 'set-integration'
        integration = 10
        msg = f'?{command},{integration}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_set_invalid_integration(self):
        command = 'set-integration'
        integration = -10
        msg = f'?{command},{integration}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'integration time must be an integer number')

    def test_set_no_integration(self):
        command = 'set-integration'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'missing argument: integration time')

    def test_get_tpi(self):
        command = 'get-tpi'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, left, right = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')
        try:
            left = float(left)
            right = float(right)
        except ValueError:
            self.fail('Tpi values should be a floating point number!')

    def test_get_tp0(self):
        command = 'get-tp0'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, left, right = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')
        try:
            left = float(left)
            right = float(right)
        except ValueError:
            self.fail('Tp0 values should be a floating point number!')
        self.assertEqual(left, 0)
        self.assertEqual(right, 0)

    def test_time(self):
        command = 'time'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, timestamp = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')
        try:
            timestamp = float(timestamp)
        except ValueError:
            self.fail('Time should be a floating point number!')
        self.assertAlmostEqual(timestamp, time.time(), places=3)

    def test_start(self):
        command = 'start'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_stop(self):
        command = 'stop'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'not acquiring')

    def test_start_wrong_timestamp(self):
        command = 'start'
        timestamp = 'wrong'
        msg = f'?{command},{timestamp}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, f"wrong timestamp '{timestamp}'")

    def test_stop_wrong_timestamp(self):
        command = 'stop'
        timestamp = 'wrong'
        msg = f'?{command},{timestamp}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, f"wrong timestamp '{timestamp}'")

    def test_start_and_stop(self):
        self.test_start()
        command = 'stop'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_start_and_start(self):
        self.test_start()
        command = 'start'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'already acquiring')

    def test_start_elapsed(self):
        command = 'start'
        starting_time = (time.time() - 1) * ACS_TO_UNIX_TIME
        msg = f'?{command},{starting_time:0.7f}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'starting time already elapsed')

    def test_start_later(self, delay=10):
        command = 'start'
        starting_time = (time.time() + delay) * ACS_TO_UNIX_TIME
        msg = f'?{command},{starting_time:0.7f}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_start_later_twice(self):
        for delay in [10, 11]:
            self.test_start_later(delay)

    def test_stop_elapsed(self):
        command = 'stop'
        starting_time = (time.time() - 1) * ACS_TO_UNIX_TIME
        msg = f'?{command},{starting_time:0.7f}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'stop time already elapsed')

    def test_stop_later(self, delay=10):
        command = 'stop'
        starting_time = (time.time() + delay) * ACS_TO_UNIX_TIME
        msg = f'?{command},{starting_time:0.7f}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_stop_later_twice(self):
        for delay in [10, 11]:
            self.test_stop_later(delay)

    def _set_section(
        self,
        section=0,
        start_freq=1000.,
        bandwidth=1000.,
        feed=0,
        mode='default',
        sample_rate=10.,
        bins=10
    ):
        command = 'set-section'
        args = (
            command,
            section,
            start_freq,
            bandwidth,
            feed,
            mode,
            sample_rate,
            bins
        )
        msg = f'?{args[0]},{args[1]},{args[2]},{args[3]},'
        msg += f'{args[4]},{args[5]},{args[6]},{args[7]}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        return self.system.parse(msg[-1]).strip()

    def test_set_section(self):
        response = self._set_section()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!set-section')
        self.assertEqual(answer, 'ok')

    def test_set_section_wildcards(self):
        response = self._set_section(
            '*', '*', '*', '*', '*', '*', '*'
        )
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!set-section')
        self.assertEqual(answer, 'ok')

    def test_set_section_wrong_section(self):
        response = self._set_section(section=15)
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!set-section')
        self.assertEqual(answer, 'fail')
        expected_reason = 'backend supports '
        expected_reason += f'{self.system.max_sections} sections'
        self.assertEqual(reason, expected_reason)

    def test_set_section_wrong_bandwidth(self):
        response = self._set_section(bandwidth=2500.)
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!set-section')
        self.assertEqual(answer, 'fail')
        expected_reason = 'backend maximum bandwidth is '
        expected_reason += f'{self.system.max_bandwidth:0.6f}'
        self.assertEqual(reason, expected_reason)

    def test_set_section_less_arguments(self):
        command = 'set-section'
        section = 0
        msg = f'?{command},{section}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'set-section needs 7 arguments')

    def test_set_section_wrong_arguments(self):
        command = 'set-section'
        section = 0
        msg = f'?{command},{section},w,w,w,w,w,w\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'wrong parameter format')

    def test_cal_on(self):
        command = 'cal-on'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_cal_on_with_interleave(self):
        command = 'cal-on'
        interleave = 10
        msg = f'?{command},{interleave}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_cal_on_negative_interleave(self):
        command = 'cal-on'
        interleave = -10
        msg = f'?{command},{interleave}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'interleave samples must be a positive int')

    def test_set_filename(self):
        command = 'set-filename'
        filename = 'testfile'
        msg = f'?{command},{filename}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_set_no_filename(self):
        command = 'set-filename'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'command needs <filename> as argument')

    def test_convert_data(self):
        command = 'convert-data'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_set_enable(self):
        command = 'set-enable'
        feed1 = 0
        feed2 = 3
        msg = f'?{command},{feed1},{feed2}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_set_enable_less_than_2_feeds(self):
        command = 'set-enable'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'set-enable needs 2 arguments')

    def test_set_enable_wrong_parameter_format(self):
        command = 'set-enable'
        msg = f'?{command},foo,bar\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'wrong parameter format')

    def test_set_enable_feed1_out_of_range(self):
        command = 'set-enable'
        feed1 = 8
        feed2 = 3
        msg = f'?{command},{feed1},{feed2}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'feed1 out of range')

    def test_set_enable_feed2_out_of_range(self):
        command = 'set-enable'
        feed1 = 0
        feed2 = 8
        msg = f'?{command},{feed1},{feed2}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'feed2 out of range')


class TestSardara(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='sardara')

    def tearDown(self):
        self.system.system_stop()

    def test_sardara_instance(self):
        self.assertIsInstance(self.system, Sardara)


class TestMistral(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='mistral')

    def tearDown(self):
        self.system.system_stop()

    def test_mistral_instance(self):
        self.assertIsInstance(self.system, Mistral)

    def test_system_not_initialized(self):
        command = 'status'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, code, timestamp, message, acquiring = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(code, 'ok')
        self.assertEqual(message, 'system not initialized (setup required)')
        self.assertEqual(acquiring, '0')

    def test_setup(self):
        command = 'setup'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'ok')

    def test_setup_in_progress(self):
        self.test_setup()  # The setup lasts 60 seconds (setup_time)
        command = 'status'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, code, timestamp, message, acquiring = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(code, 'ok')
        self.assertEqual(message, 'setup in progress')
        self.assertEqual(acquiring, '0')

    def test_setup_and_ready(self):
        self.system.setup_time = 0  # Defalut value is 60 seconds
        self.test_setup()
        command = 'status'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, code, timestamp, message, acquiring = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(code, 'ok')
        self.assertEqual(message, 'no task is running')
        self.assertEqual(acquiring, '0')

    def test_setup_and_setup(self):
        self.test_setup()
        command = 'setup'
        msg = f'?{command}\r\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, f'!{command}')
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'setup is still running')


class TestMessage(unittest.TestCase):

    def test_request_message(self):
        message = grammar.Message(
            message_type=grammar.REQUEST,
            name='status'
        )
        self.assertEqual(str(message), '?status\r\n')


if __name__ == '__main__':
    unittest.main()
