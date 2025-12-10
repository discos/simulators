import unittest
from simulators import calmux


class TestCalmux(unittest.TestCase):

    def setUp(self):
        self.system = calmux.System()

    def _send(self, message):
        for byte in message[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(message[-1])
        response = response.strip().split(' ')
        if len(response) == 1:
            if response[0] == 'nak':
                raise Exception('Received nak')
        else:
            for index, val in enumerate(response):
                response[index] = int(val)
        return response

    def test_known_headers(self):
        for header in ['?', 'I', 'C', 'F']:
            self.assertTrue(self.system.parse(header))
            self.system.msg = ''

    def test_unknown_header(self):
        self.assertFalse(self.system.parse('U'))

    def test_max_msg_length_reached(self):
        message = 'I 16 10'
        with self.assertRaises(ValueError):
            self._send(message)

    def test_too_few_arguments(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self._send('I 1\n')

    def test_unrecognized_command(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self._send('? 5\n')

    def test_wrong_args_type(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self._send('C ONE\n')

    def test_get_status(self):
        message = '?\n'

        response = self._send(message)

        self.assertEqual(len(response), 3)
        self.assertEqual(response[0], 16)
        self.assertEqual(response[1], 0)
        self.assertEqual(response[2], 0)

    def test_get_status_wrong_argc(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            _ = self._send('? 0 0\n')

    def test_set_input(self, channel=0, polarity=0):
        message = f'I {channel} {polarity}\n'

        response = self._send(message)

        self.assertEqual(len(response), 1)
        self.assertEqual(response[0], 'ack')

    def test_set_input_wrong_polarity(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self.test_set_input(polarity=2)

    def test_set_input_too_high_channel(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self.test_set_input(channel=50)

    def test_set_calibration(self, cal=1):
        message = f'C {cal}\n'

        response = self._send(message)

        self.assertEqual(len(response), 1)
        self.assertEqual(response[0], 'ack')

    def test_calibration_wrong_cal(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self.test_set_calibration(cal=2)

    def test_calibration_wrong_params(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self._send('C 0 0\n')

    def test_get_frequency(self, period=500):
        message = f'F {period}\n'

        response = self._send(message)

        self.assertEqual(len(response), 3)
        self.assertEqual(response[0], 0)
        self.assertEqual(response[1], 0)
        self.assertEqual(response[2], 0)

    def test_get_frequency_too_high_period(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self.test_get_frequency(period=6000)

    def test_get_frequency_wrong_params(self):
        with self.assertRaisesRegex(Exception, 'Received nak'):
            self._send('F 0 1\n')


if __name__ == '__main__':
    unittest.main()
