import abc


class BaseSystem(object):

    __metaclass__ = abc.ABCMeta

    @staticmethod
    def system_stop():
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
        execute an unknown command.
        Additional information here:
        https://github.com/discos/simulators/issues/1

        :param byte: the received message byte."""


class SendingSystem(BaseSystem):

    @abc.abstractmethod
    def subscribe(self, q):
        """This method passes a queue object to the System instance in order
        for it to add it to its clients list. The System will therefore put any
        new status message into this queue, along with the queue of other
        clients, as soon as the status message is updated.
        Additional information here:
        https://github.com/discos/simulators/issues/175

        :param q: the queue object in which the System will put the last status
            message to be sent to the client."""

    @abc.abstractmethod
    def unsubscribe(self, q):
        """This method passes a queue object to the System instance in order
        for it to be removed from the clients list. The System will therefore
        release the handle to the queue object in order for the garbage
        collector to destroy it when the client has finally disconnected.
        Additional information here:
        https://github.com/discos/simulators/issues/175

        :param q: the queue object that contains the last status message to
            send to the connected client."""


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
