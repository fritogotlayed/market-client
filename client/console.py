"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
from __future__ import print_function
# Standard Libs
import logging
import os

from os.path import basename, abspath

# Other Libs
import yaml

from client.objects import Overlord
from client import logging_helper


def _get_current_dir():
    full_path = abspath(__file__)
    idx = full_path.index(basename(full_path))
    return full_path[:idx]


def main():
    """Entry point for the market data packet capture client."""
    config = yaml.load(open(_get_current_dir() + 'config.yml'))
    logging_helper.initialize(config)

    logging.info('Console app is running on PID %s.', os.getpid())
    lord = Overlord(config=config)
    lord.oversee()
    logging.info('Console app shut down.')

if __name__ == '__main__':
    main()
