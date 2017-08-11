from __future__ import print_function
import os
import types
import socket
import logging
import importlib
import threading

from multiprocessing import Process
from SocketServer import (
    ThreadingMixIn, ThreadingTCPServer, BaseRequestHandler
)


logging.basicConfig(
    filename=os.path.join(os.getenv('ACSDATA', ''), 'sim-server.log'),
    format='%(asctime)s %(message)s',
    level=logging.DEBUG)


class Handler(BaseRequestHandler):

    def handle(self):
        """See https://github.com/discos/simulators/issues/1"""
        logging.info('Got connection from %s', self.client_address)
        # We accept some commands not related to the protocol.  I.e. a
        # $stop! command will stop the server, a $error! command will
        # configure the system in order to respond with errors, etc.
        # We call these commands *custom commands*, and we use for them
        # the following header and tail:
        custom_header, custom_tail = ('$', '!')
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
                self.request.sendall(response)
            elif response is False:
                # The system is still waiting for the header:
                # check if the client is sending a custom command
                # $command:par1,par2,...,parN!
                if byte == custom_header:
                    custom_msg = custom_header
                elif custom_msg.startswith(custom_header):
                    custom_msg += byte
                    if byte == custom_tail:
                        msg_body = custom_msg[1:-1]
                        custom_msg = b''
                        if ':' in msg_body:
                            name, params_str = msg_body.split(':')
                        else:
                            name, params_str = msg_body, ''
                        if ',' in params_str:
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
            else:
                logging.debug('unexpected response: %s', response)


class Server(ThreadingMixIn, ThreadingTCPServer):

    def __init__(self, server_address, system, *args):
        """
        :param server_address: a tuple (ip, port) of the server
        :param system: the module that implements the system (acu,
                       active_surface, etc.).  It could also be a module
                       name ('acu', 'active_surface', ect.), and
                       in that case the module will be loaded dynamically.
        :param args: a tuple of extra arguments for the Server class
        """
        if not isinstance(system, types.ModuleType):
            system = importlib.import_module('simulators.%s' % system)
        Handler.system = system.System(*args)
        ThreadingTCPServer.__init__(self, server_address, Handler)

    def start(self):
        """Start a thread with the server.

        That thread will then start one more thread for each request."""
        server_thread = threading.Thread(target=self.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

    def stop(self):
        self.shutdown()


class Simulator(object):
    """This class represents the whole simulator, composed of one
    or more servers."""

    def __init__(self, system_module):
        """
        :param system_module: the module that implements the system.
        """
        self.system_module = system_module

    def start(self, daemon=False):
        processes = []
        for address, args in self.system_module.servers:
            s = Server(address, self.system_module, *args)
            p = Process(target=s.serve_forever)
            p.daemon = daemon
            processes.append(p)
            p.start()
            print('Server %s up and running.' % (address,))

    def stop(self):
        for address, _ in self.system_module.servers:
            try:
                sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sockobj.settimeout(1)
                sockobj.connect(address)
                sockobj.sendall('$system_stop!')
            except Exception, ex:
                logging.debug(ex)
            finally:
                sockobj.close()


if __name__ == '__main__':
    server = Server(('', 10000), 'as')
    server.serve_forever()
