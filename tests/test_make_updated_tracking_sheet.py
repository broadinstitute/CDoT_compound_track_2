"""Module for testing make_updated_tracking_sheet"""

# Import modules from the unittesting framework
from unittest import TestCase
from unittest.mock import patch

# Import pandas and numpy
import pandas as pd
import numpy as np

# Import re for testing regular expressions
import re

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
    """Class for testing the main method of the app"""

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

    @patch('make_updated_tracking_sheet.make_updated_tracking_sheet.get_dot_data')
    @patch('google_sheet_data.get_gsheet_data')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_df_merge_tracking_brd_22_char(self, mock_1, mock_2, mock_3, mock_4):

        # Mock returns for getting G-Sheet Data and Database data
        mock_3.return_value = pd.read_csv('tests/fixtures/compound_shipment_tracking_example.csv')
        mock_4.return_value = pd.read_csv('tests/fixtures/dotmatics_data_example.csv')

        # Call the main method under test.
        result = main(file=False, save_file=self.tracking_file_path)

        for brd in result[0]['BRD']:
            self.assertEqual(22, len(brd))

    @patch('make_updated_tracking_sheet.make_updated_tracking_sheet.get_dot_data')
    @patch('google_sheet_data.get_gsheet_data')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_df_merge_tracking_data_format(self, mock_1, mock_2, mock_3, mock_4):

        # Mock returns for getting G-Sheet Data and Database data
        mock_3.return_value = pd.read_csv('tests/fixtures/compound_shipment_tracking_example.csv')
        mock_4.return_value = pd.read_csv('tests/fixtures/dotmatics_data_example.csv')

        # Call the main method under test.
        result = main(file=False, save_file=self.tracking_file_path)

        for date in result[0]['DATE_RECEIVED']:
            if date is np.nan:
                continue
            self.assertNotEqual(None, re.match(r'\d{4}-\d{2}-\d{2}', date))

    @patch('make_updated_tracking_sheet.make_updated_tracking_sheet.get_dot_data')
    @patch('google_sheet_data.get_gsheet_data')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_compounds_no_data_broad(self, mock_1, mock_2, mock_3, mock_4):

        # Mock returns for getting G-Sheet Data and Database data
        mock_3.return_value = pd.read_csv('tests/fixtures/compound_shipment_tracking_example.csv')
        mock_4.return_value = pd.read_csv('tests/fixtures/dotmatics_data_example.csv')

        # Call the main method under test.
        result = main(file=False, save_file=self.tracking_file_path)

        ls_broad = list(result[2]['Broad'])

        expected = ['BRD-K00080713-014-01-9', 'BRD-A00072919-001-02-9', 'BRD-A00071633-001-02-9',
                   'BRD-K00080818-014-01-9', 'BRD-K00071602-001-01-9', 'BRD-K00080819-014-01-9',
                   'BRD-K00080971-001-01-9', 'BRD-A00080735-014-01-9', 'BRD-A00071634-001-02-9',
                   'BRD-K00080817-014-01-9', 'BRD-K00080968-001-01-9', 'BRD-K00030927-014-02-9',
                   'BRD-A00072914-001-01-9', 'BRD-K00080969-001-01-9', 'BRD-A00071632-001-02-9',
                   'BRD-K00071600-001-01-9', 'BRD-A00072915-001-01-9', 'BRD-A00080829-001-01-9',
                   'BRD-A00080830-001-01-9', 'BRD-A00080714-014-01-9', 'BRD-A00080716-014-01-9',
                   'BRD-K00071601-001-01-9', 'BRD-A00080715-014-01-9']

        for brd in ls_broad:
            self.assertIn(brd, expected)

    @patch('make_updated_tracking_sheet.make_updated_tracking_sheet.get_dot_data')
    @patch('google_sheet_data.get_gsheet_data')
    @patch('pandas.ExcelWriter')
    @patch('pandas.DataFrame.to_excel')
    def test_compounds_no_data_viva(self, mock_1, mock_2, mock_3, mock_4):

        # Mock returns for getting G-Sheet Data and Database data
        mock_3.return_value = pd.read_csv('tests/fixtures/compound_shipment_tracking_example.csv')
        mock_4.return_value = pd.read_csv('tests/fixtures/dotmatics_data_example.csv')

        # Call the main method under test.
        result = main(file=False, save_file=self.tracking_file_path)

        ls_viva = list(result[2]['Viva'])

        expected = ['BRD-K00080713-014-01-9', 'BRD-A00072919-001-02-9', 'BRD-A00071633-001-02-9',
                    'BRD-K00080818-014-01-9', 'BRD-A00080754-014-01-9', '\xa0BRD-A00071634-001-02-',
                    'BRD-K00080819-014-01-9', 'BRD-K00080971-001-01-9', 'BRD-A00080735-014-01-9',
                    'BRD-K00080817-014-01-9', 'BRD-K00080968-001-01-9', 'BRD-K00030927-014-02-9',
                    'BRD-A00072914-001-01-9', 'BRD-K00027014-001-02-9', 'BRD-K00080969-001-01-9',
                    'BRD-A00071632-001-02-9', 'BRD-A00072915-001-01-9', 'BRD-A00080829-001-01-9',
                    'BRD-A00080830-001-01-9', 'BRD-A00080714-014-01-9', 'BRD-A00080716-014-01-9',
                    'BRD-A00080715-014-01-9', np.nan]

        for brd in ls_viva:
            self.assertIn(brd, expected)
