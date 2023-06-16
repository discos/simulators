import unittest
from simulators.lo import System


class TestGenericLocalOscillator(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='generic_LO')

    def test_set_power(self, power=10):
        msg = f'POWER {power} dBm\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.power, power)

    def test_set_wrong_power(self, power=10):
        # dBm suffix missing
        msg = f'POWER {power}\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.power, power)

        # wrong dBm suffix
        msg = f'POWER {power} dbm\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.power, power)

        # String instead of int power
        msg = 'POWER dummy dBm\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.power, power)

    def test_get_power(self):
        power = 20
        self.test_set_power(power=power)
        msg = 'POWER?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{power}\n')

    def test_set_get_power(self, power=10):
        msg = f'POWER {power} dBm;POWER?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{power}\n')

    def test_set_frequency(self, frequency=10):
        msg = f'FREQ {frequency} MHZ\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.frequency, frequency)

    def test_set_wrong_frequency(self, frequency=10):
        # MHZ suffix missing
        msg = f'FREQ {frequency}\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.frequency, frequency)

        # wrong MHZ suffix
        msg = f'FREQ {frequency} MHz\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.frequency, frequency)

        # String instead of int frequency
        msg = 'FREQ dummy MHZ\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertNotEqual(self.system.frequency, frequency)

    def test_get_frequency(self):
        frequency = 20
        self.test_set_frequency(frequency=frequency)
        msg = 'FREQ?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{frequency * 1000000}\n')

    def test_set_get_frequency(self, frequency=10):
        msg = f'FREQ {frequency} MHZ;FREQ?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, f'{frequency * 1000000}\n')

    def test_read_status(self):
        msg = 'SYST:ERR?\n'
        for byte in msg[:-1]:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse(msg[-1])
        self.assertEqual(response, '0,\"No error\"\n')

    def test_wrong_empty_commands(self):
        msg = 'dummy;;\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))


class TestWLocalOscillator(unittest.TestCase):

    def setUp(self):
        self.system = System(system_type='w_LO')

    def test_enable_USB_devs(self, w_usb_devs=1):
        msg = 'enable USB_devs\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_USB_devs, w_usb_devs)

    def test_disable_w_LO_Inter(self, w_usb_devs=0):
        msg = 'disable USB_devs\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_USB_devs, w_usb_devs)

    def test_set_w_LO_freq_PolH(self, polh=12.23):
        msg = 'set W_LO_freq_PolH=12.23\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_lo_freq_polH, polh)

    def test_set_w_LO_freq_PolV(self, polv=31.82):
        msg = 'set W_LO_freq_PolV=31.82\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_lo_freq_polV, polv)

    def test_get_w_LO_PolH(self, polh=12.23):
        msg = 'set W_LO_freq_PolH=12.23\r\nget W_LO_PolH\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'{self.system.w_lo_freq_polH}',
            f'{polh}')

    def test_get_w_LO_PolV(self, polv=31.82):
        msg = 'set W_LO_freq_PolV=31.82\r\nget W_LO_PolV\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'{self.system.w_lo_freq_polV}',
            f'{polv}')

    def test_get_w_LO_Pols(self, polh=12.23, polv=31.82):
        msg = "set W_LO_freq_PolH=12.23\r\n" +\
            "set W_LO_freq_PolV=31.82\r\nget W_LO_Pols\r\n"
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'{self.system.w_lo_freq_polH},'
            f'{self.system.w_lo_freq_polV}'),
            (f'{polh},' f'{polv}'))

    def test_get_w_LO_Synths_Temp(self, c1=0., c2=0.):
        msg = 'get W_LO_Synths_Temp\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'{self.system.w_LO_Synths_Temp[0]}',
            f'{self.system.w_LO_Synths_Temp[1]}'),
            (f'{c1}', f'{c2}'))

    def test_get_w_LO_HKP_Temp(self, c1=0., c2=0., c3=0., c4=0.):
        msg = 'get W_LO_HKP_Temp\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'{self.system.w_LO_HKP_Temp[0]}',
            f'{self.system.w_LO_HKP_Temp[1]}',
            f'{self.system.w_LO_HKP_Temp[2]}',
            f'{self.system.w_LO_HKP_Temp[3]}'),
            (f'{c1}', f'{c2}', f'{c3}', f'{c4}'))

    def test_set_W_LO_RefH(self, w_lo_refh='INT'):
        msg = 'set W_LO_RefH=INT\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_LO_refH, w_lo_refh)

    def test_set_W_LO_RefV(self, w_lo_refv='INT'):
        msg = 'set W_LO_RefV=INT\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.w_LO_refV, w_lo_refv)

    def test_get_W_LO_RefH(self, w_lo_refh='INT'):
        msg = 'set W_LO_RefH=INT\r\nget W_LO_RefH\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'{self.system.w_LO_refH}',
            f'{w_lo_refh}')

    def test_get_W_LO_RefV(self, w_lo_refv='INT'):
        msg = 'set W_LO_RefV=INT\r\nget W_LO_RefV\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'{self.system.w_LO_refV}',
            f'{w_lo_refv}')

    def test_get_w_LO_status(self, stat_polh=0, stat_polv=0):
        msg = 'get W_LO_status\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'{self.system.status_W_LO_PolH}'
            f'{self.system.status_W_LO_PolV}'),
            (f'{stat_polh}' f'{stat_polv}'))

    def test_set_LO_att_PolH(self, att_polh=9.22):
        msg = 'set LO_att_PolH=9.22\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.lo_att_polH, att_polh)

    def test_set_LO_att_PolV(self, att_polv=12.51):
        msg = 'set LO_att_PolV=12.51\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(self.system.lo_att_polV, att_polv)

    def test_get_LO_att_PolH(self, att_polh=9.22):
        msg = 'set LO_att_PolH=9.22\r\nget LO_att_PolH\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'{self.system.lo_att_polH}',
            f'{att_polh}')

    def test_get_LO_att_PolV(self, att_polv=12.51):
        msg = 'set LO_att_PolV=12.51\r\nget LO_att_PolV\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            f'{self.system.lo_att_polV}',
            f'{att_polv}')

    def test_get_LO_atts(self, att_polh=9.22, att_polv=12.51):
        msg = 'set LO_att_PolH=9.22\r\nset LO_att_PolV=12.51\
        \r\nget LO_atts\r\n'
        for byte in msg:
            self.assertTrue(self.system.parse(byte))
        self.assertEqual(
            (f'{self.system.lo_att_polH},'
            f'{self.system.lo_att_polV}'),
            (f'{att_polh},' f'{att_polv}'))


class TestLocalOscillatorUnknownType(unittest.TestCase):

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            self.system = System(system_type='unknown')


if __name__ == '__main__':
    unittest.main()
