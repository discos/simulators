import time
from socketserver import ThreadingTCPServer
from simulators.common import ListeningSystem


servers = [(('0.0.0.0', 12500), (), ThreadingTCPServer, {})]


class System(ListeningSystem):
   pass