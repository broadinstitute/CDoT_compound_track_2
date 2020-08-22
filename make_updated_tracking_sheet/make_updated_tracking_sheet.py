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

# Import packages needed to query Oracle database.
import cx_Oracle
import sqlalchemy
from sqlalchemy import and_
import crypt


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
    df_ori_tracking['BRD'] = df_ori_tracking['BRD'].apply(lambda x: x[:22])

    # Get all SPR data from Dotmatics
    logging.info('Attempting to download spr results from database...')
    df_spr_dot_data = get_dot_data()

    

    df_pivoted_tracking = df_ori_tracking.copy()

    # Save the output file to an Excel workbook
    try:
        logging.info('Saving file to Excel workbook...')
        save_output(df_1=df_ori_tracking, df_2=df_pivoted_tracking, save_file=save_file)
    except Exception:
        raise RuntimeError('Saving the output file.')


def get_data(tracking_file):
    """
    Method that does the work of reading in the original tacking file data into a DataFrame.

    :param tracking_file: Path to the tracking_file
    """
    return pd.read_csv(tracking_file)


def _connect(engine):
    """
    Private method that actually makes the connection to resultsdb
    :param engine: Sqlalchemy engine object
    """
    logging.info('Making a connection attempt to resultsdb...')
    c = engine.connect()
    logging.info('Connection successful, proceeding...')
    return c


def get_dot_data():
    """
    Downloads all SPR results from database and returns a DataFrame consisting of the following headers:

    ['BROAD_ID', 'PROJECT_CODE', 'OPERATOR', 'PROTEIN_ID', 'DATE']

    PROJECT_CODE = 7279
    PROTEIN_ID = BIP-0384-01
    """

    # Create a cryptographic object
    c = crypt.Crypt()

    # Connect to database.
    try:
        host = 'cbpdb01'
        port = '1521'
        sid = 'cbplate'
        user = os.getenv('DB_USER')
        password = str(c.f.decrypt(c.token), 'utf-8')
        sid = cx_Oracle.makedsn(host, port, sid=sid)

        cstr = 'oracle://{user}:{password}@{sid}'.format(
            user=user,
            password=password,
            sid=sid
        )

        engine = sqlalchemy.create_engine(cstr,
                                          pool_recycle=3600,
                                          pool_size=5,
                                          echo=False
                                          )

        # Connect to resultsdb by calling private connection method
        conn = _connect(engine=engine)

    except Exception:
        raise ConnectionError("\nCannot connect to resultsdb database. Make sure you are on the interal network and "
                              "try again.")

    # Reflect Tables
    metadata = sqlalchemy.MetaData()
    spr_data_tbl = sqlalchemy.Table('upload_spr_dose', metadata, autoload=True, autoload_with=engine)

    stmt = sqlalchemy.select([spr_data_tbl.c.broad_id, spr_data_tbl.c.project_code,
                              spr_data_tbl.c.operator, spr_data_tbl.c.protein_id,
                              spr_data_tbl.c.date_]).where(spr_data_tbl.c.project_code == 7279)

    # Execute the statement
    results = conn.execute(stmt).fetchall()

    # Create a DataFrame from results
    df = pd.DataFrame(results)

    # Assign column names to the DataFrame
    df.columns = ['BROAD_ID', 'PROJECT_CODE', 'OPERATOR', 'PROTEIN_ID', 'DATE']

    # TODO: Issue where filtering by bip using sqlalchemy fails
    df = df[df['PROTEIN_ID'] == 'BIP-0384-01']

    # Close the database connection
    conn.close()

    # Turn the results into a DataFrame.
    return df


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


