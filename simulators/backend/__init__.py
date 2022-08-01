from SocketServer import ThreadingTCPServer
from simulators.utils import get_multitype_systems
from simulators.common import MultiTypeSystem


systems = get_multitype_systems(__file__)
servers = [
    (('0.0.0.0', 12801), (), ThreadingTCPServer, {'system_type': 'sardara'}),
    (('0.0.0.0', 12802), (), ThreadingTCPServer, {'system_type': 'mistral'}),
]


class System(MultiTypeSystem):

    def __new__(cls, **kwargs):
        cls.systems = systems
        cls.system_type = kwargs.pop('system_type')
        return MultiTypeSystem.__new__(cls, **kwargs)
