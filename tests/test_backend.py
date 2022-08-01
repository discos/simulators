import unittest
import time
from simulators.utils import ACS_TO_UNIX_TIME
from simulators.backend.sardara import System as Sardara
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
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, "invalid command 'unknown'")

    def test_invalid_header(self):
        command = 'status'
        msg = '&%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!undefined')
        self.assertEqual(answer, 'invalid')
        self.assertEqual(reason, "syntax error: invalid message type '&'")

    def test_invalid_separator(self):
        command = 'set-enable'
        msg = '?%s foo bar\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!undefined')
        self.assertEqual(answer, 'invalid')
        self.assertEqual(reason, 'syntax error: invalid syntax')

    def test_greet_message(self):
        msg = self.system.system_greet()
        expected = '!version,ok,%s\r\n' % PROTOCOL_VERSION
        self.assertEqual(msg, expected)

    def test_send_reply_instead_of_request(self):
        command = 'status'  # We use an existing command
        msg = '!%s,ok\r\n' % command
        for byte in msg:
            self.assertTrue(self.system.parse(byte))

    def test_status(self):
        command = 'status'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, timestamp, status_code, acquiring = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
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
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, version = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')
        self.assertEqual(version, PROTOCOL_VERSION)

    def test_get_configuration(self):
        command = 'get-configuration'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, configuration = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')
        self.assertEqual(configuration, 'unconfigured')

    def test_set_valid_configuration(self):
        command = 'set-configuration'
        configuration = 'valid'
        msg = '?%s,%s\r\n' % (command, configuration)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_set_invalid_configuration(self):
        command = 'set-configuration'
        configuration = 'Invalid'
        msg = '?%s,%s\r\n' % (command, configuration)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'invalid configuration')

    def test_set_no_configuration(self):
        command = 'set-configuration'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'missing argument: configuration')

    def test_get_integration(self):
        command = 'get-integration'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, integration = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')
        self.assertEqual(integration, '0')

    def test_set_valid_integration(self):
        command = 'set-integration'
        integration = 10
        msg = '?%s,%s\r\n' % (command, integration)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_set_invalid_integration(self):
        command = 'set-integration'
        integration = -10
        msg = '?%s,%s\r\n' % (command, integration)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'integration time must be an integer number')

    def test_set_no_integration(self):
        command = 'set-integration'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'missing argument: integration time')

    def test_get_tpi(self):
        command = 'get-tpi'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, left, right = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')
        try:
            left = float(left)
            right = float(right)
        except ValueError:
            self.fail('Tpi values should be a floating point number!')

    def test_get_tp0(self):
        command = 'get-tp0'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, left, right = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
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
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, timestamp = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')
        try:
            timestamp = float(timestamp)
        except ValueError:
            self.fail('Time should be a floating point number!')
        self.assertAlmostEqual(timestamp, time.time(), places=3)

    def test_start(self):
        command = 'start'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_stop(self):
        command = 'stop'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'not acquiring')

    def test_start_wrong_timestamp(self):
        command = 'start'
        timestamp = 'wrong'
        msg = '?%s,%s\r\n' % (command, timestamp)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, "wrong timestamp '%s'" % timestamp)

    def test_stop_wrong_timestamp(self):
        command = 'stop'
        timestamp = 'wrong'
        msg = '?%s,%s\r\n' % (command, timestamp)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, "wrong timestamp '%s'" % timestamp)

    def test_start_and_stop(self):
        self.test_start()
        command = 'stop'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_start_and_start(self):
        self.test_start()
        command = 'start'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'already acquiring')

    def test_start_elapsed(self):
        command = 'start'
        starting_time = (time.time() - 1) * ACS_TO_UNIX_TIME
        msg = '?%s,%.7f\r\n' % (command, starting_time)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'starting time already elapsed')

    def test_start_later(self, delay=10):
        command = 'start'
        starting_time = (time.time() + delay) * ACS_TO_UNIX_TIME
        msg = '?%s,%.7f\r\n' % (command, starting_time)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_start_later_twice(self):
        for delay in [10, 11]:
            self.test_start_later(delay)

    def test_stop_elapsed(self):
        command = 'stop'
        starting_time = (time.time() - 1) * ACS_TO_UNIX_TIME
        msg = '?%s,%.7f\r\n' % (command, starting_time)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'stop time already elapsed')

    def test_stop_later(self, delay=10):
        command = 'stop'
        starting_time = (time.time() + delay) * ACS_TO_UNIX_TIME
        msg = '?%s,%.7f\r\n' % (command, starting_time)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
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
        msg = '?%s,%s,%s,%s,%s,%s,%s,%s\r\n' % (
            command,
            section,
            start_freq,
            bandwidth,
            feed,
            mode,
            sample_rate,
            bins
        )
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
        expected_reason = 'backend supports %d sections' % (
            self.system.max_sections
        )
        self.assertEqual(reason, expected_reason)

    def test_set_section_wrong_bandwidth(self):
        response = self._set_section(bandwidth=2500.)
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!set-section')
        self.assertEqual(answer, 'fail')
        expected_reason = 'backend maximum bandwidth is %f' % (
            self.system.max_bandwidth
        )
        self.assertEqual(reason, expected_reason)

    def test_set_section_less_arguments(self):
        command = 'set-section'
        section = 0
        msg = '?%s,%d\r\n' % (command, section)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'set-section needs 7 arguments')

    def test_set_section_wrong_arguments(self):
        command = 'set-section'
        section = 0
        msg = '?%s,%d,w,w,w,w,w,w\r\n' % (command, section)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'wrong parameter format')

    def test_cal_on(self):
        command = 'cal-on'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_cal_on_with_interleave(self):
        command = 'cal-on'
        interleave = 10
        msg = '?%s,%s\r\n' % (command, interleave)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_cal_on_negative_interleave(self):
        command = 'cal-on'
        interleave = -10
        msg = '?%s,%s\r\n' % (command, interleave)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'interleave samples must be a positive int')

    def test_set_filename(self):
        command = 'set-filename'
        filename = 'testfile'
        msg = '?%s,%s\r\n' % (command, filename)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_set_no_filename(self):
        command = 'set-filename'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'command needs <filename> as argument')

    def test_convert_data(self):
        command = 'convert-data'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_set_enable(self):
        command = 'set-enable'
        feed1 = 0
        feed2 = 3
        msg = '?%s,%d,%d\r\n' % (command, feed1, feed2)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'ok')

    def test_set_enable_less_than_2_feeds(self):
        command = 'set-enable'
        msg = '?%s\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'set-enable needs 2 arguments')

    def test_set_enable_wrong_parameter_format(self):
        command = 'set-enable'
        msg = '?%s,foo,bar\r\n' % command
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'wrong parameter format')

    def test_set_enable_feed1_out_of_range(self):
        command = 'set-enable'
        feed1 = 8
        feed2 = 3
        msg = '?%s,%d,%d\r\n' % (command, feed1, feed2)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'feed1 out of range')

    def test_set_enable_feed2_out_of_range(self):
        command = 'set-enable'
        feed1 = 0
        feed2 = 8
        msg = '?%s,%d,%d\r\n' % (command, feed1, feed2)
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1]).strip()
        cmd, answer, reason = response.split(',')
        self.assertEqual(cmd, '!%s' % command)
        self.assertEqual(answer, 'fail')
        self.assertEqual(reason, 'feed2 out of range')


class TestSardara(unittest.TestCase):

    def setUp(self):
        self.system = Sardara()

    def tearDown(self):
        self.system.system_stop()

    def test_sardara_instance(self):
        self.assertEqual(type(self.system), Sardara)


class TestMessage(unittest.TestCase):

    def test_request_message(self):
        message = grammar.Message(
            message_type=grammar.REQUEST,
            name='status'
        )
        self.assertEqual(str(message), '?status\r\n')


if __name__ == '__main__':
    unittest.main()
