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

# Import main method directly
from make_updated_tracking_sheet.make_updated_tracking_sheet import main

# Load environmental variables
from dotenv import load_dotenv


class TestInvokeCLI(TestCase):
    """Class for testing the invocation of the 'make_updated_tracking_sheet' on the command line"""

    @patch('make_updated_tracking_sheet.make_updated_tracking_sheet.get_dot_data')
    @patch('google_sheet_data.get_gsheet_data')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_CLI(self, mock_1, mock_2, mock_3, mock_4):
        """Test invocation of the 'make_updated_tracking_sheet' script"""

        # Mock returns for getting G-Sheet Data and Database data
        mock_3.return_value = pd.read_csv('tests/fixtures/compound_shipment_tracking_example.csv')
        mock_4.return_value = pd.read_csv('tests/fixtures/dotmatics_data_example.csv', sep=',')
        
        # Load environmental vars
        load_dotenv()

        # Use the click CliRunner object for testing Click implemented Cli programs.
        runner = CliRunner()
        result = runner.invoke(run_main, ['--save_file', 'Test'])

        self.assertEqual(0, result.exit_code)


class TestMain(TestCase):
    """Class for testing something"""

    tracking_file_path = 'tests/fixtures/compound_shipment_tracking_example.csv'
    df_dot_data_path = 'tests/fixtures/dotmatics_data_example.csv'

    @classmethod
    def setUpClass(cls) -> None:
        """
        Method used to setup fixtures for testing
        :return:
        """
        # Variable to be used in all tests in this class.
        cls.tracking_file = pd.read_csv(cls.tracking_file_path)
        cls.df_dot_data = pd.read_csv(cls.df_dot_data_path)

    @patch('make_updated_tracking_sheet.make_updated_tracking_sheet.get_dot_data')
    @patch('google_sheet_data.get_gsheet_data')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_get_data_expected_cols(self, mock_1, mock_2, mock_3, mock_4):

        # Mock returns for getting G-Sheet Data and Database data
        mock_3.return_value = pd.read_csv('tests/fixtures/compound_shipment_tracking_example.csv')
        mock_4.return_value = pd.read_csv('tests/fixtures/dotmatics_data_example.csv')

        expected_cols = ['BRD', 'FROM', 'TO', 'DATE_RUN_BROAD', 'DATE_RUN_VIVA', 'DATE_RECEIVED']

        result = main(file=False, save_file=self.tracking_file_path)

        for header in expected_cols:
            self.assertIn(header, result[0].columns)


# class test_save(TestCase):
#     """Class for testing something"""
#
#     @classmethod
#     def setUpClass(cls) -> None:
#         """
#         Method used to setup fixtures for testing
#         :return:
#         """
#
#         # Variable to be used in all tests in this class.
#         cls.var_name = ''
#         pass

    # @patch('full.path.to.some.method', return_value='return_something')
    # def test_something(self, mock_1):
    #     """
    #     Test something...
    #     :param mock_1: Mocks the 'fill this in' method
    #     """
    #     pass
