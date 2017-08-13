"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
import logging
import os
import select
import socket
import threading

from time import sleep

from client.objects.packet_handlers import PacketHandler
from . import net_scanner


class Eavesdropper(object):
    """Listens on the specified port and captures the UDP traffic"""
    _BUFFER_SIZE = 2**16
    _BIND_ADDRESS = '0.0.0.0'

    def __init__(self, listen_port, mode, config=None):
        self._listen_port = listen_port  # type: int
        self._mode = mode
        self._socket = None  # type: socket.socket
        self._thread_run = True  # type: bool
        self._thread = None  # type: threading.Thread
        self._config = config or {}
        self._handler = None

    def __del__(self):
        self._cleanup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def start_listening(self):
        """Starts the child thread socket listener.

        Starts a child thread to listen on the specified port. If a thread has
        already been started then this is a no-op.
        """
        # Set up the packet handler
        if not self._handler:
            logging.debug('Initializing packet handler')
            self._handler = PacketHandler.get_packet_handler(self._config)

        if not self._thread:
            logging.debug('Starting listener thread.')
            self._thread = threading.Thread(target=self._listen)
            self._thread_run = True
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

        protocol = (socket.IPPROTO_TCP if self._mode.upper() == 'TCP'
                    else socket.IPPROTO_UDP)
        if self._mode == 'TCP':
            return
        self._socket = socket.socket(socket.AF_INET,
                                     socket.SOCK_RAW,
                                     protocol)
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


class Overlord(object):
    """Controls the entire packet capturing process"""
    DEFAULT_SLEEP_TIME = 5

    def __init__(self, config=None):
        self._eavesdroppers = {}
        self._config = config or {}

    def oversee(self):
        """Starts the overlord on whatever scrape methodology is configured

        This is a blocking operation.
        """
        try:
            while True:
                if self._config['app']['scrape_mode'] == 'packet_capture':
                    self._process_packet_scraping()

                sleep(self.sleep_time)
        except KeyboardInterrupt:
            logging.debug('Gracefully closing eavesdroppers.')
            keys = list(self._eavesdroppers.keys())
            for key in keys:
                self._eavesdroppers[key].stop_listening()
                del self._eavesdroppers[key]

    def _process_packet_scraping(self):
        """Starts the overlords port listening process.

        This is a blocking operation. Ports will be updated based on whatever
        values are configured in the supplied configuration."""
        logging.debug('beginning albion scan.')
        scanned_ports = net_scanner.find_albion_ports()
        known_ports = list(self._eavesdroppers.keys())

        for port, mode in scanned_ports:
            if port not in known_ports:
                logging.debug('Adding eavesdropper for port %s.', port)
                eavesdropper = Eavesdropper(
                    port, mode, config=self._config)
                self._eavesdroppers[port] = eavesdropper
                eavesdropper.start_listening()

        ports = [p for p, _ in scanned_ports]
        for known_port in known_ports:
            if known_port not in ports:
                logging.debug('Removing eavesdropper on port %s.',
                              known_port)
                eavesdropper = self._eavesdroppers[known_port]
                eavesdropper.stop_listening()
                del self._eavesdroppers[known_port]

        logging.debug('finished albion scan.')

    @property
    def sleep_time(self):
        """Gets the seconds that Overlord should sleep between port lookups

        :return: The time in seconds overlord should sleep
        :rtype: int
        """
        try:
            return self._config['app']['overlord']['sleep_time']
        except KeyError:
            return self.DEFAULT_SLEEP_TIME
