import unittest
import time
from simulators.active_surface import command_library, System
from simulators import utils

byte_ack = '\x06'
byte_nak = '\x15'


class TestCommandLibrary(unittest.TestCase):

    @staticmethod
    def _compose(command, usd_index=None, address_on_response=True):
        if usd_index is None:
            cmd = '\x00'
            cmd += utils.int_to_bytes(
                val=len(command),
                n_bytes=1
            )
        else:
            length = bin(len(command))[2:].zfill(3)
            address = bin(usd_index)[2:].zfill(5)
            cmd = utils.int_to_bytes(
                val=utils.twos_to_int(length + address),
                n_bytes=1
            )

        if address_on_response:
            cmd = b'\xFC' + cmd
        else:
            cmd = b'\xFA' + cmd

        cmd += command
        cmd += utils.checksum(cmd)
        return cmd

    def test_out_of_range_usd_index(self):
        with self.assertRaises(IndexError):
            command_library.soft_reset(usd_index=100)

    def test_wrong_usd_index_type(self):
        with self.assertRaises(TypeError):
            command_library.soft_reset(usd_index='foo')

    def test_soft_reset(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.soft_reset(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x01',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.soft_reset(
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x01',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_soft_trigger(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.soft_trigger(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x02',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.soft_trigger(
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x02',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_get_version(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.get_version(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x10',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.get_version(
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x10',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_soft_stop(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.soft_stop(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x11',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.soft_stop(
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x11',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_get_position(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.get_position(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x12',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.get_position(
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x12',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_get_status(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.get_status(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x13',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.get_status(
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x13',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_driver_type(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.get_driver_type(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x14',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.get_driver_type(
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x14',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_set_min_frequency(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_min_frequency(
                    frequency=20,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x20\x00\x14',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_min_frequency(
                frequency=20,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x20\x00\x14',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_min_frequency(self):
        with self.assertRaises(TypeError):
            command_library.set_min_frequency(frequency='foo')

    def test_set_max_frequency(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_max_frequency(
                    frequency=10000,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x21\x27\x10',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_max_frequency(
                frequency=10000,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x21\x27\x10',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_max_frequency(self):
        with self.assertRaises(TypeError):
            command_library.set_max_frequency(frequency='foo')

    def test_set_slope_multiplier(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_slope_multiplier(
                    multiplier=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x22\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_slope_multiplier(
                multiplier=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x22\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_slope_multiplier(self):
        with self.assertRaises(TypeError):
            command_library.set_slope_multiplier(multiplier='foo')

    def test_set_reference_position(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_reference_position(
                    position=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x23\x00\x00\x00\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_reference_position(
                position=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x23\x00\x00\x00\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_reference_position(self):
        with self.assertRaises(TypeError):
            command_library.set_reference_position(position='foo')

    def test_set_out_of_range_reference_position(self):
        with self.assertRaises(ValueError):
            command_library.set_reference_position(position=10000000000)

    def test_set_io_pins(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x25\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.set_io_pins(
                    byte_value=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.set_io_pins(
                    byte_value='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_io_pins(
                byte_value=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x25\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_io_pins(self):
        with self.assertRaises(TypeError):
            command_library.set_io_pins(byte_value='foo')

    def test_set_resolution(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x26\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.set_resolution(
                    resolution=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.set_resolution(
                    resolution='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_resolution(
                resolution=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x26\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_resolution(self):
        with self.assertRaises(TypeError):
            command_library.set_resolution(resolution='foo')

    def test_reduce_current(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x27\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.reduce_current(
                    byte_value=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.reduce_current(
                    byte_value='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.reduce_current(
                byte_value=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x27\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_reduce_current(self):
        with self.assertRaises(TypeError):
            command_library.reduce_current(byte_value='foo')

    def test_set_response_delay(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_response_delay(
                    delay=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x28\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_response_delay(
                delay=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x28\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_response_delay(self):
        with self.assertRaises(TypeError):
            command_library.set_response_delay(delay='foo')

    def test_toggle_delayed_execution(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x29\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.toggle_delayed_execution(
                    byte_value=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.toggle_delayed_execution(
                    byte_value='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.toggle_delayed_execution(
                byte_value=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x29\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_toggle_delayed_execution(self):
        with self.assertRaises(TypeError):
            command_library.toggle_delayed_execution(byte_value='foo')

    def test_set_absolute_position(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_absolute_position(
                    position=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x30\x00\x00\x00\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_absolute_position(
                position=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x30\x00\x00\x00\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_absolute_position(self):
        with self.assertRaises(TypeError):
            command_library.set_absolute_position(position='foo')

    def test_set_out_of_range_absolute_position(self):
        with self.assertRaises(ValueError):
            command_library.set_absolute_position(position=10000000000)

    def test_set_relative_position(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_relative_position(
                    position=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x31\x00\x00\x00\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_relative_position(
                position=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x31\x00\x00\x00\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_relative_position(self):
        with self.assertRaises(TypeError):
            command_library.set_relative_position(position='foo')

    def test_set_out_of_range_relative_position(self):
        with self.assertRaises(ValueError):
            command_library.set_relative_position(position=10000000000)

    def test_rotate(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.rotate(
                    direction=1,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x32\x01',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.rotate(
                direction=1,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x32\x01',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_rotate(self):
        with self.assertRaises(TypeError):
            command_library.rotate(direction='foo')

    def test_set_velocity(self):
        for address_on_response in [True, False]:
            for i in range(32):
                cmd = command_library.set_velocity(
                    velocity=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                expected_cmd = self._compose(
                    '\x35\x00\x00\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_velocity(
                velocity=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x35\x00\x00\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_velocity(self):
        with self.assertRaises(TypeError):
            command_library.set_velocity(velocity='foo')

    def test_set_stop_io(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x2A\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.set_stop_io(
                    byte_value=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.set_stop_io(
                    byte_value='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_stop_io(
                byte_value=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x2A\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_stop_io(self):
        with self.assertRaises(TypeError):
            command_library.set_stop_io(byte_value='foo')

    def test_set_positioning_io(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x2B\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.set_positioning_io(
                    byte_value=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.set_positioning_io(
                    byte_value='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_positioning_io(
                byte_value=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x2B\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_positioning_io(self):
        with self.assertRaises(TypeError):
            command_library.set_positioning_io(byte_value='foo')

    def test_set_home_io(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x2C\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.set_home_io(
                    byte_value=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.set_home_io(
                    byte_value='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_home_io(
                byte_value=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x2C\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_home_io(self):
        with self.assertRaises(TypeError):
            command_library.set_home_io(byte_value='foo')

    def test_set_working_mode(self):
        for address_on_response in [True, False]:
            for i in range(32):
                expected_cmd = self._compose(
                    '\x2D\x00\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                cmd = command_library.set_working_mode(
                    byte_value=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)
                cmd = command_library.set_working_mode(
                    byte_value='\x00',
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(cmd, expected_cmd)

            cmd = command_library.set_working_mode(
                byte_value=0,
                address_on_response=address_on_response
            )
            expected_cmd = self._compose(
                '\x2D\x00\x00',
                address_on_response=address_on_response
            )
            self.assertEqual(cmd, expected_cmd)

    def test_wrong_set_working_mode(self):
        with self.assertRaises(TypeError):
            command_library.set_working_mode(byte_value='foo')


class TestASParse(unittest.TestCase):

    def setUp(self):
        self.system = System()
        # Set the response delay to 0 to speed up the tests
        for driver in self.system.drivers:
            driver.delay_multiplier = 0

    def tearDown(self):
        del self.system

    def _send_cmd(self, cmd):
        """This method is useful to send the whole command without repeating
        the `for` loop every test. If an exception is expected this method can
        be called from inside a `assertRaises` block."""
        for byte in cmd[:-1]:
            self.assertTrue(self.system.parse(byte))
        return self.system.parse(cmd[-1])

    def _test_wrong_cmd(self, command):
        """This method receives a wrong command string, it builds the whole
        command around it and sends it to every driver first in a separate
        transmission and then in a broadcast one. For each driver it checks
        that the response is equal to `nak` for a single driver transmission,
        or equal to `True` for a broadcast one, as expected by the protocol.
        """
        binary_length = bin(len(command))[2:].zfill(3)
        for i in range(len(self.system.drivers)):
            binary_index = bin(i)[2:].zfill(5)
            byte_nbyte_address = binary_length + binary_index
            byte_nbyte_address = utils.binary_to_bytes(byte_nbyte_address)

            for header in ['\xFA', '\xFC']:
                msg = header
                msg += byte_nbyte_address
                msg += command
                msg += utils.checksum(msg)
                self.assertEqual(self._send_cmd(msg), byte_nak)

        for header in ['\xFA', '\xFC']:
            msg = header
            msg += '\x00'  # Test the broadcast command
            msg += utils.int_to_bytes(len(command), 1)
            msg += command
            msg += utils.checksum(msg)
            self.assertTrue(self._send_cmd(msg))

    def test_fa_header(self):
        """Return True when the first byte is the 0xFA header."""
        # '\xFA' header -> we do not get the driver address in the response
        self.assertTrue(self.system.parse('\xFA'))

    def test_fc_header(self):
        """Return True when the first byte is the 0xFC header."""
        # '\xFC' header -> we get the driver address in the response
        self.assertTrue(self.system.parse('\xFC'))

    def test_wrong_header(self):
        """Return False when the first byte is not an allowed header."""
        self.assertFalse(self.system.parse(b'w'))

    def test_broadcast(self):
        """Return True in case of broadcast byte (byte_switchall)."""
        self.system.parse('\xFA')  # Send the header
        self.assertTrue(self.system.parse('\x00'))  # Send broadcast byte

    def test_expected_second_byte(self):
        """The second byte should have the value 0x00 or > 0x1F."""
        self.system.parse('\xFA')  # Send the header
        self.assertTrue(self.system.parse('\xAF'))

    def test_wrong_second_byte(self):
        self.system.parse('\xFA')  # Send the header
        with self.assertRaises(ValueError):
            self.system.parse('\x0F')

    def test_wrong_message_length(self):
        # Declaring a lenght of 2 but sending 3 bytes
        msg = b'\xFA\x40\x01\x02\x03'
        msg += utils.checksum(msg)
        with self.assertRaises(ValueError):
            self._send_cmd(msg)

    def test_wrong_message_broadcast_length(self):
        # Declaring a lenght of 2 but sending 3 bytes
        msg = b'\xFA\x00\x02\x01\x02\x03'
        msg += utils.checksum(msg)
        with self.assertRaises(ValueError):
            self._send_cmd(msg)

    def test_unknown_command(self):
        msg = b'\xFA\x20\x00'
        msg += utils.checksum(msg)
        with self.assertRaises(ValueError):
            self._send_cmd(msg)

    def test_too_high_message_length(self):
        msg = b'\xFA\x00\x08'
        with self.assertRaises(ValueError):
            self._send_cmd(msg)

    def test_wait_for_header_after_wrong_message_lenght(self):
        msg = b'\xFA\x40\x01\x02\x01'  # The ckecksum is '0xC2'
        for byte in msg:
            try:
                self.system.parse(byte)
            except ValueError:
                pass
        self.assertFalse(self.system.parse(b'w'))
        self.assertTrue(self.system.parse('\xFA'))

    def test_soft_reset(self):
        """The system returns True for every proper byte, and
        returns the byte_ack when the message is completed."""
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.soft_reset(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_soft_reset(self):
        command = '\x01\x00'
        self._test_wrong_cmd(command)

    def test_broadcast_soft_reset(self):
        """A proper broadcast command always returns True, also when
        the message is completed."""
        for address_on_response in [True, False]:
            msg = command_library.soft_reset(
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_soft_trigger(self):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.soft_trigger(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_soft_trigger(self):
        command = '\x02\x00'
        self._test_wrong_cmd(command)

    def test_broadcast_soft_trigger(self):
        for address_on_response in [True, False]:
            msg = command_library.soft_trigger(
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_get_version(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the driver version
        expressed as a byte when the message is completed."""
        expected_version = '\x13'
        binary_length = bin(len(expected_version))[2:].zfill(3)
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.get_version(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                response = self._send_cmd(msg)

                expected_response = byte_ack

                binary_index = bin(i)[2:].zfill(5)
                byte_nbyte_address = binary_length + binary_index
                byte_nbyte_address = utils.binary_to_bytes(byte_nbyte_address)

                if address_on_response:
                    expected_response += '\xFC'
                    expected_response += byte_nbyte_address
                else:
                    expected_response += '\xFA'

                expected_response += expected_version
                expected_response += utils.checksum(expected_response)
                self.assertEqual(response, expected_response)

    def test_wrong_get_version(self):
        command = '\x10\x00'
        self._test_wrong_cmd(command)

    def test_broadcast_get_version(self):
        for address_on_response in [True, False]:
            msg = command_library.get_version(
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_soft_stop(self):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.soft_stop(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_soft_stop(self):
        command = '\x11\x00'
        self._test_wrong_cmd(command)

    def test_broadcast_soft_stop(self):
        for address_on_response in [True, False]:
            msg = command_library.soft_stop(
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg), byte_ack)

    def test_get_position(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver position
        expressed as 4 bytes when the message is completed."""
        expected_position = '\x00\x00\x00\x00'  # Default position is 0
        binary_length = bin(len(expected_position))[2:].zfill(3)
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.get_position(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                response = self._send_cmd(msg)

                expected_response = byte_ack

                binary_index = bin(i)[2:].zfill(5)
                byte_nbyte_address = binary_length + binary_index
                byte_nbyte_address = utils.binary_to_bytes(byte_nbyte_address)

                if address_on_response:
                    expected_response += '\xFC'
                    expected_response += byte_nbyte_address
                else:
                    expected_response += '\xFA'

                expected_response += expected_position
                expected_response += utils.checksum(expected_response)
                self.assertEqual(response, expected_response)

    def test_wrong_get_position(self):
        command = '\x12\x00'
        self._test_wrong_cmd(command)

    def test_broadcast_get_position(self):
        for address_on_response in [True, False]:
            msg = command_library.get_position(
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_get_status(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver status
        expressed as 3 bytes when the message is completed."""
        expected_status = '\x00\x20\x18'
        binary_length = bin(len(expected_status))[2:].zfill(3)
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.get_status(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                response = self._send_cmd(msg)

                expected_response = byte_ack

                binary_index = bin(i)[2:].zfill(5)
                byte_nbyte_address = binary_length + binary_index
                byte_nbyte_address = utils.binary_to_bytes(byte_nbyte_address)

                if address_on_response:
                    expected_response += '\xFC'
                    expected_response += byte_nbyte_address
                else:
                    expected_response += '\xFA'

                expected_response += expected_status
                expected_response += utils.checksum(expected_response)
                self.assertEqual(response, expected_response)

    def test_wrong_get_status(self):
        command = '\x13\x00'
        self._test_wrong_cmd(command)

    def test_broadcast_get_status(self):
        for address_on_response in [True, False]:
            msg = command_library.get_status(
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_get_driver_type(self):
        """The system returns True for every proper byte, and
        returns the byte_ack followed by the current driver type
        expressed as a byte when the message is completed."""
        expected_type = '\x20'  # Default type is USD50XXX
        binary_length = bin(len(expected_type))[2:].zfill(3)
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.get_driver_type(
                    usd_index=i,
                    address_on_response=address_on_response
                )
                response = self._send_cmd(msg)

                expected_response = byte_ack

                binary_index = bin(i)[2:].zfill(5)
                byte_nbyte_address = binary_length + binary_index
                byte_nbyte_address = utils.binary_to_bytes(byte_nbyte_address)

                if address_on_response:
                    expected_response += '\xFC'
                    expected_response += byte_nbyte_address
                else:
                    expected_response += '\xFA'

                expected_response += expected_type
                expected_response += utils.checksum(expected_response)
                self.assertEqual(response, expected_response)

    def test_wrong_get_driver_type(self):
        command = '\x14\x00'
        self._test_wrong_cmd(command)

    def test_broadcast_get_driver_type(self):
        for address_on_response in [True, False]:
            msg = command_library.get_driver_type(
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_in_range_min_frequency(self, frequency=20):
        """Setting min freq to 20Hz, allowed range is 20-10000Hz, so the
        system returns the byte_ack"""
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_min_frequency(
                    frequency=frequency,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_broadcast_set_in_range_min_frequency(self, frequency=20):
        for address_on_response in [True, False]:
            msg = command_library.set_min_frequency(
                frequency=frequency,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_out_range_min_frequency(self):
        """Setting min freq to 10Hz, outside the allowed range, so the system
        returns the byte_nak"""
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_min_frequency(
                    frequency=10,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_nak)

    def test_broadcast_set_out_range_min_frequency(self):
        for address_on_response in [True, False]:
            msg = command_library.set_min_frequency(
                frequency=10,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_wrong_set_min_frequency(self):
        command = b'\x20\x20'
        self._test_wrong_cmd(command)

    def test_set_exceeding_min_frequency(self):
        self.test_set_in_range_max_frequency(frequency=1000)
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_min_frequency(
                    frequency=10000,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_nak)

    def test_set_in_range_max_frequency(self, frequency=10000):
        """Setting max freq to 10000Hz, allowed range is 20-10000Hz, so the
        system returns the byte_ack"""
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_max_frequency(
                    frequency=frequency,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_broadcast_set_in_range_max_frequency(self, frequency=10000):
        for address_on_response in [True, False]:
            msg = command_library.set_max_frequency(
                frequency=frequency,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_out_range_max_frequency(self):
        """Setting max freq to 11000Hz, outside the allowed range,
        so the system returns the byte_nak"""
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_max_frequency(
                    frequency=11000,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_nak)

    def test_broadcast_set_out_range_max_frequency(self):
        for address_on_response in [True, False]:
            msg = command_library.set_max_frequency(
                frequency=11000,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_wrong_set_max_frequency(self):
        command = '\x21\x21'
        self._test_wrong_cmd(command)

    def test_set_exceeding_max_frequency(self):
        self.test_set_in_range_min_frequency(frequency=1000)
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_max_frequency(
                    frequency=20,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_nak)

    def test_set_slope_multiplier(self):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_slope_multiplier(
                    multiplier=10,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_slope_multiplier(self):
        # Send no multiplier value
        command = '\x22'
        self._test_wrong_cmd(command)

    def test_broadcast_set_slope_multiplier(self):
        for address_on_response in [True, False]:
            msg = command_library.set_slope_multiplier(
                multiplier=10,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_reference_position(self):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_reference_position(
                    position=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_reference_position(self):
        command = '\x23'
        self._test_wrong_cmd(command)

    def test_broadcast_set_reference_position(self):
        for address_on_response in [True, False]:
            msg = command_library.set_reference_position(
                position=0,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_io_pins(self):
        for byte_value in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.set_io_pins(
                        byte_value=byte_value,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_io_pins(self):
        command = '\x25'
        self._test_wrong_cmd(command)

    def test_broadcast_set_io_pins(self):
        for byte_value in range(256):
            for address_on_response in [True, False]:
                msg = command_library.set_io_pins(
                    byte_value=byte_value,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_set_resolution(self):
        for resolution in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.set_resolution(
                        resolution=resolution,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_resolution(self):
        command = '\x26'
        self._test_wrong_cmd(command)

    def test_broadcast_set_resolution(self):
        for resolution in range(256):
            for address_on_response in [True, False]:
                msg = command_library.set_resolution(
                    resolution=resolution,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_reduce_current(self):
        for byte_value in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.reduce_current(
                        byte_value=byte_value,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_reduce_current(self):
        command = '\x27'
        self._test_wrong_cmd(command)

    def test_broadcast_reduce_current(self):
        for byte_value in range(256):
            for address_on_response in [True, False]:
                msg = command_library.reduce_current(
                    byte_value=byte_value,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_set_finite_delay(self):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_response_delay(
                    delay=0,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_broadcast_set_finite_delay(self):
        for address_on_response in [True, False]:
            msg = command_library.set_response_delay(
                delay=0,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_infinite_delay(self):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_response_delay(
                    delay=255,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_broadcast_set_inifinte_delay(self):
        for address_on_response in [True, False]:
            msg = command_library.set_response_delay(
                delay=255,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_wrong_set_delay(self):
        command = '\x28'
        self._test_wrong_cmd(command)

    def test_toggle_delayed_execution(self):
        for byte_value in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.toggle_delayed_execution(
                        byte_value=byte_value,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_toggle_delayed_execution(self):
        command = '\x29'
        self._test_wrong_cmd(command)

    def test_broadcast_toggle_delayed_execution(self):
        for byte_value in range(256):
            for address_on_response in [True, False]:
                msg = command_library.toggle_delayed_execution(
                    byte_value=byte_value,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_set_absolute_position(self, position=0):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_absolute_position(
                    position=position,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_absolute_position(self):
        command = '\x30'
        self._test_wrong_cmd(command)

    def test_broadcast_set_absolute_position(self):
        for address_on_response in [True, False]:
            msg = command_library.set_absolute_position(
                position=0,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_relative_position(self, position=0):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_relative_position(
                    position=position,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_relative_position(self):
        command = '\x31'
        self._test_wrong_cmd(command)

    def test_broadcast_set_relative_position(self):
        for address_on_response in [True, False]:
            msg = command_library.set_relative_position(
                position=0,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_rotate(self, should_fail=False):
        """The driver starts to rotate according to its set velocity.
        The last byte of the message (before the checksum)
        holds an int in twos complement notation, its sign (+ or -)
        represents the direction in which the motor will rotate."""
        if should_fail:
            expected_response = byte_nak
        else:
            expected_response = byte_ack
        for direction in [-1, 1]:
            for address_on_response in [True, False]:
                for i in range(len(self.system.drivers)):
                    msg = command_library.rotate(
                        direction=direction,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), expected_response)
                self.test_soft_stop()
                time.sleep(0.025)

    def test_wrong_rotate(self):
        command = '\x32'
        self._test_wrong_cmd(command)

    def test_broadcast_rotate(self):
        for direction in [-1, 1]:
            for address_on_response in [True, False]:
                msg = command_library.rotate(
                    direction=direction,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_set_velocity(self, velocity=0):
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_velocity(
                    velocity=velocity,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_set_in_range_velocity(self):
        """Setting velocity in a range between -100000 and +100000
        tenths of Hz."""
        starting_pos = []
        for driver in self.system.drivers:
            starting_pos.append(driver.current_position)

        self.test_set_velocity(100000)

        time.sleep(0.01)

        current_pos = []
        for driver in self.system.drivers:
            current_pos.append(driver.current_position)

        for i in range(len(self.system.drivers)):
            self.assertNotEqual(starting_pos[i], current_pos[i])

    def test_broadcast_set_in_range_velocity(self):
        for address_on_response in [True, False]:
            msg = command_library.set_velocity(
                velocity=0,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_set_out_range_velocity(self):
        """Setting velocity outside allowed range. (8388607 tenths of Hz)."""
        for i in range(len(self.system.drivers)):
            for address_on_response in [True, False]:
                msg = command_library.set_velocity(
                    velocity=8388607,
                    usd_index=i,
                    address_on_response=address_on_response
                )
                self.assertEqual(self._send_cmd(msg), byte_nak)

    def test_broadcast_set_out_range_velocity(self):
        for address_on_response in [True, False]:
            msg = command_library.set_velocity(
                velocity=8388607,
                address_on_response=address_on_response
            )
            self.assertTrue(self._send_cmd(msg))

    def test_wrong_set_velocity(self):
        command = '\x35'
        self._test_wrong_cmd(command)

    def test_set_stop_io(self):
        for byte_value in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.set_stop_io(
                        byte_value=byte_value,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_stop_io(self):
        command = '\x2A'
        self._test_wrong_cmd(command)

    def test_broadcast_set_stop_io(self):
        for byte_value in range(256):
            for address_on_response in [True, False]:
                msg = command_library.set_stop_io(
                    byte_value=byte_value,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_set_positioning_io(self):
        for byte_value in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.set_positioning_io(
                        byte_value=byte_value,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_positioning_io(self):
        command = '\x2B'
        self._test_wrong_cmd(command)

    def test_broadcast_set_positioning_io(self):
        for byte_value in range(256):
            for address_on_response in [True, False]:
                msg = command_library.set_positioning_io(
                    byte_value=byte_value,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_set_home_io(self):
        for byte_value in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.set_home_io(
                        byte_value=byte_value,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_home_io(self):
        command = '\x2C'
        self._test_wrong_cmd(command)

    def test_broadcast_set_home_io(self):
        for byte_value in range(256):
            for address_on_response in [True, False]:
                msg = command_library.set_home_io(
                    byte_value=byte_value,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_set_working_mode(self):
        for byte_value in range(256):
            for i in range(len(self.system.drivers)):
                for address_on_response in [True, False]:
                    msg = command_library.set_working_mode(
                        byte_value=byte_value,
                        usd_index=i,
                        address_on_response=address_on_response
                    )
                    self.assertEqual(self._send_cmd(msg), byte_ack)

    def test_wrong_set_working_mode(self):
        command = '\x2D'
        self._test_wrong_cmd(command)

    def test_broadcast_set_working_mode(self):
        for byte_value in range(256):
            for address_on_response in [True, False]:
                msg = command_library.set_working_mode(
                    byte_value=byte_value,
                    address_on_response=address_on_response
                )
                self.assertTrue(self._send_cmd(msg))

    def test_delayed_execution(self):
        self.test_toggle_delayed_execution()
        self.test_set_absolute_position(2000)
        self.test_set_relative_position(4000)

        for driver in self.system.drivers:
            self.assertEqual(driver.current_position, 0)

        self.test_soft_trigger()

        time.sleep(0.25)
        for driver in self.system.drivers:
            self.assertEqual(driver.current_position, 2000)

        self.test_soft_trigger()

        time.sleep(0.25)
        for driver in self.system.drivers:
            self.assertEqual(driver.current_position, 4000)

    def test_rotate_while_moving(self):
        self.test_set_in_range_velocity()
        self.test_rotate(should_fail=True)

    def test_multiple_set_velocity(self):
        self.test_set_in_range_velocity()
        self.test_set_velocity()

    def test_velocity_upper_limit(self):
        for driver in self.system.drivers:
            driver.current_position = 2147483640

        self.test_set_velocity(1000)
        time.sleep(0.3)

    def test_velocity_lower_limit(self):
        for driver in self.system.drivers:
            driver.current_position = -2147483640

        self.test_set_velocity(-1000)
        time.sleep(0.3)


if __name__ == '__main__':
    unittest.main()
