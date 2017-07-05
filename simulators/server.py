import os
import logging
import importlib
import threading

from SocketServer import (
    ThreadingMixIn, ThreadingTCPServer, BaseRequestHandler
)


logging.basicConfig(
    filename=os.path.join(os.getenv('ACSDATA', ''), 'sim-server.log'),
    format='%(asctime)s %(message)s',
    level=logging.DEBUG)


class Handler(BaseRequestHandler):

    def handle(self):
        logging.info('Got connection from %s', self.client_address)
        msg_header = self.system.msg_header
        msg_tail = self.system.msg_tail
        msg = b''
        while True:
            byte = self.request.recv(1)
            if not byte:
                break
            elif byte == msg_header:
                msg = msg_header
            elif msg.startswith(msg_header):
                msg += byte
                if byte == msg_tail:
                    command_name, parameters = self.system.parse(msg)
                    try:
                        command_method = getattr(self.system, command_name)
                    except AttributeError:
                        error = 'command %s not supported' % command_name
                        response = msg_header + error + msg_tail
                    else:
                        response = command_method(*parameters)
                    self.request.sendall(response)
            else:
                logging.debug('expecting the header, got a %s', byte)


class Server(ThreadingMixIn, ThreadingTCPServer):

    def __init__(self, server_address, system_name, *args):
        """system_name should be: 'as', 'roach', 'xarcos', etc."""
        module = importlib.import_module('simulators.%s' % system_name)
        Handler.system = module.System(*args)
        ThreadingTCPServer.__init__(self, server_address, Handler)

    @property
    def msg_header(self):
        return Handler.system.msg_header

    @property
    def msg_tail(self):
        return Handler.system.msg_tail

    def start(self):
        """Start a thread with the server.

        That thread will then start one more thread for each request."""
        server_thread = threading.Thread(target=self.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()

    def stop(self):
        self.shutdown()


if __name__ == '__main__':
    server = Server(('', 10000), 'as')
    server.serve_forever()
