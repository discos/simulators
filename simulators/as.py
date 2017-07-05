from common import BaseSystem


class System(BaseSystem):
    """
    Each command_x() method have to return a tuple:

    ('command_name', (par1, par2, ..., parN))

    The custom commands start with _.
    """

    msg_header = b'#'
    msg_tail = b'\n'

    def parse(self, msg):
        """Return the command name and parameters.

        @msg contains the header and tail

        In case of wrong msg, return the error message."""

    def command_a(self, *args):
        pass

    def command_b(self, *args):
        pass

