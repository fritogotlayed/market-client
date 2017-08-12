"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
import unittest
import client.console as console

from tests import capture_output
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch


class TestServer(unittest.TestCase):
    """Tests for the server module"""

    @staticmethod
    @patch('client.console.sleep')
    def test_main_starts_application(patched_sleep):
        """Test main entry point of server module"""
        # Arrange
        patched_sleep.side_effect = KeyboardInterrupt()

        # Act
        with capture_output() as (out, err):
            console.main()

            # Assert
            output = out.getvalue().strip()  # type: str
            error = err.getvalue().strip()   # type: str
            assert output.startswith('Console app is running on PID ') is True
            assert error == ''

    @staticmethod
    @patch('client.console.sleep')
    def test_main_application_stop(patched_sleep):
        """Test main entry point of server module"""
        # Arrange
        patched_sleep.side_effect = KeyboardInterrupt()

        # Act
        with capture_output() as (out, err):
            console.main()

            # Assert
            output = out.getvalue().strip()  # type: str
            error = err.getvalue().strip()   # type: str
            assert output.endswith('Gracefully shutting down client.') is True
            assert error == ''
