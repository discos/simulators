# Authors:
#   Giuseppe Carboni <giuseppe.carboni@inaf.it>
#   Lorenzo Monti <lorenzo.monti@inaf.it>

from socketserver import ThreadingTCPServer
from simulators.utils import get_multitype_systems
from simulators.common import MultiTypeSystem


systems = get_multitype_systems(__file__)
servers = [
    (
        ('0.0.0.0', 12700),
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12701),
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12702),
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12703),
        (),
        ThreadingTCPServer,
        {'system_type': 'w_LO'}
    ),
]


class System(MultiTypeSystem):

    def __new__(cls, **kwargs):
        cls.systems = systems
        cls.system_type = kwargs.pop('system_type')
        return MultiTypeSystem.__new__(cls, **kwargs)
