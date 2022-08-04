from socketserver import ThreadingTCPServer
from simulators.utils import get_multitype_systems
from simulators.common import MultiTypeSystem


systems = get_multitype_systems(__file__)
servers = [
    (
        ('0.0.0.0', 12000),
        (),
        ThreadingTCPServer,
        {'system_type': 'IFD'}
    ),
    (
        ('0.0.0.0', 12001),
        (),
        ThreadingTCPServer,
        {'system_type': 'IFD_14_channels'},
    ),
]


class System(MultiTypeSystem):

    def __new__(cls, **kwargs):
        cls.systems = systems
        cls.system_type = kwargs.pop('system_type')
        return MultiTypeSystem.__new__(cls, **kwargs)
