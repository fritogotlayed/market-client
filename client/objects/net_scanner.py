"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
import os
import subprocess


def find_albion_ports():
    """Scans the computer for any ports that are associated with Albion Online.

    :return: List of port numbers
    :rtype: list
    """
    if os.name == 'nt':
        return _windows_port_lookup()
    return _nix_port_lookup()


def _windows_port_lookup():
    ports = []
    udp_output = subprocess.check_output(
        ['netstat', '-a', '-b', '-e', '-n', '-p', 'UDP'],
        universal_newlines=True)
    tcp_output = subprocess.check_output(
        ['netstat', '-a', '-b', '-e', '-n', '-p', 'TCP'],
        universal_newlines=True)
    ports.extend(_process_windows_output_for_ports(udp_output, 'UDP'))
    ports.extend(_process_windows_output_for_ports(tcp_output, 'TCP'))
    return ports


def _process_windows_output_for_ports(output, protocol):
    ports = []
    processing = False
    last_line = ''
    for line in output.split('\n'):
        if line.startswith('  Proto  Local Address'):
            processing = True

        if processing and ':' in line:
            last_line = line

        if 'Albion-Online.exe' in line:
            start_idx = last_line.index(':') + 1
            stop_idx = last_line.index(' ', start_idx)
            ports.append((int(last_line[start_idx:stop_idx]), protocol))

    return ports


def _nix_port_lookup():
    raise NotImplementedError('Linux/Unix support currently unavailable.')
