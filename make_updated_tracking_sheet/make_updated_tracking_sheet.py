"""Main method and helper methods for make_updated_tracking_sheet.py"""

# Import the version of the script that can be used to tag the output file.
from _version import __version__

# Import module for downloading Google sheet data.
import google_sheet_data

# Import packages needed to query Oracle database.
import cx_Oracle
import sqlalchemy
import crypt

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


def main(file, save_file):
    """
    Main method that does the following work...

    Algorithm
    1. Downloads all results for Google Sheet
    2. Makes a connection to resultsdb
    3. Query's the upload_spr_dose table for all KRAS compounds, run aganist G12D. select BRD, operator, and date_,
    save to a new df
    4. Uses the new df to update the read in table
    5. Creates a new DataFrame by pivoting the updated table on BROAD ID
    6. Saves the updated non-pivoted table and pivoted table to an Excel file.
    """

    try:
        logging.info('Reading in original tracking file...')
        if file:
            t_file_path = input("Please paste the path of the tracking file as a .csv ")
            df_ori_tracking = pd.read_csv(t_file_path)
        else:
            df_ori_tracking = google_sheet_data.get_gsheet_data()
    except Exception:
        raise RuntimeError('Issue reading in tracking file from Google Sheet.')

    # Clean up the original tracking file
    df_ori_tracking['BRD'] = df_ori_tracking['BRD'].apply(lambda x: x[:22])

    # Get all SPR data from Dotmatics
    logging.info('Attempting to download spr results from database...')
    df_spr_dot_data = get_dot_data()

    # Clean the data column in Dotmatics as it is reparet is Y_m_d and we want Y-m-d
    df_spr_dot_data['DATE'] = df_spr_dot_data['DATE'].apply(lambda x: x.replace('_', '-'))
    
    # Drop all duplicate repeats except for the most recent
    df_spr_dot_data = df_spr_dot_data.sort_values(by=['BROAD_ID', 'COMPOUND_MW', 'DATE'])
    df_spr_dot_data = df_spr_dot_data.reset_index(drop=True)

    # Split the database results into two DataFrames by OPERATOR
    df_spr_data_dot_viva = df_spr_dot_data[df_spr_dot_data['OPERATOR'] == 'Viva_Biotech'].copy()
    df_spr_data_dot_viva = df_spr_data_dot_viva.reset_index(drop=True)
    df_spr_dot_data_not_viva = df_spr_dot_data[df_spr_dot_data['OPERATOR'] != 'Viva_Biotech'].copy()
    df_spr_dot_data_not_viva = df_spr_dot_data_not_viva.reset_index(drop=True)

    # For Viva data, update the `DATE_RUN_VIVA` field
    df_spr_data_dot_viva = df_spr_data_dot_viva[['BROAD_ID', 'COMPOUND_MW', 'DATE']]
    df_merge_tracking = pd.merge(left=df_ori_tracking, right=df_spr_data_dot_viva,
                                 left_on='BRD', right_on='BROAD_ID', how='left')
    df_merge_tracking = df_merge_tracking.reset_index(drop=True)
    df_merge_tracking['DATE_RUN_VIVA'] = df_merge_tracking['DATE']

    # Drop unneeded columns
    df_merge_tracking = df_merge_tracking.drop(columns=['BROAD_ID', 'DATE'])

    # For Broad data update the Date run field
    df_spr_dot_data_not_viva = df_spr_dot_data_not_viva[['BROAD_ID', 'DATE']]
    df_merge_tracking = pd.merge(left=df_merge_tracking, right=df_spr_dot_data_not_viva,
                                 left_on='BRD', right_on='BROAD_ID', how='left')
    df_merge_tracking = df_merge_tracking.reset_index(drop=True)
    df_merge_tracking['DATE_RUN_BROAD'] = df_merge_tracking['DATE']

    # Drop unneeded columns
    df_merge_tracking = df_merge_tracking.drop(columns=['BROAD_ID', 'DATE'])

    # Make a copy of the merged DataFrame
    df_merge_tracking_cp = df_merge_tracking.copy()
    df_merge_tracking_cp = df_merge_tracking_cp[['BRD', 'FROM', 'TO', 'DATE_RUN_BROAD', 'DATE_RUN_VIVA', 'DATE_RECEIVED']]

    # Pivot the final results of the tracking sheet so that a Broad ID is a unique identifier
    df_pivoted_tracking = pd.pivot_table(data=df_merge_tracking_cp, index=['BRD'], columns=['FROM', 'TO'],
                                                        aggfunc=lambda x: ' '.join(str(v) for v in x))

    # Replace nan with empty string
    df_pivoted_tracking = df_pivoted_tracking.replace('nan', '', regex=True)

    # Get all the compounds that were received with no data
    df_cmpds_no_data = get_cmpds_no_data(df=df_merge_tracking_cp)

    # Save the output file to an Excel workbook and Save compounds not tested to Google Sheet
    try:
        logging.info('Saving file to Excel workbook...')
        save_output(df_1=df_merge_tracking, df_2=df_pivoted_tracking, df_3=df_cmpds_no_data, save_file=save_file)
        if not file:
            google_sheet_data.write_gsheet_data(df=df_cmpds_no_data)
    except Exception:
        raise RuntimeError('Issue saving the output file.')

    # Return df's for testing purposes
    return [df_merge_tracking_cp, df_pivoted_tracking, df_cmpds_no_data]


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
        raise ConnectionError("\nCannot connect to resultsdb database. Make sure you are on the internal network and "
                              "try again.")

    # Reflect Tables
    metadata = sqlalchemy.MetaData()
    spr_data_tbl = sqlalchemy.Table('upload_spr_dose', metadata, autoload=True, autoload_with=engine)

    stmt = sqlalchemy.select([spr_data_tbl.c.broad_id, spr_data_tbl.c.project_code,
                              spr_data_tbl.c.operator, spr_data_tbl.c.protein_id, spr_data_tbl.c.compound_mw,
                              spr_data_tbl.c.date_]).where(spr_data_tbl.c.project_code == 7279)

    # Execute the statement
    results = conn.execute(stmt).fetchall()

    # Create a DataFrame from results
    df = pd.DataFrame(results)

    # Assign column names to the DataFrame
    df.columns = ['BROAD_ID', 'PROJECT_CODE', 'OPERATOR', 'PROTEIN_ID', 'COMPOUND_MW', 'DATE']

    # TODO: Issue where filtering by bip using sqlalchemy fails
    df = df[df['PROTEIN_ID'] == 'BIP-0384-01']

    # Close the database connection
    conn.close()

    # Turn the results into a DataFrame.
    return df


