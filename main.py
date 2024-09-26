import streamlit as st
import google.auth
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define Google Sheets API Scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Use credentials from Streamlit Secrets
def get_credentials():
    creds = None
    if 'token.json' in os.listdir():
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use OAuth credentials stored in Streamlit Secrets
            client_config = {
                "installed": {
                    "client_id": st.secrets["oauth_client"]["client_id"],
                    "client_secret": st.secrets["oauth_client"]["client_secret"],
                    "auth_uri": st.secrets["oauth_client"]["auth_uri"],
                    "token_uri": st.secrets["oauth_client"]["token_uri"],
                    "redirect_uris": [st.secrets["oauth_client"]["redirect_uri"]],
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials to a file
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# Get authenticated Google Sheets service
def get_sheets_service():
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    return service

# Example of updating a Google Sheets cell
def update_sheet_cell(sheet_id, sheet_name, cell, value):
    try:
        service = get_sheets_service()
        range_ = f"{sheet_name}!{cell}"
        body = {'values': [[value]]}
        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_,
            valueInputOption="RAW",
            body=body
        ).execute()
        return True
    except Exception as error:
        st.error(f"An error occurred: {error}")
        return False

# Streamlit app interface
def main():
    sheet_id = "YOUR_SHEET_ID"
    sheet_name = "YOUR_SHEET_NAME"
    cell = "A2"
    new_status = "Accepted"

    if st.button("Update Status"):
        if update_sheet_cell(sheet_id, sheet_name, cell, new_status):
            st.success(f"Updated status for {cell} to {new_status}")
        else:
            st.error(f"Failed to update status for {cell}")

if __name__ == "__main__":
    main()
