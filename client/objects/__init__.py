"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
import os
import select
import socket
import threading

from client.objects.packet_handlers import PrintPacketHandler


class Eavesdropper(object):
    """Listens on the specified port and captures the UDP traffic"""
    _BUFFER_SIZE = 2**16
    _BIND_ADDRESS = '0.0.0.0'

    def __init__(self, listen_port, handler=None):
        self._listen_port = listen_port  # type: int
        self._handler = handler or PrintPacketHandler()  # type: PacketHandler
        self._socket = None  # type: socket.socket
        self._thread_run = True  # type: bool
        self._thread = None  # type: threading.Thread

    def __del__(self):
        self._cleanup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def start_listening(self):
        """Starts the child thread socket listener.

        Starts a child thread to listen on the specified port. If a thread has
        already been started then this is a no-op.
        """
        if not self._thread:
            self._thread_run = True
            self._thread = threading.Thread(target=self._listen)
            self._thread.start()

    def stop_listening(self):
        """Asks the child thread to stop listening.

        This asks the child thread to stop listening. It is considered unsafe
        to force a thread to abort since it may leave resources in a bad state.
        """
        if self._thread:
            self._thread_run = False

    def _listen(self):
        if os.environ.get('AOUTILS_MC_TESTING', False):
            return

        self._socket = socket.socket(socket.AF_INET,
                                     socket.SOCK_RAW,
                                     socket.IPPROTO_UDP)
        self._socket.bind((self._BIND_ADDRESS, self._listen_port))

        while self._thread_run:
            self._socket.setblocking(0)
            ready = select.select([self._socket], [], [], 1)
            if ready[0]:
                self._handler.handle_packet(
                    *self._socket.recvfrom(self._BUFFER_SIZE),
                    port=self._listen_port)

    def _cleanup(self):
        if self._socket:
            self._socket.close()
            self._socket = None
