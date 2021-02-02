from __future__ import print_function
import abc
import os
import types
import socket
import logging
import importlib
import threading
from Queue import Queue, Empty
from multiprocessing import Process
from SocketServer import (
    ThreadingMixIn, ThreadingTCPServer, ThreadingUDPServer, BaseRequestHandler
)


logging.basicConfig(
    filename=os.path.join(os.getenv('ACSDATA', ''), 'sim-server.log'),
    format='%(asctime)s %(message)s',
    level=logging.DEBUG)


class BaseHandler(BaseRequestHandler):
    """This is the base handler class from which `ListenHandler` and
    `SendHandler` classes are inherited. It only defines the custom header
    and tail for accepting some commands not related to the system protocol,
    and the `_execute_custom_command` method to parse the received custom
    command.

    :Example:
        A $system_stop% command will stop the server, a $error% command
        will configure the system in order to respond with errors, etc."""

    custom_header, custom_tail = ('$', '%')

    def setup(self):
        """Method that gets called whenever a client connects to the server."""
        logging.info('Got connection from %s', self.client_address)
        self.custom_msg = b''

    def _execute_custom_command(self, msg_body):
        """This method accepts a custom command (without the custom header and
        tail) formatted as `command_name:par1,par2,...,parN`. It then parses
        the command and its parameters and tries to call the system's
        equivalent method, also handling unexpected exceptions.

        :param msg_body: the custom command message without the custom header
            and tail (`$` and `%` respectively)
        :type msg_body: string"""
        if ':' in msg_body:
            name, params_str = msg_body.split(':')
        else:
            name, params_str = msg_body, ''
        if params_str:
            params = params_str.split(',')
        else:
            params = ()
        try:
            method = getattr(self.system, name)
            response = method(*params)
            if isinstance(response, str):
                self.socket.sendto(response, self.client_address)
                if response == '$server_shutdown%':
                    self.server.stop()
        except AttributeError:
            logging.debug('command %s not supported', name)
        except Exception, ex:
            logging.debug('unexpected exception %s', ex)


class ListenHandler(BaseHandler):

    def setup(self):
        BaseHandler.setup(self)
        self.socket = self.request
        self.connection_oriented = True
        if not isinstance(self.socket, tuple):  # TCP client
            greet_msg = self.system.system_greet()
            if greet_msg:
                self.socket.sendto(greet_msg, self.client_address)
        else:  # UDP client
            self.connection_oriented = False

    def handle(self):
        """Method that gets called right after the `setup` method ends its
        execution. It handles incoming messages, whether they are received via
        a TCP or a UDP socket. It passes down the `System` class the received
        messages one byte at a time in order for the `System.parse()` method to
        work properly. It then returns the `System` response when  received
        from the `System` class. It also constantly listens for custom commands
        that do not belong to a specific `System` class, but are useful
        additions to the framework with the purpose of reproducing a specific
        scenario (i.e. some error condition)."""
        if not self.connection_oriented:  # UDP client
            msg, self.socket = self.socket
            msg += '\n'
            self._handle(msg)
        else:  # TCP client
            while True:
                try:
                    msg = self.socket.recv(1)
                    if not msg:
                        break
                    self._handle(msg)
                except IOError:
                    break

    def _handle(self, msg):
        """Handles a single message.

        :param msg: the received message. Usually, in case of a TCP socket,
            this is a single byte to be passed down to the `System.parse()`
            method. In case of a connection-less communication (UDP socket),
            this parameter contains a chunk of bytes, each one of them is then
            processed on its own.
        """
        response = None
        for byte in msg:
            try:
                response = self.system.parse(byte)
            except ValueError, ex:
                logging.debug(ex)
            except Exception:
                logging.debug('unexpected exception')
            if isinstance(response, bool):
                pass
            elif response and isinstance(response, str):
                try:
                    self.socket.sendto(response, self.client_address)
                except IOError:  # pragma: no cover
                    # Something went wrong while sending the response,
                    # probably the client was stopped without closing
                    # the connection
                    break
            else:
                logging.debug('unexpected response: %s', response)

            if byte == self.custom_header:
                self.custom_msg = byte
            elif self.custom_msg.startswith(self.custom_header):
                self.custom_msg += byte
                if byte == self.custom_tail:
                    msg_body = self.custom_msg[1:-1]
                    self.custom_msg = b''
                    self._execute_custom_command(msg_body)


