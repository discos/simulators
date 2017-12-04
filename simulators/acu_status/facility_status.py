from simulators import utils


class FacilityStatus(object):

    voltagePhToPh = 0  # REAL64
    currentPhToPh = 0  # REAL64

    def get_status(self):
        return (utils.real_to_bytes(self.voltagePhToPh, 2)
                + utils.real_to_bytes(self.currentPhToPh, 2))
