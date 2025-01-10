# Authors:
#   Giuseppe Carboni <giuseppe.carboni@inaf.it>
#   Lorenzo Monti <lorenzo.monti@inaf.it>

from socketserver import ThreadingTCPServer
from simulators.utils import get_multitype_systems
from simulators.common import MultiTypeSystem


systems = get_multitype_systems(__file__)
servers = [
    (
        ('0.0.0.0', 12700),  # LO_CBAND
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12701),  # LO_CLOW
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12702),  # LO_KBAND
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12703),  # LO_WBAND
        (),
        ThreadingTCPServer,
        {'system_type': 'w_LO'}
    ),
    (
        ('0.0.0.0', 12704),  # LO_KQW_WHIGH
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12705),  # LO_KQW_WLOW
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
    (
        ('0.0.0.0', 12706),  # LO_KQW_Q
        (),
        ThreadingTCPServer,
        {'system_type': 'generic_LO'}
    ),
]


class System(MultiTypeSystem):

    def __new__(cls, **kwargs):
        cls.systems = systems
        cls.system_type = kwargs.pop('system_type')
        return MultiTypeSystem.__new__(cls, **kwargs)
