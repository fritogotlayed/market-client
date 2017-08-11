"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
import unittest
import client.console as console

try:
    from mock import patch
    from mock import MagicMock
except ImportError:
    from unittest.mock import patch
    from unittest.mock import MagicMock


class TestServer(unittest.TestCase):
    """Tests for the server module"""

    @staticmethod
    @patch('client.console.logging')
    @patch('client.console.Overlord')
    def test_main_starts_application(mock_overlord, mock_logging):
        """Test main entry point of server module starts properly.

        :type mock_overlord: MagicMock
        """
        # Arrange
        mock_lord = MagicMock()
        mock_overlord.return_value = mock_lord

        # Act
        console.main()

        # Assert
        mock_lord.oversee.assert_called_once()

        # [call index][0-args,1-kwargs][arg index]
        info_calls = mock_logging.info.call_args_list
        assert info_calls[0][0][0] == 'Console app is running on PID %s.'

    @staticmethod
    @patch('client.console.logging')
    @patch('client.console.Overlord')
    def test_main_application_stop(mock_overlord, mock_logging):
        """Test main entry point of server module exits gracefully."""
        # Arrange
        mock_lord = MagicMock()
        mock_overlord.return_value = mock_lord

        # Act
        console.main()

        # Assert
        mock_lord.oversee.assert_called_once()

        # [call index][0-args,1-kwargs][arg index]
        info_calls = mock_logging.info.call_args_list
        assert info_calls[1][0][0] == 'Console app shut down.'
