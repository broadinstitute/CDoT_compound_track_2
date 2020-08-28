from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
import logging


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# The ID and range of the spreadsheet.
SPREADSHEET_ID = '1XnC6bZ_iVB7KttuSGa2h8ZlUZx-VsTspwgPOTOxIbeA'
READ_RANGE = 'Tracking!A:J'


def get_gsheet_data():
    """
    Get's all of the data in the specified Google Sheet.
    """

    # Get Credentials from JSON
    logging.info('Attempting to read values to Google Sheet.')
    creds = ServiceAccountCredentials.from_json_keyfile_name('TrackCompounds-1306f02bc0b1.json', SCOPES)
    logging.info('Authorizing Google API credentials.')
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=READ_RANGE).execute()
    data = result.get('values')

    # Turn data into a DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    logging.info('Successfully read G-Sheet data into a DataFrame.')

    return df


def iter_pd(df):
    """
    Helper method that helps write a DataFrame to a Google sheet.
    """
    for val in df.columns:
        yield val
    for row in df.to_numpy():
        for val in row:
            if pd.isna(val):
                yield ""
            else:
                yield val


def pandas_to_sheets(pandas_df, sheet, clear=True):
    """
    Updates all values in a worksheet to match a pandas dataframe
    """

    # Clear the sheet
    if clear:
        sheet.clear()
    (row, col) = pandas_df.shape
    cells = sheet.range("A1:{}".format(gspread.utils.rowcol_to_a1(row + 1, col)))
    for cell, val in zip(cells, iter_pd(pandas_df)):
        cell.value = val
    sheet.update_cells(cells)


def write_gsheet_data(df):
    """
    Method that writes data to a google sheet.

    param: df: DataFrame to write.
    """
    logging.info('Attempting to write values to Google Sheet.')

    # Get API credentials.
    creds = ServiceAccountCredentials.from_json_keyfile_name('TrackCompounds-1306f02bc0b1.json', SCOPES)

    logging.info('Authorizing Google API credentials.')
    # Authorize the credentials
    gc = gspread.authorize(creds)

    # Open the workbook
    workbook = gc.open_by_key(SPREADSHEET_ID)

    # Write data to a Google Sheet
    pandas_to_sheets(pandas_df=df, sheet=workbook.worksheet("Compounds Received but Not Tested"))

    logging.info('Values successfully written to Google Sheet.')



