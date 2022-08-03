import unittest
import datetime
from xml.etree.ElementTree import fromstring
from simulators import weather_station


class TestWeatherStation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.sensors = {
            'th01': [26.0, 'heating temp [oC]'],
            'vh01': [0.0, 'heating voltage [V]'],
            'vs01': [7.7, 'supply voltage [V]'],
            'vr01': [3.52, 'rif. voltage [V]'],
            'dn01': [287.0, 'wind dir min [deg]'],
            'dm01': [289.0, 'wind dir ave [deg]'],
            'dx01': [292.0, 'wind dir max [deg]'],
            'sn01': [1.6, 'wind speed min [m/s]'],
            'sm01': [1.8, 'wind speed ave [m/s]'],
            'sx01': [1.9, 'wind speed max [m/s]'],
            'ta01': [23.0, 'air temp [oC]'],
            'ua01': [72.5, 'rel. humidity [%]'],
            'pa01': [940.9, 'air pressure [hPa]'],
            'rc01': [9.86, 'rain amount [mm]'],
            'rd01': [4240.0, 'rain duration [s]'],
            'ri01': [0.0, 'rain intensity [mm/h]'],
            'rp01': [-9999.9, 'rain peak duration [s]'],
            'hc01': [0.0, 'hail amount [hits/cm2]'],
            'hd01': [20.0, 'hail duration [s]'],
            'hi01': [0.0, 'hail intensity [hits/cm2h]'],
            'hp01': [-9999.9, 'hail peak duration [s]']
        }

        cls.err_string = (
            '<Sensor>'
            + '<Id>sintax error or sensor not found</Id>'
            + '<Val>1.000000</Val>'
            + '<Date>error</Date>'
            + '<Info>error</Info>'
            + '</Sensor>'
        )

    def setUp(self):
        self.system = weather_station.System()

    @staticmethod
    def _expected(
            sensor=None, val=None, date=None, info=None):  # pragma: no cover
        retval = {}
        if sensor:
            retval['Id'] = sensor
        if val:
            retval['Val'] = val
        if date:
            retval['Date'] = date
        if info:
            retval['Info'] = info
        return retval

    @staticmethod
    def _parseString(answer):  # pragma: no cover
        retval = {}
        for element in list(fromstring(answer)):
            retval[element.tag] = element.text
            if element.tag == 'Val':
                try:
                    retval[element.tag] = float(element.text)
                except ValueError:
                    pass
        return retval

    @staticmethod
    def _compare(expected, response):  # pragma: no cover
        for key in expected.keys():
            try:
                if not expected[key] == response[key]:
                    return False
            except KeyError:
                return False
        return True

    def test_wrong_starting_byte(self):
        self.assertFalse(self.system.parse('c'))

    def test_no_space_after_command(self):
        self.assertTrue(self.system.parse('r'))
        self.assertFalse(self.system.parse('c'))  # Should be ` `

    def test_read(self):
        for sensor, values in iter(self.sensors.items()):
            cmd = f'r {sensor}'
            for byte in cmd:
                self.assertTrue(self.system.parse(byte))
            response = self._parseString(self.system.parse('\n'))
            expected = self._expected(
                sensor=sensor,
                val=values[0],
                info=values[1]
            )
            self.assertTrue(self._compare(expected, response))

    def test_read_error(self):
        cmd = 'r unkn'
        for byte in cmd:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse('\n')
        self.assertEqual(response, self.err_string)

    def test_read_as_write(self):
        date = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        args = (list(self.sensors.keys())[0], 10.0, date)
        cmd = f'r {args[0]} {args[1]} {args[2]}'
        for byte in cmd:
            self.assertTrue(self.system.parse(byte))
        self.assertFalse(self.system.parse('\n'))

    def test_write(self):
        date = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        for sensor, values in iter(self.sensors.items()):
            args = (sensor, 10.0, date)
            cmd = f'w {args[0]} {args[1]} {args[2]}'
            for byte in cmd:
                self.assertTrue(self.system.parse(byte))
            response = self._parseString(self.system.parse('\n'))
            expected = self._expected(
                sensor=sensor,
                val=10.0,
                date=date,
                info=values[1]
            )
            self.assertTrue(self._compare(expected, response))

    def test_write_wrong_value(self):
        date = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        for sensor, values in iter(self.sensors.items()):
            args = (sensor, 'wrong', date)
            cmd = f'w {args[0]} {args[1]} {args[2]}'
            for byte in cmd:
                self.assertTrue(self.system.parse(byte))
            response = self._parseString(self.system.parse('\n'))
            expected = self._expected(
                sensor=sensor,
                val=0.0,
                date=date,
                info=values[1]
            )
            self.assertTrue(self._compare(expected, response))

    def test_write_wrong_date(self):
        for sensor, values in iter(self.sensors.items()):
            args = (sensor, 10.0, 'wrong_date')
            cmd = f'w {args[0]} {args[1]} {args[2]}'
            for byte in cmd:
                self.assertTrue(self.system.parse(byte))
            response = self._parseString(self.system.parse('\n'))
            expected = self._expected(
                sensor=sensor,
                val=10.0,
                date='wrong_date',
                info=values[1]
            )
            self.assertTrue(self._compare(expected, response))

    def test_write_unknown_sensor(self):
        date = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        args = ('unkn', 10.0, date)
        cmd = f'w {args[0]} {args[1]} {args[2]}'
        for byte in cmd:
            self.assertTrue(self.system.parse(byte))
        response = self.system.parse('\n')
        self.assertEqual(response, self.err_string)

    def test_write_wrong_number_of_args(self):
        for sensor, _ in iter(self.sensors.items()):
            args = (sensor, 10.0)
            cmd = f'w {args[0]} {args[1]}'
            for byte in cmd:
                self.assertTrue(self.system.parse(byte))
            self.assertFalse(self.system.parse('\n'))

    def test_write_as_read(self):
        cmd = f'w {list(self.sensors.keys())[0]}'
        for byte in cmd:
            self.assertTrue(self.system.parse(byte))
        self.assertFalse(self.system.parse('\n'))


if __name__ == '__main__':
    unittest.main()
