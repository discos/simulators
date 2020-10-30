import unittest
from datetime import datetime, timedelta
from simulators.receiver import System
from simulators.receiver.DEFINITIONS import CMD_SOH, CMD_STX, CMD_ETX, CMD_EOT
from simulators.receiver.DEFINITIONS import VERSION


def checksum(msg):
    chksum = 0
    for byte in msg:
        chksum = chksum ^ ord(byte)
    return chr(chksum)


class TestReceiver(unittest.TestCase):

    def setUp(self):
        self.system = System()

    def test_wrong_header(self):
        self.assertFalse(self.system.parse(CMD_EOT))

    def test_unknown_command(self):
        command = CMD_SOH + '\x01\x01\x51\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x51\x00\x01'
        self.assertEqual(answer, expected_answer)

    def test_unknown_command_broadcast(self):
        command = CMD_SOH + '\x7F\x01\x51\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = ''
        for slave in self.system.slaves.keys():
            expected_answer += CMD_STX
            expected_answer += '\x01'
            expected_answer += slave
            expected_answer += '\x51'
            expected_answer += '\x00'
            expected_answer += '\x01'
        self.assertEqual(answer, expected_answer)

    def test_unknown_command_broadcast_no_answer(self):
        command = CMD_SOH + '\x00\x01\x51\x00'
        for byte in command:
            self.assertTrue(self.system.parse(byte))

    def test_ext_command_wrong_checksum(self):
        command = CMD_SOH + '\x01\x01\x41\x00'
        command += chr(ord(checksum(command)) + 1)  # Add 1 to right checksum
        command += CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x41\x00\x02'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_inquiry(self, slave_index='\x01', expected_data='\x00' * 11):
        command = CMD_SOH + '%c\x01\x41\x00' % slave_index
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01%c\x41\x00\x00' % slave_index
        expected_answer += '\x0B%s' % expected_data   # Expected data
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_inquiry_slave_absent(self, slave_index='\x20'):
        command = CMD_SOH + '%c\x01\x41\x00' % slave_index
        command += checksum(command) + CMD_ETX
        for byte in command:
            self.assertTrue(self.system.parse(byte))

    def test_abbr_inquiry(self):
        command = CMD_SOH + '\x01\x01\x61\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x61\x00\x00'
        expected_answer += '\x0B' + '\x00' * 11  # Expected data
        self.assertEqual(answer, expected_answer)

    def test_abbr_inquiry_with_command(self):
        self.test_abbr_save()
        command = CMD_SOH + '\x01\x01\x61\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_header = CMD_STX + '\x01\x01\x61\x00\x00'
        expected_header += '\x0B\x64\x00\x00'
        unexpected_date = '\x00' * 8  # Date should not be all zeroes
        self.assertEqual(answer[:len(expected_header)], expected_header)
        self.assertNotEqual(answer[len(expected_header):], unexpected_date)

    def test_ext_reset(self):
        command = CMD_SOH + '\x01\x01\x42\x00'
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x42\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_reset(self):
        command = CMD_SOH + '\x01\x01\x62\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x62\x00\x00'
        self.assertEqual(answer, expected_answer)

    def test_ext_version(self):
        command = CMD_SOH + '\x01\x01\x43\x00'
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x43\x00\x00'
        expected_answer += '\x08' + VERSION
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_version(self):
        command = CMD_SOH + '\x01\x01\x63\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x63\x00\x00'
        expected_answer += '\x08' + VERSION
        self.assertEqual(answer, expected_answer)

    def test_ext_save(self):
        command = CMD_SOH + '\x01\x01\x44\x00'
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x44\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_save(self):
        command = CMD_SOH + '\x01\x01\x64\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x64\x00\x00'
        self.assertEqual(answer, expected_answer)

    def test_ext_restore(self):
        command = CMD_SOH + '\x01\x01\x45\x00'
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x45\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_restore(self):
        command = CMD_SOH + '\x01\x01\x65\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x65\x00\x00'
        self.assertEqual(answer, expected_answer)

    def test_ext_get_address(self, ):
        for slave in self.system.slaves.keys():
            command = CMD_SOH + '%c\x01\x46\x00' % slave
            command += checksum(command) + CMD_ETX
            for byte in command[:-1]:
                self.assertTrue(self.system.parse(byte))
            answer = self.system.parse(command[-1])
            expected_answer = CMD_STX + '\x01%c\x46\x00\x00' % slave
            expected_answer += '\x01%c' % slave
            expected_answer += checksum(expected_answer)
            expected_answer += CMD_EOT
            self.assertEqual(answer, expected_answer)

    def test_abbr_get_address(self):
        for slave in self.system.slaves.keys():
            command = CMD_SOH + '%c\x01\x66\x00' % slave
            for byte in command[:-1]:
                self.assertTrue(self.system.parse(byte))
            answer = self.system.parse(command[-1])
            expected_answer = CMD_STX + '\x01%c\x66\x00\x00' % slave
            expected_answer += '\x01%c' % slave
            self.assertEqual(answer, expected_answer)

    def test_ext_set_address(self):
        command = CMD_SOH + '\x01\x01\x47\x00'
        command += '\x01\x20'  # x20 is the new address
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        now = datetime.utcnow()
        expected_answer = CMD_STX + '\x01\x01\x47\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)
        # Check that the old slave address is now absent
        self.test_ext_inquiry_slave_absent('\x01')
        # Retrieve the last command with the new address
        expected_inquiry = '\x47\x00\x00'
        expected_inquiry += chr(int(str(now.year)[:2]))
        expected_inquiry += chr(int(str(now.year)[2:]))
        expected_inquiry += chr(now.month)
        expected_inquiry += chr(now.day)
        expected_inquiry += chr(now.hour)
        expected_inquiry += chr(now.minute)
        expected_inquiry += chr(now.second)
        expected_inquiry += chr(int(round(now.microsecond / 10000.)))
        self.test_ext_inquiry(
            slave_index='\x20',
            expected_data=expected_inquiry
        )

    def test_abbr_set_address(self):
        command = CMD_SOH + '\x01\x01\x67\x00'
        command += '\x01\x20'  # x20 is the new address
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        now = datetime.utcnow()
        expected_answer = CMD_STX + '\x01\x01\x67\x00\x00'
        self.assertEqual(answer, expected_answer)
        # Check that the old slave address is now absent
        self.test_ext_inquiry_slave_absent('\x01')
        # Retrieve the last command with the new address
        expected_inquiry = '\x67\x00\x00'
        expected_inquiry += chr(int(str(now.year)[:2]))
        expected_inquiry += chr(int(str(now.year)[2:]))
        expected_inquiry += chr(now.month)
        expected_inquiry += chr(now.day)
        expected_inquiry += chr(now.hour)
        expected_inquiry += chr(now.minute)
        expected_inquiry += chr(now.second)
        expected_inquiry += chr(int(round(now.microsecond / 10000.)))
        self.test_ext_inquiry(
            slave_index='\x20',
            expected_data=expected_inquiry
        )

    def test_ext_set_address_out_of_range(self):
        command = CMD_SOH + '\x01\x01\x47\x00'
        command += '\x01\xFF'  # xFF out of range
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x47\x00\x04'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_address_already_taken(self):
        command = CMD_SOH + '\x01\x01\x47\x00'
        command += '\x01\x02'  # x02 already taken
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x47\x00\x04'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_address_wrong_format(self):
        command = CMD_SOH + '\x01\x01\x47\x00'
        command += '\x02\x20\x00'
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x47\x00\x03'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_time(self, offset=timedelta(0)):
        command = CMD_SOH + '\x01\x01\x48\x00'
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        now = datetime.utcnow() + offset
        expected_answer = CMD_STX + '\x01\x01\x48\x00\x00\x08'
        # Insert a date placeholder, we check the date differently
        expected_answer += '\x00' * 8
        received_date = datetime(
            ord(answer[7]) * 100 + ord(answer[8]),  # Year
            ord(answer[9]),  # Month
            ord(answer[10]),  # Day
            ord(answer[11]),  # Hour
            ord(answer[12]),  # Minute
            ord(answer[13]),  # Second
            min(ord(answer[14]) * 10000, 999999)  # Microsecond
        )
        self.assertEqual(answer[:6], expected_answer[:6])
        self.assertAlmostEqual(
            now,
            received_date,
            delta=timedelta(seconds=.01)
        )

    def test_abbr_get_time(self, offset=timedelta(0)):
        command = CMD_SOH + '\x01\x01\x68\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        now = datetime.utcnow() + offset
        expected_answer = CMD_STX + '\x01\x01\x68\x00\x00\x08'
        # Insert a date placeholder, we check the date differently
        expected_answer += '\x00' * 8
        received_date = datetime(
            ord(answer[7]) * 100 + ord(answer[8]),  # Year
            ord(answer[9]),  # Month
            ord(answer[10]),  # Day
            ord(answer[11]),  # Hour
            ord(answer[12]),  # Minute
            ord(answer[13]),  # Second
            min(ord(answer[14]) * 10000, 999999)  # Microsecond
        )
        self.assertEqual(answer[:6], expected_answer[:6])
        self.assertAlmostEqual(
            now,
            received_date,
            delta=timedelta(seconds=.01)
        )

    def test_ext_set_time(self):
        command = CMD_SOH + '\x01\x01\x49\x00\x08'
        offset = timedelta(days=1)
        new_time = datetime.utcnow() + offset
        command += chr(int(str(new_time.year)[:2]))
        command += chr(int(str(new_time.year)[2:]))
        command += chr(new_time.month)
        command += chr(new_time.day)
        command += chr(new_time.hour)
        command += chr(new_time.minute)
        command += chr(new_time.second)
        command += chr(int(round(new_time.microsecond / 10000.)))
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x49\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)
        # Check that the offset is respected
        self.test_ext_get_time(offset=offset)

    def test_abbr_set_time(self):
        command = CMD_SOH + '\x01\x01\x69\x00\x08'
        offset = timedelta(days=1)
        new_time = datetime.utcnow() + offset
        command += chr(int(str(new_time.year)[:2]))
        command += chr(int(str(new_time.year)[2:]))
        command += chr(new_time.month)
        command += chr(new_time.day)
        command += chr(new_time.hour)
        command += chr(new_time.minute)
        command += chr(new_time.second)
        command += chr(int(round(new_time.microsecond / 10000.)))
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x69\x00\x00'
        self.assertEqual(answer, expected_answer)
        # Check that the offset is respected
        self.test_abbr_get_time(offset=offset)

    def test_ext_set_time_wrong_format(self):
        command = CMD_SOH + '\x01\x01\x49\x00\x06'
        offset = timedelta(days=1)
        new_time = datetime.utcnow() + offset
        command += chr(int(str(new_time.year)[:2]))
        command += chr(int(str(new_time.year)[2:]))
        command += chr(new_time.month)
        command += chr(new_time.day)
        command += chr(new_time.hour)
        command += chr(new_time.minute)
        # Omit seconds and microseconds
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x49\x00\x03'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_time_wrong_date(self):
        command = CMD_SOH + '\x01\x01\x49\x00\x08'
        command += '\x00' * 8  # We send a list of zeroes
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x49\x00\x04'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_frame(self, frame_size='\x7E'):
        command = CMD_SOH + '\x01\x01\x4A\x00'
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4A\x00\x00'
        expected_answer += '\x01%c' % frame_size
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_get_frame(self, frame_size='\x7E'):
        command = CMD_SOH + '\x01\x01\x6A\x00'
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x6A\x00\x00'
        expected_answer += '\x01%c' % frame_size
        self.assertEqual(answer, expected_answer)

    def test_ext_set_frame(self):
        command = CMD_SOH + '\x01\x01\x4B\x00'
        frame_size = '\x0A'
        command += '\x01%c' % frame_size
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4B\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)
        self.test_ext_get_frame(frame_size=frame_size)

    def test_ext_set_frame_wrong_format(self):
        command = CMD_SOH + '\x01\x01\x4B\x00'
        frame_size = '\x0A'
        command += '\x02%c\x01' % frame_size
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4B\x00\x03'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_frame_wrong_frame(self):
        command = CMD_SOH + '\x01\x01\x4B\x00'
        frame_size = '\x00'
        command += '\x01%c' % frame_size
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4B\x00\x08'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_set_frame(self):
        command = CMD_SOH + '\x01\x01\x6B\x00'
        frame_size = '\x0A'
        command += '\x01%c' % frame_size
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x6B\x00\x00'
        self.assertEqual(answer, expected_answer)
        self.test_abbr_get_frame(frame_size=frame_size)

    def test_ext_get_port(self):
        command = CMD_SOH + '\x01\x01\x4C\x00\x03'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4C\x00\x00'
        expected_answer += '\x01\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_port_wrong_format(self):
        command = CMD_SOH + '\x01\x01\x4C\x00\x01'
        data_type = '\x00'
        command += data_type
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4C\x00\x03'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_port_wrong_data_type(self):
        command = CMD_SOH + '\x01\x01\x4C\x00\x03'
        data_type = '\x1B'  # Unknown data type
        port_type = '\x00'
        port_number = '\x00'
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4C\x00\x09'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_port_wrong_port_type(self):
        command = CMD_SOH + '\x01\x01\x4C\x00\x03'
        data_type = '\x00'
        port_type = '\x80'  # Out of range
        port_number = '\x00'
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4C\x00\x0A'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_port_wrong_port_number(self):
        command = CMD_SOH + '\x01\x01\x4C\x00\x03'
        data_type = '\x00'
        port_type = '\00'
        port_number = '\x80'  # Out of range
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4C\x00\x0B'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_get_port(self):
        command = CMD_SOH + '\x01\x01\x6C\x00\x03'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        command += data_type + port_type + port_number
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x6C\x00\x00'
        expected_answer += '\x01\x00'
        self.assertEqual(answer, expected_answer)

    def test_ext_set_port(self):
        command = CMD_SOH + '\x01\x01\x4D\x00\x04'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4D\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_port_wrong_format(self):
        command = CMD_SOH + '\x01\x01\x4D\x00\x01'
        data_type = '\x00'
        command += data_type
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4D\x00\x03'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_port_wrong_data_type(self):
        command = CMD_SOH + '\x01\x01\x4D\x00\x04'
        data_type = '\x1B'  # Unknown data type
        port_type = '\x00'
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4D\x00\x09'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_port_wrong_port_type(self):
        command = CMD_SOH + '\x01\x01\x4D\x00\x04'
        data_type = '\x00'
        port_type = '\x80'  # Out of range
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4D\x00\x0A'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_port_wrong_port_number(self):
        command = CMD_SOH + '\x01\x01\x4D\x00\x04'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x80'  # Out of range
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4D\x00\x0B'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_set_port(self):
        command = CMD_SOH + '\x01\x01\x6D\x00\x04'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x6D\x00\x00'
        self.assertEqual(answer, expected_answer)

    def test_ext_get_data(self):
        command = CMD_SOH + '\x01\x01\x4E\x00\x03'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4E\x00\x00'
        expected_answer += '\x01\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_data_wrong_format(self):
        command = CMD_SOH + '\x01\x01\x4E\x00\x01'
        data_type = '\x00'
        command += data_type
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4E\x00\x03'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_data_wrong_data_type(self):
        command = CMD_SOH + '\x01\x01\x4E\x00\x03'
        data_type = '\x1B'  # Unknown data type
        port_type = '\x00'
        port_number = '\x00'
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4E\x00\x09'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_data_wrong_port_type(self):
        command = CMD_SOH + '\x01\x01\x4E\x00\x03'
        data_type = '\x00'
        port_type = '\x80'  # Out of range
        port_number = '\x00'
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4E\x00\x0A'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_get_data_wrong_port_number(self):
        command = CMD_SOH + '\x01\x01\x4E\x00\x03'
        data_type = '\x00'
        port_type = '\00'
        port_number = '\x80'  # Out of range
        command += data_type + port_type + port_number
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4E\x00\x0B'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_get_data(self):
        command = CMD_SOH + '\x01\x01\x6E\x00\x03'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        command += data_type + port_type + port_number
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x6E\x00\x00'
        expected_answer += '\x01\x00'
        self.assertEqual(answer, expected_answer)

    def test_ext_set_data(self):
        command = CMD_SOH + '\x01\x01\x4F\x00\x04'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4F\x00\x00'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_data_wrong_format(self):
        command = CMD_SOH + '\x01\x01\x4F\x00\x01'
        data_type = '\x00'
        command += data_type
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4F\x00\x03'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_data_wrong_data_type(self):
        command = CMD_SOH + '\x01\x01\x4F\x00\x04'
        data_type = '\x1B'  # Unknown data type
        port_type = '\x00'
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4F\x00\x09'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_data_wrong_port_type(self):
        command = CMD_SOH + '\x01\x01\x4F\x00\x04'
        data_type = '\x00'
        port_type = '\x80'  # Out of range
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4F\x00\x0A'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_ext_set_data_wrong_port_number(self):
        command = CMD_SOH + '\x01\x01\x4F\x00\x04'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x80'  # Out of range
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        command += checksum(command) + CMD_ETX
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x4F\x00\x0B'
        expected_answer += checksum(expected_answer)
        expected_answer += CMD_EOT
        self.assertEqual(answer, expected_answer)

    def test_abbr_set_data(self):
        command = CMD_SOH + '\x01\x01\x6F\x00\x04'
        data_type = '\x00'
        port_type = '\x00'
        port_number = '\x00'
        port_setting = '\x00'
        command += data_type + port_type + port_number + port_setting
        for byte in command[:-1]:
            self.assertTrue(self.system.parse(byte))
        answer = self.system.parse(command[-1])
        expected_answer = CMD_STX + '\x01\x01\x6F\x00\x00'
        self.assertEqual(answer, expected_answer)


if __name__ == '__main__':
    unittest.main()
