from simulators import utils

# Each system module (like active_surface.py, acu.py, etc.) has to
# define a list called servers.s This list contains tuples
# (l_address, s_address, args). l_address is the tuple (ip, port) that
# defines the listening node that exposes the parse method, s_address
# is the tuple that defines the optional sending node that exposes the
# get_message method, while args is a tuple of optional extra arguments.
servers = [(('127.0.0.1', 12000), (), ())]

systems = utils.get_systems()
default_system_type = 'IFD_14_channels'
system_type = default_system_type


class System(object):

    def __new__(cls, *args):
        if system_type not in systems:
            raise ValueError(
                'Configuration %s for system if_distributor not found.'
                % system_type
            )

        return systems[system_type].System(*args)
