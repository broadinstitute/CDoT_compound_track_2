import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import logging

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of the spreadsheet.
SPREADSHEET_ID = '1XnC6bZ_iVB7KttuSGa2h8ZlUZx-VsTspwgPOTOxIbeA'
READ_RANGE = 'Tracking!A:J'
WRITE_RANGE = 'Compounds Received but Not Tested!A:B'


def get_credentials():
    """
    Method that generates credentials for the API key that is used connect and download data from google sheets.
    """

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_gsheet_data():
    """
    Get's all of the data in the specified Google Sheet.
    """

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=READ_RANGE).execute()
    data = result.get('values')

    # Turn data into a DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


def write_gsheet_data(df):
    """
    Method that writes data to a google sheet

    param: df: DataFrame to write.
    param: sheet_id: Id of the Google Sheet to write.
    """

    # Get API credentials.
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    response_date = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        valueInputOption='RAW',
        range=WRITE_RANGE,
        body=dict(
            majorDimension='ROWS',
            values=df.T.reset_index().T.values.tolist())
    ).execute()
    logging.info('Values successfully written to Google Sheet')



