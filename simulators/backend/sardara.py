import re
from simulators.backend.genericbackend import GenericBackend


class Sardara(GenericBackend):

    def __init__(self):
        GenericBackend.__init__(self)
        self._valid_conf_re = re.compile("^[A-Z0-9]")
