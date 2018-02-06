from simulators.acu_status.generic_axis import AxisStatus
from simulators.acu_status.cable_wrap_axis import CableWrapAxisStatus


class AzimuthAxisStatus(AxisStatus):

    def __init__(self):
        AxisStatus.__init__(self, 8, 0.85, 0.4, (-90, 450), [180])

        self.AzimuthCableWrap = CableWrapAxisStatus()

    def get_cable_wrap_axis_status(self):
        return self.AzimuthCableWrap.get_axis_status()

    def get_cable_wrap_motor_status(self):
        return self.AzimuthCableWrap.get_motor_status()

    def stop(self):
        self.run = False
        self.AzimuthCableWrap.stop()
