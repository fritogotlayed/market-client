"""
The MIT License (MIT)
Copyright (c) 2017 AOUtils-Team

For full license details please see the LICENSE file located in the root folder
of the project.
"""
import unittest
import client.console as console

from tests import capture_output


class TestServer(unittest.TestCase):
    """Tests for the server module"""

    @staticmethod
    def test_main():
        """Test main entry point of server module"""
        # Act
        with capture_output() as (out, err):
            console.main()

            # Assert
            output = out.getvalue().strip()
            error = err.getvalue().strip()
            assert output == 'console app'
            assert error == ''
