import re
from simulators.backend.genericbackend import GenericBackendSystem


class System(GenericBackendSystem):

    def __init__(self):
        GenericBackendSystem.__init__(self)
        self._valid_conf_re = re.compile("^[A-Z0-9]")
