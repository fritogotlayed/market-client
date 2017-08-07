"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
from __future__ import print_function
import os

from time import sleep

from client.objects import Eavesdropper


def main():
    """Entry point for the market data packet capture client."""
    print('Console app is running on PID %s.' % os.getpid())
    ports = [60552, 49252]
    eavesdroppers = []
    for port in ports:
        eavesdropper = Eavesdropper(port)
        eavesdroppers.append(eavesdropper)
        eavesdropper.start_listening()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('Gracefully shutting down client.')
        for eavesdropper in eavesdroppers:
            eavesdropper.stop_listening()


if __name__ == '__main__':
    main()
