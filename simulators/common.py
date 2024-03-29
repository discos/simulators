import abc


class BaseSystem:
    """`System` class from which every other `System` class is inherited.
    If a custom command that can be useful for every kind of simulator has to
    be implemented, this class is the right place."""

    __metaclass__ = abc.ABCMeta

    def system_stop(self):
        """Sends back to the server the message `$server_shutdown%%%%%`
        ordering it to stop accepting requests, to close its socket and to shut
        down.

        :return: a message telling the server to proceed with its shutdown."""
        return '$server_shutdown%%%%%'

    @staticmethod
    def system_greet():
        """Override this method to define a greeting message to send to the
        clients as soon as they connect.

        :return: the greeting message to sent to connected clients."""
        return None


class ListeningSystem(BaseSystem):
    """Implements a server that waits for its client(s) to send a command, it
    can then answer back when required."""

    @abc.abstractmethod
    def parse(self, byte):
        """Receives and parses the command to be sent to the System. Additional
        information here:
        https://github.com/discos/simulators/issues/1

        :param byte: the received message byte.
        :type byte: byte
        :return: False when the given byte is not the header, but the header is
            expected. True when the given byte is the header or a following
            expected byte. The response (the string to be sent back to the
            client) when the message is completed.
        :rtype: boolean, string
        :raise ValueError: when the declared length of the message exceeds the
            maximum expected length, when the sent message carries a wrong
            checksum or when the client asks to execute an unknown command."""


class SendingSystem(BaseSystem):
    """Implements a server that periodically sends some information data
    regarding the status of the system to every connected client. The time
    period is the one defined as `sampling_time` variable, which defaults
    to 10ms and can be overridden. The class also accepts simulator-related
    custom commands, but no regular commands are accepted (they are ignored
    and immediately discarded)."""

    sampling_time = 0.01  # 10ms

    @abc.abstractmethod
    def subscribe(self, q):
        """Passes a queue object to the System instance in order for it to add
        it to its clients list. The System will therefore put any new status
        message into this queue, along with the queue of other clients, as soon
        as the status message is updated. Additional information here:
        https://github.com/discos/simulators/issues/175

        :param q: the queue object in which the System will put the last status
            message to be sent to the client.
        :type q: Queue"""

    @abc.abstractmethod
    def unsubscribe(self, q):
        """Passes a queue object to the System instance in order for it to be
        removed from the clients list. The System will therefore release the
        handle to the queue object in order for the garbage collector to
        destroy it when the client has finally disconnected. Additional
        information here:
        https://github.com/discos/simulators/issues/175

        :param q: the queue object that contains the last status message to
            send to the connected client.
        :type q: Queue"""


class MultiTypeSystem:
    """This class acts as a 'class factory', it means that given the
    attributes `system_type` and `systems` (that must be defined in child
    classes), creating an instance of `MultiTypeSystem` (or some other
    class that inherits from this one) will actually create an object of
    `system_type` type if it's defined in the `systems` list. This class is
    meant to be used in systems that have multiple simulator types or
    configuration in order for the user to be able to choose the desired
    type when launching the simulator."""

    def __new__(cls, **kwargs):
        """Checks if the desired configuration is available and returns its
        correspondent class type.

        :return: the System class correspoding to the one selected via command
            line interface, or the default one."""
        if cls.system_type not in cls.systems:
            raise ValueError(f'System type {cls.system_type} not found.')

        return cls.systems[cls.system_type].System(**kwargs)
