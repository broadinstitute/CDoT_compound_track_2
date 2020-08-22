"""Module for testing make_updated_tracking_sheet"""

# Import modules from the unittesting framework
from unittest import TestCase
from unittest.mock import patch

# Import pandas and numpy
import pandas as pd
import numpy as np

# Import click testing module
from click.testing import CliRunner

# Import the main method of the script for the command line interface entry point.
from make_updated_tracking_sheet.cli import main


class test_Cli(TestCase):
    """Class for testing the invocation of the 'make_updated_tracking_sheet' on the command line"""

    def test_Cli_somthing(self):
        """Test invocation of the 'make_updated_tracking_sheet' script"""

        # Use the click CliRunner object for testing Click implemented Cli programs.
        runner = CliRunner()
        result = runner.invoke(main, ['--option_1', 'EXAMPLE_path_to_fixture_', 'option_2',
                                                        'input_2'])

        self.assertEqual(0, result.exit_code)


class test_something(TestCase):
    """Class for testing something"""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Method used to setup fixtures for testing
        :return:
        """

        # Variable to be used in all tests in this class.
        cls.var_name = ''
        pass

    @patch('full.path.to.some.method', return_value='return_something')
    def test_something(self, mock_1):
        """
        Test something...
        :param mock_1: Mocks the 'fill this in' method
        """
        pass