def get_cmpds_received_not_run(df):
    """
    Method that finds any compounds received at Broad or Viva but not run.

    :param df: Tracking sheet updated with dates the compounds were run as a DataFrame
    """

    # Filter out compounds not going to the Broad or Viva
    df = df[(df['TO'] == 'Broad') | (df['TO'] == 'Viva')]

    # Issue where some cells have spaces and those don't fill with nan.  Fill all empty cells with nan.
    df = df.apply(lambda x: x.str.strip()).replace('', np.nan)

    # Find compounds received at Broad but not run.
    df_broad = df[df['TO'] == 'Broad'].copy()
    df_broad = df_broad.dropna(subset=['DATE_RECEIVED'])
    df_broad = df_broad[df_broad['DATE_RUN_BROAD'].isnull()]
    ls_broad = list(set(df_broad['BRD']))

    # Find compounds received at Viva but not run.
    df_viva = df[df['TO'] == 'Viva'].copy()
    df_viva = df_viva.dropna(subset=['DATE_RECEIVED'])
    df_viva = df_viva[df_viva['DATE_RUN_VIVA'].isnull()]
    ls_viva = list(set(df_viva['BRD']))

    # Make the lists the same length as that is required to construct a DataFrame
    if len(ls_broad) < len(ls_viva):
        ls_broad.extend([np.nan] * (len(ls_viva) - len(ls_broad)))
    if len(ls_viva) < len(ls_broad):
        ls_viva.extend([np.nan] * (len(ls_broad) - len(ls_viva)))

    # Turn results into a DataFrame
    df_cmpds_not_run = pd.DataFrame({'Broad': ls_broad, 'Viva': ls_viva})

    return df_cmpds_not_run