class SendHandler(BaseHandler):

    def handle(self):
        """Method that gets called right after the `setup` method ends its
        execution. It handles messages that the server has to periodically send
        to its connected client(s). It also constantly listens for custom
        commands that do not belong to a specific `System` class, but are
        useful additions to the framework with the purpose of reproducing a
        specific scenario (i.e. some error condition)."""
        sampling_time = self.system.sampling_time
        message_queue = Queue(1)

        self.socket = self.request
        msg = None
        if isinstance(self.socket, tuple):
            msg, self.socket = self.socket
        self.socket.setblocking(False)

        self.system.subscribe(message_queue)
        while True:
            try:
                if msg:
                    custom_msg = msg
                    msg = None
                else:
                    custom_msg = self.socket.recv(1024)
                # Check if the client is sending a custom command
                if not custom_msg:
                    break
                if (
                    custom_msg.startswith(self.custom_header)
                    and custom_msg.endswith(self.custom_tail)
                ):
                    self._execute_custom_command(custom_msg[1:-1])
            except IOError:
                # No data received, just pass
                pass
            try:
                response = message_queue.get(timeout=sampling_time)
                self.socket.sendto(response, self.client_address)
                if self.socket.type == socket.SOCK_DGRAM:
                    break
            except Empty:
                pass
            except IOError:
                # Something went wrong while sending the message, probably
                # the client was stopped without closing the connection
                break
        self.system.unsubscribe(message_queue)


class Server(ThreadingMixIn):
    """This class inherits from the ThreadingMixIn class.
    It can instance a server for the given address(es). The server can either
    be a TCP or a UDP server, depending on which `server_type` argument is
    provided. Also, the server could be a listening server, if param
    `l_address` is provided, or a sending server, if param `s_address` is
    provided. If both addresses are provided, the server acts as both as a
    listening server and a sending server. Be aware that if the server both
    listens and send to its clients, `l_address` and `s_address` must not share
    the same endpoint (IP address and/or port should be different).

    :param system: the desired simulator system module
    :param server_type: the type of threading server to be used
    :param kwargs: the arguments to pass to the system instance constructor
        method
    :param l_address: the address of the server that exposes the
        `System.parse()` method
    :param s_address: the address of the server that exposes the
        `System.subscribe()` and `System.unsubscribe()` methods
    :type system: System class that inherits from ListeningServer or/and
        SendingServer
    :type server_type: ThreadingTCPServer or ThreadingUDPServer
    :type kwargs: dict
    :type l_address: (ip, port)
    :type s_address: (ip, port)
    """
    def __init__(
            self, system, server_type, kwargs, l_address=None, s_address=None):
        if server_type not in [ThreadingTCPServer, ThreadingUDPServer]:
            raise ValueError(
                'Provide either the `ThreadingTCPServer` class '
                + 'or the `ThreadingUDPServer` class!'
            )
        self.__class__.__bases__ = (ThreadingMixIn, server_type, )
        self.server_type = server_type
        self.server_type.allow_reuse_address = True
        self.system = system
        self.system_kwargs = kwargs

        self.child_server = None
        if l_address:
            self.address = l_address
            self.server_type.__init__(self, l_address, ListenHandler)
            if s_address:
                self.child_server = Server(
                    system, self.server_type, kwargs, None, s_address
                )
        elif s_address:
            self.address = s_address
            self.server_type.__init__(self, s_address, SendHandler)
        else:
            raise ValueError('You must specify at least one server.')
        self.RequestHandlerClass.system = None
        self.RequestHandlerClass.server = self

    def serve_forever(self, poll_interval=0.05):
        """Overrides the base class `serve_forever` method. Before calling the
        base method, which would stay in a loop until the process is stopped,
        it starts the eventual child server as a daemon thread.

        :param poll_interval: the interval used by the class to check for
            incoming shutdown requests
        :type poll_interval: float
        """
        if isinstance(self.system, types.ModuleType):
            self.system = self.system.System(**self.system_kwargs)
        elif isinstance(self.system, abc.ABCMeta):
            self.system = self.system(**self.system_kwargs)
        if not self.RequestHandlerClass.system:
            self.RequestHandlerClass.system = self.system
        if self.child_server:
            self.child_server.system = self.system
            self.child_server.start()
        try:
            self.server_type.serve_forever(self, poll_interval)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        """Starts a daemon thread which calls the `serve_forever` method. The
        server is therefore started as a daemon."""
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def stop(self):
        """Stops the server and its eventual child."""
        if self.child_server:
            self.child_server.shutdown()
        self.shutdown()


