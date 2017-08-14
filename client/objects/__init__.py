"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
import logging
import os
import threading


from client.objects.packet_handlers import PacketHandler
if os.name == 'nt':
    from client.objects.windows import PCap


class Eavesdropper(object):
    """Listens on the specified port and captures the UDP traffic"""
    def __init__(self, device_id, config=None):
        self._device_id = device_id
        self._pcap = None  # type: PCap
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
            self._pcap = PCap(self._device_id, self._handler.handle_packet)
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
        if self._pcap:
            self._pcap.stop()

    def _listen(self):
        if os.environ.get('AOUTILS_MC_TESTING', False):
            return

        # while self._thread_run:
        logging.debug('Starting PCap listener.')
        self._pcap.start()

    def _cleanup(self):
        if self._pcap:
            self._pcap.stop()


class Overlord(object):
    """Controls the entire packet capturing process"""
    DEFAULT_SLEEP_TIME = 5

    def __init__(self, config=None):
        self._eavesdroppers = []
        self._config = config or {}
        self._running = False

    def oversee(self):
        """Starts the overlord on whatever scrape methodology is configured

        This is a blocking operation.
        """
        self._running = True
        if self._config['app']['scrape_mode'] == 'packet_capture':
            self._process_packet_scraping()

        try:
            logging.info(
                'Press the Enter key or ctrl+c to gracefully shut down.')
            _ = input()
            self._running = False
        except KeyboardInterrupt:
            pass
        finally:
            logging.debug('Gracefully closing eavesdroppers.')
            eavesdroppers = list(self._eavesdroppers)
            for eavesdropper in eavesdroppers:
                eavesdropper.stop_listening()
                self._eavesdroppers.remove(eavesdropper)

    def _process_packet_scraping(self):
        """Starts the overlords port listening process.

        This is a blocking operation. Ports will be updated based on whatever
        values are configured in the supplied configuration."""
        logging.debug('beginning albion scan.')

        devices_list = PCap.list_devices()
        device_names = self._config['app']['scrape_devices']

        if len(device_names) == 1:
            if device_names[0].lower() == 'all':
                logging.debug('User specified all devices for capture.')
                device_names = [d['name'] for d in devices_list]

        for dev in devices_list:
            if dev['name'] in device_names:
                logging.debug('Starting eavesdropper for device %s.',
                              dev['name'])
                eavesdropper = Eavesdropper(dev['id'], self._config)
                self._eavesdroppers.append(eavesdropper)
                eavesdropper.start_listening()
        # NOTE: Leaving the below code as it will get re-purposed when we begin
        #       acting on captured packets
        # for port, mode in scanned_ports:
        #     if port not in known_ports:
        #         logging.debug('Adding eavesdropper for port %s.', port)
        #         eavesdropper = Eavesdropper(
        #             port, mode, config=self._config)
        #         self._eavesdroppers[port] = eavesdropper
        #         eavesdropper.start_listening()
        #
        # ports = [p for p, _ in scanned_ports]
        # for known_port in known_ports:
        #     if known_port not in ports:
        #         logging.debug('Removing eavesdropper on port %s.',
        #                       known_port)
        #         eavesdropper = self._eavesdroppers[known_port]
        #         eavesdropper.stop_listening()
        #         del self._eavesdroppers[known_port]

        logging.debug('finished albion scan.')

    @property
    def sleep_time(self):
        """Gets the seconds that Overlord should sleep between port lookups

        :return: The time in seconds overlord should sleep
        :rtype: int
        """
        try:
            return self._config['app']['port_scan_interval']
        except KeyError:
            return self.DEFAULT_SLEEP_TIME
