import streamlit as st
import google.auth
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define Google Sheets API Scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Function to get Google Sheets API credentials from Streamlit secrets
def get_credentials():
    creds = None
    # Check if token.json exists, it stores credentials for re-use
    if 'token.json' in os.listdir():
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, authenticate the user
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
            # Start OAuth flow to authenticate user
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

# Function to get Google Sheets service after authentication
def get_sheets_service():
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    return service

# Function to update a specific cell in Google Sheets
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

# Main Streamlit interface
def main():
    st.title("Google Sheets Status Updater")
    
    # Input Google Sheets details
    sheet_id = st.text_input("Enter Google Sheet ID", value="YOUR_SHEET_ID")
    sheet_name = st.text_input("Enter Google Sheet Name", value="YOUR_SHEET_NAME")
    cell = st.text_input("Enter Cell to Update", value="A2")
    new_status = st.text_input("Enter New Status", value="Accepted")
    
    # Button to update the status in the Google Sheet
    if st.button("Update Status"):
        if update_sheet_cell(sheet_id, sheet_name, cell, new_status):
            st.success(f"Updated status for {cell} to {new_status}")
        else:
            st.error(f"Failed to update status for {cell}")

if __name__ == "__main__":
    main()
