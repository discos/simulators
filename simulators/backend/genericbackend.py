import time
import random
import re
from threading import Timer


class BackendException(Exception):
    pass


class GenericBackend(object):

    def __init__(self, max_sections=5, max_bandwidth=2000):
        self.status_string = "ok"
        self.acquiring = False
        self.configuration_string = "unconfigured"
        self.integration = 0
        self._waiting_for_start_time = False
        self._startID = None
        self._waiting_for_stop_time = False
        self._stopID = None
        self._valid_conf_re = re.compile("^[a-z]")
        self._sections = {}
        self.max_sections = max_sections
        self.max_bandwidth = max_bandwidth
        self._filename = ""
        self.interleave = 0

    def system_stop(self):
        if self._startID:
            self._startID.cancel()
            self._startID.join()
        if self._stopID:
            self._stopID.cancel()
            self._stopID.join()

    def status(self):
        return (
            self._get_time(),
            self.status_string,
            1 if self.acquiring else 0
        )

    @staticmethod
    def get_tpi():
        return [random.random() * 100, random.random() * 100]

    @staticmethod
    def get_tp0():
        return [0, 0]

    def get_configuration(self):
        return [self.configuration_string]

    def set_configuration(self, conf_name):
        if not self._is_valid_configuration(conf_name):
            raise BackendException("invalid configuration")
        # Here you should perform actual hardware configuration
        self.configuration_string = conf_name

    def get_integration(self):
        return [self.integration]

    def set_integration(self, integration):
        self.integration = integration

    def time(self):
        return [self._get_time()]

    def start(self, timestamp=None):
        if not timestamp:
            self._start_now()
        else:
            self._start_at(timestamp)

    def stop(self, timestamp=None):
        if not timestamp:
            self._stop_now()
        else:
            self._stop_at(timestamp)

    def set_section(self, section, start_freq, bandwidth,
                    feed, mode, sample_rate, bins):
        if section > self.max_sections and not section == "*":
            raise BackendException(
                "backend supports %d sections" % (self.max_sections)
            )
        if bandwidth > self.max_bandwidth and not bandwidth == "*":
            raise BackendException(
                "backend maximum bandwidth is %f" % (self.max_bandwidth)
            )
        self._sections[section] = (
            start_freq,
            bandwidth,
            feed,
            mode,
            sample_rate,
            bins
        )

    def cal_on(self, interleave):
        self.interleave = interleave

    def set_filename(self, filename):
        self._filename = filename

    @staticmethod
    def convert_data():
        pass

    @staticmethod
    def _get_time():
        # Should ask the backend hardware clock
        return '%.7f' % time.time()

    def _is_valid_configuration(self, configuration_name):
        return self._valid_conf_re.match(configuration_name)

    def _start_at(self, timestamp):
        if timestamp < time.time():
            raise BackendException("starting time already elapsed")
        if self._waiting_for_start_time:
            self._startID.cancel()
        self._waiting_for_start_time = True
        start_in = timestamp - time.time()
        self._startID = Timer(start_in, self._start_now)
        self._startID.start()

    def _start_now(self):
        if self.acquiring:
            raise BackendException("already acquiring")
        self._waiting_for_start_time = False
        self.acquiring = True

    def _stop_now(self):
        if not self.acquiring:
            raise BackendException("not acquiring")
        self._waiting_for_start_time = False
        self._waiting_for_stop_time = False
        self.acquiring = False

    def _stop_at(self, timestamp):
        if timestamp < time.time():
            raise BackendException("stop time already elapsed")
        if self._waiting_for_stop_time:
            self._stopID.cancel()
        self._waiting_for_stop_time = True
        stop_in = timestamp - time.time()
        self._stopID = Timer(stop_in, self._stop_now)
        self._stopID.start()
