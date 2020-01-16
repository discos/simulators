import unittest
from simulators.mscu import System
from simulators.mscu.servo import Servo


class TestMSCU(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def tearDown(self):
        del self.system

    def test_wrong_header(self):
        self.assertFalse(self.system.parse('1'))

    def test_clean(self):
        for servo in range(4):
            msg = '#clean:0=%s\r\n' % servo
            exp_response = '?%s@%s' % (msg[1:], msg[1:])
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_clean_with_params(self):
        for servo in range(4):
            msg = '#clean:0=%s,0,1.1,0x0002\r\n' % servo
            exp_response = 'clean:0=%s,0,1.1,2\r\n' % servo
            exp_response = '?%s@%s' % (exp_response, exp_response)
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_disable(self):
        for servo in range(4):
            msg = '#disable:0=%s\r\n' % servo
            exp_response = '?%s@%s' % (msg[1:], msg[1:])
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_disable_with_params(self):
        for servo in range(4):
            msg = '#disable:0=%s,0,1.1,0x0002\r\n' % servo
            exp_response = 'disable:0=%s,0,1.1,2\r\n' % servo
            exp_response = '?%s@%s' % (exp_response, exp_response)
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_getappstatus(self):
        for servo in range(4):
            msg = '#getappstatus:0=%s\r\n' % servo
            exp_response = '?getappstatus:0=%s> 0000030D\r\n' % servo
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_getpos(self):
        for servo in range(4):
            msg = '#getpos:0=%s\r\n' % servo
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response[0], '?')
            self.assertEqual(response[1:11], msg[1:11])
            self.assertEqual(response[11:13], '> ')
            self.assertEqual(response[-2:], '\r\n')
            params = response[13:-2].split(',')
            recv_time = int(params[0])
            exp_time = Servo.ctime()
            self.assertTrue(abs(recv_time - exp_time) < 1000)
            data = self.system.servos[servo].history.get()[1:]
            for i, _ in enumerate(data):
                self.assertEqual(float(params[1+i]), data[i])

    def test_getspar(self):
        for servo in range(4):
            msg = '#getspar:0=%s' % servo
            exp_response = '?%s> 0\r\n' % msg[1:]
            msg += '\r\n'
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_getspar_acceleration(self):
        for servo in range(4):
            msg = '#getspar:0=%s' % servo
            exp_response = '?%s> 3\r\n' % msg[1:]
            msg += ',1250,0\r\n'
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_getspar_max_speed(self):
        for servo in range(4):
            msg = '#getspar:0=%s' % servo
            exp_response = '?%s> 10\r\n' % msg[1:]
            msg += ',1240,0\r\n'
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_getstatus(self):
        for servo in range(4):
            msg = '#getstatus:0=%s\r\n' % servo
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response[0], '?')
            self.assertEqual(response[1:14], msg[1:14])
            self.assertEqual(response[14:16], '> ')
            self.assertEqual(response[-2:], '\r\n')
            params = response[16:-2].split(',')
            recv_time = int(params[0])
            exp_time = Servo.ctime()
            self.assertTrue(abs(recv_time - exp_time) < 1000)
            recv_state = int(params[1])
            self.assertEqual(recv_state, 4)  # 4: remote auto
            recv_status = params[2]
            self.assertEqual(recv_status, 'FFFF')  # FFFF: everything ok
            recv_cab_state = int(params[3])
            self.assertEqual(recv_cab_state, 3)  # 3: stow, parked
            data = self.system.servos[servo].history.get()[1:]
            for i, _ in enumerate(data):
                self.assertEqual(float(params[4+i]), data[i])

    def test_setsdatbitb16(self):
        for servo in range(4):
            msg = '#setsdatbitb16:0=%s\r\n' % servo
            exp_response = '@%s' % msg[1:]
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_setsdatbitb16_with_params(self):
        for servo in range(4):
            msg = '#setsdatbitb16:0=%s,0,1.1,0x0002\r\n' % servo
            exp_response = '@setsdatbitb16:0=%s,0,1.1,2\r\n' % servo
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_setpos(self, pos=0):
        for servo in range(4):
            msg = '#setpos:0=%s,0,0,0' % servo
            msg += (',%s' % pos) * self.system.servos[servo].axes
            msg += '\r\n'
            exp_response = 'setpos:0=%s,0,0,0' % servo
            exp_response += (',%s' % pos) * self.system.servos[servo].axes
            exp_response += '\r\n'
            exp_response = '?%s@%s' % (exp_response, exp_response)
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_setpos_wrong_axes_number(self):
        for servo in range(4):
            exp_response = '!NAK_setpos:0=%s' % servo
            exp_response += ',cannot set the position\r\n'
            exp_response = exp_response * 2

            msg = '#setpos:0=%s,0,0' % servo
            msg += ',0' * 15  # Too many axes
            msg += '\r\n'
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

            msg = '#setpos:0=%s,0,0,0\r\n' % servo  # No positions
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_setpos_nak(self):
        servo = 1
        self.system.system_setpos_NAK()
        msg = '#setpos:0=%s,0,1.1,0x0002\r\n' % servo
        exp_response = '!NAK_setpos:0=%s' % servo
        exp_response += ',cannot set the position\r\n'
        exp_response = exp_response * 2
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, exp_response)

    def test_setpos_nak_ack(self):
        self.test_setpos_nak()
        self.system.system_setpos_ACK()
        self.test_setpos()

    def test_setup(self):
        for servo in range(4):
            msg = '#setup:0=%s\r\n' % servo
            exp_response = '?%s@%s' % (msg[1:], msg[1:])
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_multiple_setup_timer_restarted(self):
        for servo in range(4):
            for _ in range(2):
                msg = '#setup:0=%s\r\n' % servo
                exp_response = '?%s@%s' % (msg[1:], msg[1:])
                for byte in msg[:-1]:
                    self.assertTrue(self.system.parse(byte))
                response = self.system.parse(msg[-1])
                self.assertEqual(response, exp_response)

    def test_setup_with_params(self):
        for servo in range(4):
            msg = '#setup:0=%s,0,1.1,0x0002\r\n' % servo
            exp_response = 'setup:0=%s,0,1.1,2\r\n' % servo
            exp_response = '?%s@%s' % (exp_response, exp_response)
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_stow(self):
        for servo in range(4):
            msg = '#stow:0=%s\r\n' % servo
            exp_response = '?%s@%s' % (msg[1:], msg[1:])
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_stow_with_params(self):
        for servo in range(4):
            msg = '#stow:0=%s,0,1.1,0x0002\r\n' % servo
            exp_response = 'stow:0=%s,0,1.1,2\r\n' % servo
            exp_response = '?%s@%s' % (exp_response, exp_response)
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            response = self.system.parse(msg[-1])
            self.assertEqual(response, exp_response)

    def test_drive_cabinet_wrong_key(self):
        for servo in range(4):
            self.system.servos[servo].dc.set_state('dummy')

    def test_unknown_command(self):
        for servo in range(4):
            msg = '#unknown:0=%s\r\n' % servo
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            with self.assertRaises(ValueError):
                self.system.parse(msg[-1])

    def test_wrong_parameters(self):
        for servo in range(4):
            msg = '#getstatus:0=%s,dummy\r\n' % servo
            for byte in msg[:-1]:
                self.assertTrue(self.system.parse(byte))
            with self.assertRaises(ValueError):
                self.system.parse(msg[-1])

    def test_history(self):
        before = Servo.ctime() - 10000000
        self.test_setpos(0)
        self.test_setpos(1000)
        for servo in range(4):
            # Check if interpolation is correct
            t0 = self.system.servos[servo].history.history[-2][0]
            t1 = self.system.servos[servo].history.history[-1][0]
            midtime = (t0 + t1) / 2
            response = self.system.servos[servo].history.get(midtime)
            timestamp = response[0]
            self.assertEqual(midtime, timestamp)
            positions = response[1:]
            for position in positions:
                position = int(round(position))
                self.assertEqual(position, 500)

            # Read last inserted positions
            response = self.system.servos[servo].history.get()
            timestamp = response[0]
            self.assertEqual(t1, timestamp)
            positions = response[1:]
            for position in positions:
                position = int(round(position))
                self.assertEqual(position, 1000)

            # Read first inserted positions
            response = self.system.servos[servo].history.get(before)
            exp_timestamp = self.system.servos[servo].history.history[0][0]
            timestamp = response[0]
            self.assertEqual(timestamp, exp_timestamp)
            positions = response[1:]
            for position in positions:
                position = int(round(position))
                self.assertEqual(position, 0)

            # Clean positions after t0
            self.system.servos[servo].history.clean(t0 + 1)
            response = self.system.servos[servo].history.get()
            timestamp = response[0]
            self.assertEqual(t0, timestamp)
            positions = response[1:]
            for position in positions:
                position = int(round(position))
                self.assertEqual(position, 0)


if __name__ == '__main__':
    unittest.main()
