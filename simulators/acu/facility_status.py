from simulators import utils


class FacilityStatus:

    def __init__(self):
        self.status = bytearray(16)
        self.voltagePhToPh = 0
        self.currentPhToPh = 0

    @property
    def voltagePhToPh(self):
        return utils.bytes_to_real(self.status[0:8], precision=2)

    @voltagePhToPh.setter
    def voltagePhToPh(self, value):
        # REAL64
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[0:8] = utils.real_to_bytes(value, precision=2)

    @property
    def currentPhToPh(self):
        return utils.bytes_to_real(self.status[8:16], precision=2)

    @currentPhToPh.setter
    def currentPhToPh(self, value):
        # REAL64
        if not isinstance(value, (float, int)):
            raise ValueError('Provide a floating point number!')
        self.status[8:16] = utils.real_to_bytes(value, precision=2)
