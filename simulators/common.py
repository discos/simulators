import os
import signal


class BaseSystem(object):

    @staticmethod
    def __stop():
        os.kill(os.getpid(), signal.SIGHUP)  # Send myself SIGHUP