def get_cmpds_no_data(df):
    """
    Method that finds the compounds received at Broad or Viva with no data in database.

    :param df: Tracking sheet updated with dates the compounds were run as a DataFrame
    """

    # Filter out compounds not going to the Broad or Viva
    df = df[(df['TO'] == 'Broad') | (df['TO'] == 'Viva')]

    # Issue where some cells have spaces and those don't fill with nan.  Fill all empty cells with nan.
    df = df.apply(lambda x: x.str.strip()).replace('', np.nan)

    # Create master list of all compounds with no data.
    df_all_not_run = df.dropna(subset=['DATE_RECEIVED']).copy()
    df_all_not_run = df_all_not_run[(df_all_not_run['DATE_RUN_BROAD'].isnull()) &
                                    (df_all_not_run['DATE_RUN_VIVA'].isnull())]
    ls_not_run = set(df_all_not_run['BRD'])

    # Find compounds received at Broad but not run.
    df_broad = df[df['TO'] == 'Broad'].copy()
    df_broad = df_broad.dropna(subset=['DATE_RECEIVED'])
    df_broad = df_broad[df_broad['DATE_RUN_BROAD'].isnull()]
    ls_broad = list(set(df_broad['BRD']))
    ls_broad = [i for i in ls_not_run if i in ls_broad]

    # Find compounds received at Viva but not run.
    df_viva = df[df['TO'] == 'Viva'].copy()
    df_viva = df_viva.dropna(subset=['DATE_RECEIVED'])
    df_viva = df_viva[df_viva['DATE_RUN_VIVA'].isnull()]
    ls_viva = list(set(df_viva['BRD']))
    ls_viva = [i for i in ls_not_run if i in ls_viva]
    
    # Make the lists the same length as that is required to construct a DataFrame
    if len(ls_broad) < len(ls_viva):
        ls_broad.extend([np.nan] * (len(ls_viva) - len(ls_broad)))
    if len(ls_viva) < len(ls_broad):
        ls_viva.extend([np.nan] * (len(ls_broad) - len(ls_viva)))

    # Turn results into a DataFrame
    df_cmpds_no_data = pd.DataFrame({'Broad': ls_broad, 'Viva': ls_viva})

    return df_cmpds_no_data


def save_output(df_1, df_2, df_3, save_file):
    """
    Method that does the work of saving the output to an Excel file.

    :param df_1: Original updated tracking sheet to save in one tab of an excel file
    :param df_2: Pivoted tracking sheet where each row has a unique BRD. Save to another tab.
    :param df_3: DataFrame containing compounds received by Broad and Viva but not run.
    :param save_file: Path and name of the saved file.

    """
    # Note the version is saved to the file name so that data can be linked to the script version.
    logging.info('Saving results to Excel workbook...')
    save_file = save_file.replace('.xlsx', '')
    save_file = os.path.join(homedir, 'Desktop', save_file + '_APPVersion_' + str(__version__))
    save_file = save_file.replace('.', '_')
    save_file = save_file + '.xlsx'

    with pd.ExcelWriter(save_file) as writer:
        df_1.to_excel(writer, sheet_name='Updated_Tracking')
        df_2.to_excel(writer, sheet_name='Pivoted_Tracking')
        df_3.to_excel(writer, sheet_name='Cmpds_Received_no_Data')



