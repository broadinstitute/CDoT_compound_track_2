"""Main method and helper methods for make_updated_tracking_sheet.py"""

# Import the version of the script that can be used to tag the output file.
from _version import __version__

# Import system packages for determining what OS the script is running on..
import platform
import os

# Import data wrangling Python packages
import pandas as pd
import numpy as np

# Import logging package
# Configure logger
import logging
logging.basicConfig(level=logging.INFO)


# Get the users home directory
if platform.system() == "Windows":
    from pathlib import Path

    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']


def main(tracking_file, save_file):
    """
    Main method for script...
    """

    """
    1. Ask user to paste the path of the Google spreadsheet
    2. Read in the csv file.
    3. Make a connection to resultsdb
    4. Query the upload_spr_dose table for all KRAS compounds, run aganist G12D. select BRD, operator, and date_, 
    save to a new df
    5. Use the new df to update the read in table
    6. Create a new DataFrame by pivoting the updated table on BROAD ID
    7. Save the updated non-pivoted table and pivoted table to an Excel file.
    
    """
    try:
        logging.info('Reading in original tracking file...')
        df_ori_tracking = get_data(tracking_file=tracking_file)
    except Exception:
        raise RuntimeError('Issue reading in tracking file. Make sure the file is saved as a .csv file and try again.')

    # Clean up the original tracking file
    df_ori_tracking_cleaned = df_ori_tracking.copy()
    df_pivoted_tracking = df_ori_tracking_cleaned.copy()

    # Save the output file to an Excel workbook
    try:
        logging.info('Saving file to Excel workbook...')
        save_output(df_1=df_ori_tracking_cleaned, df_2=df_pivoted_tracking, save_file=save_file)
    except Exception:
        raise RuntimeError('Saving the output file.')


def get_data(tracking_file):
    """
    Method that does the work of reading in the original tacking file data into a DataFrame.

    :param tracking_file: Path to the tracking_file
    """
    return pd.read_csv(tracking_file)


def save_output(df_1, df_2, save_file):
    """
    Method that does the work of saving the output to an Excel file.

    :param df_1: Original updated tracking sheet to save in one tab of an excel file
    :param df_2: Pivoted tracking sheet where each row has a unique BRD. Save to another tab.
    :param save_file: Path and name of the saved file.

    """

    with pd.ExcelWriter(save_file) as writer:
        df_1.to_excel(writer, sheet_name='Updated_Tracking')
        df_2.to_excel(writer, sheet_name='Pivoted_Tracking')


