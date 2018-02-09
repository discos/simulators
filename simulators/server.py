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

    custom_header, custom_tail = ('$', '!')

    def _execute_custom_command(self, msg_body):
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


class ListenHandler(BaseHandler):

    def handle(self):
        """See https://github.com/discos/simulators/issues/1"""
        logging.info('Got connection from %s', self.client_address)
        # We accept some commands not related to the protocol.  I.e. a
        # $stop! command will stop the server, a $error! command will
        # configure the system in order to respond with errors, etc.
        # We call these commands *custom commands*, and we use for them
        # the following header and tail:
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
        self.request.setblocking(False)
        sampling_time = self.system.sampling_time
        while True:
            try:
                custom_msg = self.request.recv(1024)
                if not custom_msg:
                    break
                if custom_msg.startswith('$') and custom_msg.endswith('!'):
                    self._execute_custom_command(custom_msg[1:-1])
            except IOError:
                # No data received, just pass
                pass
            try:
                self.request.sendall(self.system.get_message())
            except IOError:
                break
            time.sleep(sampling_time)


class Server(ThreadingMixIn, ThreadingTCPServer):

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

    def run(self):
        print('Server %s up and running.' % (self.server_address,))
        if self.child_server:
            print(
                'Server %s up and running.'
                % (self.child_server.server_address,)
            )
            self.child_server.start()
        self.serve_forever()

    def start(self):
        t1 = threading.Thread(target=self.serve_forever)
        t1.daemon = True
        t1.start()
        if self.child_server:
            self.child_server.start()

    def stop(self):
        self.shutdown()


class Simulator(object):
    """This class represents the whole simulator, composed of one
    or more servers."""

    def __init__(self, system_module):
        """
        :param system_module: the module that implements the system.
        """
        if not isinstance(system_module, types.ModuleType):
            self.system_module = importlib.import_module(
                'simulators.%s'
                % system_module
            )
        else:
            self.system_module = system_module

    def start(self, daemon=False):
        processes = []
        for l_address, s_address, args in self.system_module.servers:
            system = self.system_module.System(*args)
            s = Server(system, l_address, s_address)
            p = Process(target=s.run)
            p.daemon = daemon
            processes.append(p)
            p.start()

    def stop(self):
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
