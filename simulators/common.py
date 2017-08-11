import os
import signal


class BaseSystem(object):

    @staticmethod
    def system_stop():
        os.kill(os.getpid(), signal.SIGHUP)  # Send myself SIGHUP
