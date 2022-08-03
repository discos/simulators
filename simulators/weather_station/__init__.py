import datetime
from socketserver import ThreadingUDPServer
from threading import current_thread
from simulators.common import ListeningSystem


servers = [(('0.0.0.0', 12600), (), ThreadingUDPServer, {})]


class System(ListeningSystem):

    def __init__(self):
        self.starting_date = \
            datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')

        self.commands = {
            'r': '_read',
            'w': '_write'
        }

        self.tail = '\n'

        self.sensors = {
            'th01': [26.0, self.starting_date, 'heating temp [oC]'],
            'vh01': [0.0, self.starting_date, 'heating voltage [V]'],
            'vs01': [7.7, self.starting_date, 'supply voltage [V]'],
            'vr01': [3.52, self.starting_date, 'rif. voltage [V]'],
            'dn01': [287.0, self.starting_date, 'wind dir min [deg]'],
            'dm01': [289.0, self.starting_date, 'wind dir ave [deg]'],
            'dx01': [292.0, self.starting_date, 'wind dir max [deg]'],
            'sn01': [1.6, self.starting_date, 'wind speed min [m/s]'],
            'sm01': [1.8, self.starting_date, 'wind speed ave [m/s]'],
            'sx01': [1.9, self.starting_date, 'wind speed max [m/s]'],
            'ta01': [23.0, self.starting_date, 'air temp [oC]'],
            'ua01': [72.5, self.starting_date, 'rel. humidity [%]'],
            'pa01': [940.9, self.starting_date, 'air pressure [hPa]'],
            'rc01': [9.86, self.starting_date, 'rain amount [mm]'],
            'rd01': [4240.0, self.starting_date, 'rain duration [s]'],
            'ri01': [0.0, self.starting_date, 'rain intensity [mm/h]'],
            'rp01': [-9999.9, '#', 'rain peak duration [s]'],
            'hc01': [0.0, self.starting_date, 'hail amount [hits/cm2]'],
            'hd01': [20.0, self.starting_date, 'hail duration [s]'],
            'hi01': [0.0, self.starting_date, 'hail intensity [hits/cm2h]'],
            'hp01': [-9999.9, '#', 'hail peak duration [s]']
        }

        self.err_string = (
            '<Sensor>'
            + '<Id>sintax error or sensor not found</Id>'
            + '<Val>1.000000</Val>'
            + '<Date>error</Date>'
            + '<Info>error</Info>'
            + '</Sensor>'
        )

        self.msg = {}

    def _reset(self, t):
        del self.msg[t]

    def parse(self, byte):
        t = current_thread().ident
        if not self.msg.get(t):
            self.msg[t] = ''

        self.msg[t] += byte

        if len(self.msg[t]) == 1:
            if byte in self.commands:
                return True
            else:
                self._reset(t)
                return False
        elif len(self.msg[t]) == 2:
            if byte == ' ':
                return True
            else:
                self._reset(t)
                return False
        elif byte == self.tail:
            self.msg[t] = self.msg[t].strip()
            args = self.msg[t].split()

            if len(args) > 1:
                command = getattr(self, self.commands.get(args[0]))
                sensor = args[1]
            if len(args) == 2:
                self._reset(t)
                if command != self._read:  # pylint: disable=W0143
                    return False
                return self._read(sensor)
            elif len(args) == 4:
                if command != self._write:  # pylint: disable=W0143
                    self._reset(t)
                    return False
                try:
                    value = float(args[2])
                except ValueError:
                    value = 0.0
                date = args[3]
                self._reset(t)
                return self._write(sensor, value, date)
            else:
                self._reset(t)
                return False
        return True

    def _read(self, sensor):
        try:
            value, date, info = self.sensors[sensor]
            retval = (
                '<Sensor>'
                + f'<Id>{sensor}</Id>'
                + f'<Val>{float(value):0.6f}</Val>'
                + f'<Date>{date}</Date>'
                + f'<Info>{info}</Info>'
                + '</Sensor>'
            )
        except KeyError:
            retval = self.err_string
        return retval

    def _write(self, sensor, value, date):
        try:
            self.sensors[sensor][0] = value
            self.sensors[sensor][1] = date
        except KeyError:
            pass
        return self._read(sensor)
