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
from make_updated_tracking_sheet.cli import run_main

# Import modules under test
from make_updated_tracking_sheet.make_updated_tracking_sheet import get_data

class TestInvokeCLI(TestCase):
    """Class for testing the invocation of the 'make_updated_tracking_sheet' on the command line"""

    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_CLI(self, mock_1, mock_2):
        """Test invocation of the 'make_updated_tracking_sheet' script"""

        # Use the click CliRunner object for testing Click implemented Cli programs.
        runner = CliRunner()
        result = runner.invoke(run_main, ['--tracking_file', './tests/fixtures/compound_shipment_tracking_Tracking.csv',
                                      '--save_file','Test.xlsx'])

        self.assertEqual(0, result.exit_code)


class TestIOMethods(TestCase):
    """Class for testing something"""

    tracking_file_path = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Method used to setup fixtures for testing
        :return:
        """

        # Variable to be used in all tests in this class.
        cls.tracking_file_path = './tests/fixtures/compound_shipment_tracking_Tracking.csv'

    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_get_data_is_df(self, mock_1, mock_2):
        """
        Test that the get_data() method returns a Pandas DataFrame
        :param mock_1: Mocks the pandas method that writes a dataframe to an Excel workbook.
        :param mock_2: Mocks the pandas ExcelWriter class.

        """

        result = get_data(self.tracking_file_path)
        self.assertEqual(pd.DataFrame, result.__class__)

    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_get_data_expected_cols(self, mock_1, mock_2):

        expected_cols = ['BRD', 'NAME', 'FROM',	'TO',
                         'DATE_SENT', 'BARCODE',
                         'DATE_RECEIVED', 'DATE_RUN_VIVA', 'DATE_RUN_BROAD',
                         'TRACKING_NUMBER', "BRD's To Find"]

        result = get_data(self.tracking_file_path)

        for header in expected_cols:
            self.assertIn(header, result.columns)


class test_save(TestCase):
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
