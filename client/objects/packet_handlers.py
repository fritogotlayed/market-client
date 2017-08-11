"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
from __future__ import print_function
import abc
import logging


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

    @staticmethod
    def get_packet_handler(config):
        """Gets a packet handler based on the provided configuration dict.

        Uses the provided dictionary to find what type of packet handler to
        return to the caller. In the event that the configuration key cannot be
        found a NoOp handler is returned.

        :param config: config used to find the packet handler
        :type config: dict

        :return: A packet handler
        :rtype: PacketHandler
        :raises ValueError: Unknown configuration value
        """
        if not config:
            raise ValueError("config is required.")

        try:
            value = config['app']['packet_handler']
        except ValueError:
            logging.warning('Could not read config value for '
                            'app.packet_handler. Using NoOp handler.')
            value = 'NoOp'

        logging.debug('%s packet handler was requested.', value)
        if value == 'NoOp':
            return NoOpPacketHandler()
        elif value == 'Print':
            return PrintPacketHandler()
        else:
            raise NotImplementedError(
                'Packet handler (%s) is unknown or invalid. Please check the '
                'spelling or casing before trying again.' % value)


class NoOpPacketHandler(PacketHandler):
    """No Operation packet handler

    Intended mainly for use as a debugging packet handler. This handler will
    not perform any action on the packets thus removing the need for a
    developer to have a version of the backend-aggregator available.
    """
    def handle_packet(self, data, source, **kwargs):
        """Handles the packet by doing nothing.

        :param data: The data packet
        :param source: The originator of the data packet
        :param kwargs: Any additional arguments that the handler implementation
                       may use.

                       port - Prefix the message with the port the message was
                              received on.
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
