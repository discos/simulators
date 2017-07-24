import os
import signal


class BaseSystem(object):

    @staticmethod
    def _exit():
        os.kill(os.getpid(), signal.SIGHUP)  # Send myself SIGHUP