class Simulator(object):
    """This class represents the whole simulator, composed of one
    or more servers.

    :param system_module: the module that implements the System class.
    :type system_module: module that implements the System class, string
    """
    def __init__(self, system_module, **kwargs):
        if not isinstance(system_module, types.ModuleType):
            self.system_module = importlib.import_module(
                'simulators.%s'
                % system_module
            )
        else:
            self.system_module = system_module
        self.kwargs = kwargs
        self.simulator_name = self.system_module.__name__.split('.')[-1]

    def start(self, daemon=False):
        """Starts a simulator by instancing the servers listed in the given
        module.

        :param daemon: if true, the server processes are created as daemons,
            meaning that when this simulator object is destroyed, they get
            destroyed as well. Default value is false, meaning that the server
            processes will continue to run even if the simulator object gets
            destroyed. To stop these processes, method `stop` must be called.
        :type daemon: bool
        """
        processes = []
        for l_addr, s_addr, server_type, kwargs in self.system_module.servers:
            kwargs.update(self.kwargs)
            s = Server(
                self.system_module, server_type, kwargs, l_addr, s_addr
            )
            p = Process(target=s.serve_forever)
            p.daemon = daemon
            processes.append(p)
            p.start()
        print("Simulator '%s' up and running." % self.simulator_name)

        if not daemon:
            try:
                for p in processes:
                    p.join()
            except KeyboardInterrupt:
                print('')  # Skip the line displaying the SIGINT character
                self.stop()

    def stop(self):
        """Stops a simulator by sending the custom `$system_stop%` command to
        all servers of the given simulator."""
        def _send_stop(entry):
            for address in entry[:2]:
                if not address:
                    continue
                if entry[2] == ThreadingTCPServer:
                    socket_type = socket.SOCK_STREAM
                else:
                    socket_type = socket.SOCK_DGRAM
                sockobj = socket.socket(socket.AF_INET, socket_type)
                try:
                    sockobj.settimeout(0.1)
                    sockobj.connect(address)
                    try:
                        while sockobj.recv(1024):
                            pass
                    except socket.timeout:
                        pass
                    sockobj.sendto('$system_stop%', address)
                    response = sockobj.recv(1024)
                    if response != '$server_shutdown%':  # pragma: no cover
                        logging.warning(
                            '%s %s %s',
                            'The server did not answer with the',
                            '$server_shutdown% string!',
                            'The simulator might still be running!'
                        )
                except Exception, ex:  # pragma: no cover
                    logging.debug(ex)
                finally:
                    sockobj.close()
                break
        threads = []
        for entry in self.system_module.servers:
            t = threading.Thread(target=_send_stop, args=(entry,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        print("Simulator '%s' stopped." % self.simulator_name)
