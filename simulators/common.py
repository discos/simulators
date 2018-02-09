import os
import abc
import signal


class BaseSystem(object):

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def system_stop():
        os.kill(os.getpid(), signal.SIGHUP)  # Send myself SIGHUP


class ListeningSystem(BaseSystem):

    @abc.abstractmethod
    def parse(self, byte):
        """This method takes a byte (single character string) and returns:
        False when the given byte is not the header, but the header is
        expected, True when the given byte is the header or a following
        expected byte, the response (the string to be sent back to the client)
        when the message is completed.
        The method eventually raises a ValueError in one of the following
        cases: the declared length of the message exceeds the maximum expected
        length, the sent message carries a wrong checksum, the client asks to
        execute an unknown command."""


class SendingSystem(BaseSystem):

    @abc.abstractmethod
    def get_message(self):
        """This method returns the message the system wants to send to
        its client(s). The message is sent periodically and the system
        must have an attribute called 'sampling_rate'. Make sure that
        the method is implemented thread safely."""
