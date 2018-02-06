from simulators.acu_status.generic_axis import AxisStatus


class ElevationAxisStatus(AxisStatus):

    def __init__(self):
        AxisStatus.__init__(self, 4, 0.5, 0.25, (5, 90), [90])
