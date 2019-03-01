import abc


class BaseSystem(object):

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def system_stop():
        """This method sends back to the server the message `$server_shutdown!`
        ordering it to stop accepting requests and to shut down."""
        return '$server_shutdown!'


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
        execute an unknown command. See
        https://github.com/discos/simulators/issues/1 for more information.

        :param byte: the byte recived by the server"""


class SendingSystem(BaseSystem):

    @abc.abstractmethod
    def get_message(self):
        """This method returns the message the system wants to send to
        its client(s). The message is sent periodically and the system
        must have an attribute called 'sampling_time'. Make sure that
        the method is implemented thread safely. See
        https://github.com/discos/simulators/issues/51 for more information."""


class MultiTypeSystem(object):

    def __new__(cls, *args):
        """This class acts as a 'class factory', it means that given the
        attributes `system_type` and `systems` (that must be set in inherited
        classes), creating an instance of `MultiTypeSystem` (or some other
        class that inherits from this one) will actually create an object of
        `system_type` type if it's found in the `systems` list. This class is
        meant to be used in systems that have multiple simulator types in order
        for the user to be able to choose the desired type at simulator
        startup.
        """

        if cls.system_type not in cls.systems:
            raise ValueError('System type %s not found.' % cls.system_type)

        return cls.systems[cls.system_type].System(*args)
