"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.

The intent of this module is to hold any code that is dependent on windows
specific libraries.
"""
import ctypes
import logging

from collections import Callable

try:
    from client.objects import pcap_types as ptypes
except OSError:
    logging.fatal('Could not properly import windows pcap library. Could it '
                  'be that NPCap is not installed?')
    raise


class PCap(object):
    """Wrapper around pcap library.

    This class handles the allocation and de-allocation of packet capturing
    objects.
    """
    HANDLER_SIGNATURE = ctypes.CFUNCTYPE(None,
                                         ctypes.POINTER(ctypes.c_ubyte),
                                         ctypes.POINTER(ptypes.pcap_pkthdr),
                                         ctypes.POINTER(ctypes.c_ubyte))

    def __init__(self, device_id, callback):
        """Creates a new packet capture interface

        :param device_id: The device id on which to capture
        :type device_id: str

        :param callback: The method to call when data is captured
        :type callback: Callable
        """
        if not isinstance(callback, Callable):
            raise ValueError('callback is not callable.')

        self._device_id = device_id.encode('utf-8')
        self._callback = callback
        self._running = False
        self._handle = None
        self._err_buffer = ctypes.create_string_buffer(ptypes.PCAP_ERRBUF_SIZE)
        self._callback_wrapper = self.HANDLER_SIGNATURE(self._pcap_callback)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def __del__(self):
        self._cleanup()

    @staticmethod
    def list_devices():
        """Lists the net devices on the system.

        :return: A list of dicts containing the id and name of network
                 interfaces on the system.
        :rtype: list
        """
        all_devices = None
        data = []
        try:
            all_devices = ctypes.POINTER(ptypes.pcap_if)()
            err_buffer = ctypes.create_string_buffer(ptypes.PCAP_ERRBUF_SIZE)
            if (ptypes.pcap_findalldevs(
                    ctypes.byref(all_devices), err_buffer) == -1):
                raise Exception('Could not find all devices.')

            while bool(all_devices):
                data.append({
                    'id': all_devices.contents.name.decode('utf-8'),
                    'name': all_devices.contents.description.decode('utf-8')
                })
                all_devices = all_devices.contents.next

        finally:
            if all_devices:
                ptypes.pcap_freealldevs(all_devices)

        return data

    def start(self, promiscuous=False, timeout=1000, snap_length=2**16):
        """Starts capturing packets

        :param promiscuous: Specifies if the interface should be promiscuous.
                            In promiscuous mode all traffic on the interface is
                            sniffed for processing where in non-promiscuous
                            mode only traffic directed at this host is sniffed.
        :type promiscuous: bool

        :param timeout: Milliseconds to wait for traffic to arrive at the host.
        :type timeout: int

        :param snap_length: Specifies the snapshot length for the handle.
        :type snap_length: int
        """
        # Convert promiscuous to int for pcap method signature
        promiscuous = 1 if promiscuous else 0

        if self._running is False and self._device_id is not None:
            self._running = True
            self._handle = ptypes.pcap_open_live(
                self._device_id, snap_length, promiscuous, timeout,
                self._err_buffer)

            ptypes.pcap_loop(self._handle, 0, self._callback_wrapper, None)

    def stop(self):
        """Stops the pcap listening loop from running."""
        if self._running is True:
            self._running = False
            ptypes.pcap_breakloop(self._handle)

    def _pcap_callback(self, param, header, pkt_pointer):
        try:
            pkt_data = ctypes.string_at(pkt_pointer, header.contents.len)
            self._callback(param, header, pkt_data)
        except KeyboardInterrupt:
            self.stop()
            raise

    def _cleanup(self):
        if self._handle is not None:
            ptypes.pcap_close(self._handle)
            self._handle = None
