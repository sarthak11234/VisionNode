import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# Scopes required by the Google Drive and Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

class GoogleHandler:
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.creds = None
        self.service = None
        
        self._authenticate()

    def _authenticate(self):
        """Authenticates with Google using the Service Account JSON."""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Google credentials file not found at {self.credentials_path}")
            
        self.creds = Credentials.from_service_account_file(self.credentials_path, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=self.creds)
        logger.info("Successfully authenticated with Google Cloud via Service Account.")

    def fetch_pending_rows(self, sheet_range: str) -> list[dict]:
        """
        Reads the Google Sheet and returns a list of dictionaries representing the rows.
        A. IDEMPOTENCY CHECK:
        Filters out any row where the 'Status' column is 'Sent'.
        """
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=sheet_range).execute()
            values = result.get('values', [])

            if not values:
                logger.info("No data found in sheet.")
                return []

            # Assume first row constitutes headers
            headers = values[0]
            rows = []
            
            # Map remaining rows to a dictionary
            for row_idx, row_values in enumerate(values[1:], start=2): # +2 because real rows start at row 2 in Excel/Sheets
                # Pad row_values if it's shorter than headers.
                padded_row = row_values + [''] * (len(headers) - len(row_values))
                row_dict = dict(zip(headers, padded_row))
                row_dict['_row_index'] = row_idx # keep track of row number for updating later
                
                # Ensure Idempotency Check:
                # We skip processing if 'Status' is explicitly 'Sent'
                status = row_dict.get('Status', '').strip().lower()
                if status != 'sent':
                    rows.append(row_dict)
                else:
                    logger.debug(f"Row {row_idx} skipped. Status already 'Sent'.")
                    
            return rows

        except HttpError as err:
            logger.error(f"An error occurred fetching rows: {err}")
            return []

    def update_row_status(self, sheet_name: str, row_index: int, status_letter_column: str, new_status: str):
        """
        Updates the specific cell corresponding to the 'Status' column for a row.
        Example range notation: "Sheet1!D2"
        """
        range_notation = f"{sheet_name}!{status_letter_column}{row_index}"
        
        body = {
            'values': [[new_status]]
        }
        
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, 
                range=range_notation,
                valueInputOption="RAW", 
                body=body
            ).execute()
            logger.info(f"Updated {range_notation} to '{new_status}'")
            
        except HttpError as err:
            logger.error(f"Failed to update row status at {range_notation}: {err}")
