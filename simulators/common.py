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


class ConfigurableSystem(object):

    def __new__(cls, *args):
        """This class acts as a 'class factory', it means that given the
        attributes `cls.system_type` and `cls.systems` (that must be
        present in inherited classes), creating an instance of
        `ConfigurableSystem` (or some other class that inherits from this one)
        will actually create an object of `cls.system_type` type if it's
        found in the `cls.systems` list. This class is useful when we have
        more than one configuration for the same system."""

        if cls.system_type not in cls.systems:
            raise ValueError('Configuration %s not found.' % cls.system_type)

        return cls.systems[cls.system_type].System(*args)
