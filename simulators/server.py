from __future__ import print_function
import os
import types
import socket
import logging
import importlib
import threading
import time
from multiprocessing import Process
from SocketServer import (
    ThreadingMixIn, ThreadingTCPServer, BaseRequestHandler
)


logging.basicConfig(
    filename=os.path.join(os.getenv('ACSDATA', ''), 'sim-server.log'),
    format='%(asctime)s %(message)s',
    level=logging.DEBUG)


class BaseHandler(BaseRequestHandler):
    """This is the base handler class from which `ListenHandler` and
    `SendHandler` classes are inherited. It only defines the custom
    header and tail for accepting some commands not related to the system
    protocol, and the `_execute_custom_command` method to parse the received
    custom command.
    I.e. a $system_stop! command will stop the server, a $error! command
    will configure the system in order to respond with errors, etc.
    """

    custom_header, custom_tail = ('$', '!')

    def _execute_custom_command(self, msg_body):
        if ':' in msg_body:
            name, params_str = msg_body.split(':')
        else:
            name, params_str = msg_body, ''
        # $command:par1,par2,...,parN!
        if params_str:
            params = params_str.split(',')
        else:
            params = ()
        try:
            method = getattr(self.system, name)
            response = method(*params)
            if isinstance(response, str):
                self.request.sendall(response)
        except AttributeError:
            logging.debug('command %s not supported', name)
        except Exception, ex:
            logging.debug('unexpected exception %s', ex)


class ListenHandler(BaseHandler):

    def handle(self):
        """See https://github.com/discos/simulators/issues/1"""
        logging.info('Got connection from %s', self.client_address)
        custom_msg = b''
        while True:
            byte = self.request.recv(1)
            if not byte:
                break
            try:
                response = self.system.parse(byte)
            except ValueError, ex:
                logging.debug(ex)
                continue
            except Exception:
                logging.debug('unexpected exception')
                continue
            if response is True:
                # All custom command bytes should be different than the
                # system header, otherwise the custom command will be cleared
                custom_msg = b''
                continue  # The system is still composing the message
            elif response and isinstance(response, str):
                try:
                    self.request.sendall(response)
                except IOError:
                    # Something went wrong while sending the response, probably
                    # the client was stopped without closing the connection
                    break
            elif response is False:
                # The system is still waiting for the header:
                # check if the client is sending a custom command
                if byte == self.custom_header:
                    custom_msg = byte
                elif custom_msg.startswith(self.custom_header):
                    custom_msg += byte
                    if byte == self.custom_tail:
                        msg_body = custom_msg[1:-1]
                        custom_msg = b''
                        self._execute_custom_command(msg_body)
            else:
                logging.debug('unexpected response: %s', response)


class SendHandler(BaseHandler):

    def handle(self):
        """See https://github.com/discos/simulators/issues/51"""
        logging.info('Got connection from %s', self.client_address)
        self.request.setblocking(False)
        sampling_time = self.system.sampling_time
        while True:
            t0 = time.time()
            try:
                custom_msg = self.request.recv(1024)
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
                self.request.sendall(self.system.get_message())
            except IOError:
                # Something went wrong while sending the message, probably
                # the client was stopped without closing the connection
                break
            elapsed_time = time.time() - t0
            time.sleep(sampling_time - elapsed_time)


class Server(ThreadingMixIn, ThreadingTCPServer):
    """This class inherits from the ThreadingTCPServer class.
    It instances a TCP server for the given address(es), and pass it the
    given system instance. A server could be a listening server,
    if param l_address is provided, or a sending server,
    if param s_address is provided. If both addresses are provided,
    the server acts as both as a listening server and a sending server.
    Be aware that if the server both listens and send to its clients,
    `l_address` and `s_address` must have at least different ports,
    if not different ips.

    :param system: the system instance needed by the server.
    :param l_address: a tuple (ip, port), the address of the server that
        exposes the `System.parse()` method.
    :param s_address: a tuple (ip, port), the address of the server that
        exposes the `System.get_message()` method.
    """
    def __init__(self, system, l_address=None, s_address=None):
        self.child_server = None
        if l_address:
            self.address = l_address
            ListenHandler.system = system
            ThreadingTCPServer.__init__(self, l_address, ListenHandler)
            if s_address:
                self.child_server = Server(system, None, s_address)
        elif s_address:
            self.address = s_address
            SendHandler.system = system
            ThreadingTCPServer.__init__(self, s_address, SendHandler)
        else:
            raise ValueError('You must specify at least one server.')

    def serve_forever(self, poll_interval=0.5):
        """This method overrides the ThreadingTCPServer `serve_forever`
        method. Before calling the base method, which would stay in a loop
        until the process is stopped, it starts the eventual child server
        as a daemon thread.
        """
        if self.child_server:
            self.child_server.start()
        ThreadingTCPServer.serve_forever(self, poll_interval)

    def start(self):
        """This method starts a daemon thread which calls the `serve_forever`
        method. The server is therefore started as a daemon."""
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def stop(self):
        """This method stops the server and its eventual child."""
        if self.child_server:
            self.child_server.shutdown()
        self.shutdown()


class Simulator(object):
    """This class represents the whole simulator, composed of one
    or more servers.

    :param system_module: the module that implements the system. It could
        also be a module name. In that case the module will be loaded
        dynamically.
    """
    def __init__(self, system_module):
        if not isinstance(system_module, types.ModuleType):
            self.system_module = importlib.import_module(
                'simulators.%s'
                % system_module
            )
        else:
            self.system_module = system_module

    def start(self, daemon=False):
        """This method starts a simulator by instancing
        the servers listed in the given module.

        :param daemon: if true, the server processes are created as daemons,
            meaning that when this simulator object is destroyed, they get
            destroyed as well. Default value is false, meaning that the server
            processes will continue to run even if the simulator object gets
            destroyed. To stop these processes, method `stop` must be called.
        """
        for l_address, s_address, args in self.system_module.servers:
            system = self.system_module.System(*args)
            s = Server(system, l_address, s_address)
            p = Process(target=s.serve_forever)
            p.daemon = daemon
            p.start()
            if not daemon:
                if l_address:
                    print('Server %s up and running.' % (l_address,))
                if s_address:
                    print('Server %s up and running.' % (s_address,))

    def stop(self):
        """This method stops a simulator by sending the custom `$system_stop!`
        command to all servers of the given simulator."""
        for entry in self.system_module.servers:
            for address in entry[:-1]:
                if not address:
                    continue
                try:
                    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sockobj.settimeout(1)
                    sockobj.connect(address)
                    sockobj.sendall('$system_stop!')
                except Exception, ex:
                    logging.debug(ex)
                finally:
                    sockobj.close()
