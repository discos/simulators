from SocketServer import ThreadingTCPServer
from simulators import utils
from simulators.common import MultiTypeSystem

# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers.s This list contains tuples
# (l_address, s_address, args). l_address is the tuple (ip, port) that
# defines the listening node that exposes the parse method, s_address
# is the tuple that defines the optional sending node that exposes the
# get_message method, while args is a tuple of optional extra arguments.
servers = [(('0.0.0.0', 12000), (), ThreadingTCPServer, ())]

systems = utils.get_systems()
default_system_type = 'IFD'
system_type = default_system_type


class System(MultiTypeSystem):

    def __new__(cls, *args):
        cls.systems = systems
        cls.system_type = system_type
        return MultiTypeSystem.__new__(cls, *args)
