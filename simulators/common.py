import os
import signal


class BaseSystem(object):

    def _exit(self):
        os.kill(os.getpid(), signal.SIGHUP)  # Send myself SIGHUP
