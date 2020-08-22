"""Main method and helper methods for make_updated_tracking_sheet.py"""

# Import the version of the script that can be used to tag the output file.
from _version import __version__

# Import system packages for determining what OS the script is running on..
import platform
import os

# Import data wrangling Python packages
import pandas as pd
import numpy as np


# Get the users home directory
if platform.system() == "Windows":
    from pathlib import Path

    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']


def main(arg_1, arg_2, flag):
    """
    Main method for script...
    """

    """"
    1. Ask user to paste the path of the Google spreadsheet
    2. Read in the csv file.
    3. Make a connection to resultsdb
    4. Query the upload_spr_dose table for all KRAS compounds, run aganist G12D. select BRD, operator, and date_, 
    save to a new df
    5. Use the new df to update the read in table
    6. Create a new DataFrame by pivoting the updated table on BROAD ID
    7. Save the updated non-pivoted table and pivoted table to an Excel file.
    
    """




    pass