"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
from __future__ import print_function
import abc


class PacketHandler(object):
    """Base packet handler

    Defines the contract with which all packet handlers should follow.
    """
    @abc.abstractmethod
    def handle_packet(self, data, source, **kwargs):
        """Provides a common signature for handling data packets.

        :param data: The data packet
        :param source: The originator of the data packet
        :param kwargs: Any additional arguments that the handler implementation
                       may use.
        """
        return


class PrintPacketHandler(PacketHandler):
    """Printing packet handler.

    Intended mainly for use as a debugging packet handler. This handler will
    print all supplied packets to standard out.
    """
    def handle_packet(self, data, source, **kwargs):
        """Handles the packet by printing it's contents to stdout

        :param data: The data packet
        :param source: The originator of the data packet
        :param kwargs: Any additional arguments that the handler implementation
                       may use.

                       port - Prefix the message with the port the message was
                              received on.
        """
        if 'port' in kwargs:
            print('Port %s: %s' % (kwargs['port'], (data, source)))
        else:
            print((data, source))
