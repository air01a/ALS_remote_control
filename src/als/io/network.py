""" Provide networking features"""
import os
import socket
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer as BaseHTTPServer
from logging import getLogger
from typing import Tuple

from als import config
from als.code_utilities import log, AlsLogAdapter
from multiprocessing.connection import Listener
import threading

_LOGGER = AlsLogAdapter(getLogger(__name__), {})


@log
def get_ip():
    """
    Retrieves machine's IP address.

    :return: IP address
    :rtype: str
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        test_socket.connect(('10.255.255.255', 1))
        ip_address = test_socket.getsockname()[0]
    except OSError:
        ip_address = '127.0.0.1'
    finally:
        test_socket.close()
    return ip_address


class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""
    @log
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath


class HTTPServer(BaseHTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""
    @log
    def __init__(self, base_path, server_address, request_handler_class=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, request_handler_class)

    @log
    def process_request(self, request: bytes, client_address: Tuple[str, int]) -> None:
        super().process_request(request, client_address)


class WebServer(threading.Thread):
    """
    Thread class with a stop() method.

    The thread itself has to check regularly for the stopped() condition.
    """

    # FIXME logging this init causes issue with server thread init. To be investigated
    #  @log
    def __init__(self, web_dir):
        # web stuff
        self.web_dir = web_dir
        self.httpd = HTTPServer(self.web_dir, ("", config.get_www_server_port_number()))
        self.httpd.timeout = 1

        # thread stuff
        self._stop_event = threading.Event()

        # Init parent thread
        super().__init__(target=self.serve)

    @log
    def serve(self):
        """
        Continuously handles incomming HTTP requests.
        """
        while not self.stopped():
            self.httpd.handle_request()

    @log
    def stop(self):
        """
        Stops the web server.
        """
        self._stop_event.set()

    def stopped(self):
        """
        Checks if server is stopped.

        :return: True if server is stopped, False otherwise
        """
        return self._stop_event.is_set()




class SocketController:


    def _run_server(self):
        address = (self.address, self.port)     # family is deduced to be 'AF_INET'
        self.listener = Listener(address)
        while self._run:
            conn = self.listener.accept()
            print('connection accepted from', self.listener.last_accepted)
            try:
                while self._run:
                    msg = conn.recv()
                    # do something with msg
                    if msg == 'close':
                        conn.close()
                        break
                    t_tmp = msg.split('(')
                    if len(t_tmp)==2:
                        if t_tmp[0] in self.callbacks.keys():
                            function = t_tmp[0]
                            vars=t_tmp[1].split(')')[0].split(',')
                            ret = self.callbacks[function](vars)
                            conn.send("0:RET CODE={}".format(ret))
                        else:
                            conn.send("1:UNKNOWN COMMAND")
                    else:
                        conn.send("2:SYNTAX ERROR")
            except:
                print("Socket error")
        self.listener.close()


    def __init__(self, address, port, callbacks):
        self._run = True
        self.address = address
        self.port = port
        self.callbacks=callbacks
        self.thread = threading.Thread(target=self._run_server, args=(),daemon=True)
        self.thread.start()