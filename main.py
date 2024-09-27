import pandas as pd
import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Set page configuration at the very beginning
st.set_page_config(layout="wide")

def get_google_sheets_service():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    return service

def get_sheet_data(service, spreadsheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        raise Exception('No data found.')
    
    headers = values[0]
    rows = values[1:]
    
    # Find the maximum number of columns
    max_cols = max(len(headers), max(len(row) for row in rows))
    
    # Pad headers and rows to match the maximum number of columns
    headers = headers + [''] * (max_cols - len(headers))
    rows = [row + [''] * (max_cols - len(row)) for row in rows]
    
    df = pd.DataFrame(rows, columns=headers)
    return df


def update_sheet_cell(service, spreadsheet_id, sheet_name, row, column_name, value):
    # Get the header row from the sheet
    header_range = f"'{sheet_name}'!1:1"  # Assumes headers are in the first row
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=header_range).execute()
    headers = result.get('values', [])[0]
    
    # Find the index of the column that matches column_name
    try:
        column_index = headers.index(column_name) + 1  # Google Sheets columns are 1-based
    except ValueError:
        st.error(f"Column '{column_name}' not found in the sheet headers.")
        return False
    
    # Convert column index to letter (A, B, C, etc.)
    column_letter = chr(64 + column_index)  # Converts 1 -> A, 2 -> B, etc.
    range_name = f"'{sheet_name}'!{column_letter}{row}"  # E.g., 'Status' column updates at this row
    
    body = {
        'values': [[value]]
    }
    
    try:
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, 
            range=range_name,
            valueInputOption='RAW',  # RAW means the value will be input directly as-is
            body=body
        ).execute()
        return True
    except Exception as e:
        st.error(f"Error updating cell: {str(e)}")
        return False

# In your loop for saving status changes
if 'status_updates' in st.session_state and st.session_state.status_updates and st.button("Save Status Changes", key="save_status"):
    for index, new_status in st.session_state.status_updates.items():
        try:
            # Update the 'Status' column dynamically by name
            if update_sheet_cell(service, spreadsheet_id, sheet_name, index + 2, 'Status', new_status):
                st.success(f"Updated status for row {index + 2} to {new_status}")
            else:
                st.error(f"Failed to update status for row {index + 2}")
        except Exception as e:
            st.error(f"Error updating row {index + 2}: {str(e)}")
    
    # Clear status updates after saving
    st.session_state.status_updates.clear()
    st.rerun()  # Refresh the page to show updated data

def show_login_page():
    st.markdown("<h1 style='text-align: center;'>Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        if st.button("Login", use_container_width=True, key="login_button"):
            if check_credentials(username, password):
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Invalid username or password")

def check_credentials(username, password):
    return username == st.secrets["app"]["username"] and password == st.secrets["app"]["password"]

def show_main_page(service, spreadsheet_id, sheet_name):
    if 'status_updates' not in st.session_state:
        st.session_state.status_updates = {}

    col1, col2, col3 = st.columns([3,1,1])
    with col3:
        if st.button("Logout", key="logout_button"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    st.header("Data from Google Sheets")
    try:
        df = get_sheet_data(service, spreadsheet_id, sheet_name)
        
        # Check if 'Timestamp' column exists
        if 'Timestamp' not in df.columns:
            st.error("The 'Timestamp' column is missing from the sheet data.")
            return
        
        # Convert 'Timestamp' column to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        # Handle cases where Timestamp conversion fails
        if df['Timestamp'].isnull().all():
            st.error("Unable to parse any dates from the 'Timestamp' column. Please check the data format.")
            return
        
        # Remove rows with NaT (Not a Time) values in Timestamp
        df = df.dropna(subset=['Timestamp'])
        
        if df.empty:
            st.warning("No valid data remaining after filtering out rows with invalid timestamps.")
            return
        
        # Create filters
        col1, col2 = st.columns(2)
        with col1:
            years = sorted(df['Timestamp'].dt.year.unique(), reverse=True)
            if not years:
                st.error("No valid years found in the data.")
                return
            selected_year = st.selectbox("Select Year", years)
        
        with col2:
            months = [
                "January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"
            ]
            selected_month = st.selectbox("Select Month", months)
        
        # Apply filters
        filtered_df = df[
            (df['Timestamp'].dt.year == selected_year) & 
            (df['Timestamp'].dt.month == months.index(selected_month) + 1)
        ]
        
        if filtered_df.empty:
            st.warning(f"No data available for {selected_month} {selected_year}")
            return
        
        # Display filtered data
        st.dataframe(filtered_df)
        
        # Display information about empty columns
        empty_cols = filtered_df.columns[filtered_df.isna().all()].tolist()
        if empty_cols:
            st.warning(f"The following columns are empty or have no data: {', '.join(empty_cols)}")
        
        # Display row count
        st.info(f"Showing {len(filtered_df)} rows for {selected_month} {selected_year}")
        
        # Separate section for status update table
        st.header("Update Status")
        
        # Create a DataFrame for status updates
        status_df = filtered_df[['Timestamp', 'Status']].copy()
        status_df['Row'] = status_df.index + 2  # +2 because of 0-indexing and header row
        status_df = status_df[['Row', 'Timestamp', 'Status']]
        
        # Use st.data_editor for an editable table
        edited_df = st.data_editor(
            status_df,
            column_config={
                "Row": st.column_config.NumberColumn("Row", disabled=True),
                "Timestamp": st.column_config.DatetimeColumn("Timestamp", disabled=True),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=['', 'Accept', 'Reject'],
                    required=True
                )
            },
            hide_index=True,
            key="status_editor"
        )
        
        # Check for changes and update session state
        for index, row in edited_df.iterrows():
            if row['Status'] != status_df.loc[index, 'Status']:
                st.session_state.status_updates[index] = row['Status']
        
        # Save button
        if st.session_state.status_updates and st.button("Save Status Changes", key="save_status_changes"):
            for index, new_status in st.session_state.status_updates.items():
                try:
                    if update_sheet_cell(service, spreadsheet_id, sheet_name, index + 2, 'Status', new_status):
                        st.success(f"Updated status for row {index + 2} to {new_status}")
                    else:
                        st.error(f"Failed to update status for row {index + 2}")
                except Exception as e:
                    st.error(f"Error updating row {index + 2}: {str(e)}")
            
            # Clear status updates after saving
            st.session_state.status_updates.clear()
            st.rerun()  # Refresh the page to show updated data
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check your Sheet ID and Sheet Name in the secrets configuration.")
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        show_login_page()
    else:
        service = get_google_sheets_service()
        spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        sheet_name = st.secrets["google_sheets"]["worksheet_name"]
        show_main_page(service, spreadsheet_id, sheet_name)

if __name__ == "__main__":
    main()
