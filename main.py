import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# Create a connection object.
credentials = service_account.Credentials.from_service_account_file(
    'path/to/your/service_account.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

service = build('sheets', 'v4', credentials=credentials)

def get_sheet_data(sheet_id, sheet_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_name).execute()
    values = result.get('values', [])

    if not values:
        raise Exception('No data found.')

    headers = values[0]
    rows = values[1:]
    df = pd.DataFrame(rows, columns=headers)
    return df

def update_sheet_cell(sheet_id, sheet_name, cell, value):
    sheet = service.spreadsheets()
    range_name = f"{sheet_name}!{cell}"
    body = {
        'values': [[value]]
    }
    result = sheet.values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='USER_ENTERED', body=body).execute()
    return result

def show_login_page():
    st.markdown("<h1 style='text-align: center;'>Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        if st.button("Login", use_container_width=True):
            if check_credentials(username, password):
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Invalid username or password")

def check_credentials(username, password):
    correct_username = "admin"
    correct_password = "tr1st3p"
    return username == correct_username and password == correct_password

def show_main_page(sheet_id, sheet_name):
    col1, col2, col3 = st.columns([3,1,1])
    with col3:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    st.header("Data from Google Sheets")
    try:
        df = get_sheet_data(sheet_id, sheet_name)
        
        # Convert 'Timestamp' column to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Create filters
        col1, col2 = st.columns(2)
        with col1:
            years = sorted(df['Timestamp'].dt.year.unique(), reverse=True)
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
        
        # Display filtered data
        st.dataframe(filtered_df)
        
        # Display information about empty columns
        empty_cols = filtered_df.columns[filtered_df.isna().all()].tolist()
        if empty_cols:
            st.warning(f"The following columns are empty or have no data: {', '.join(empty_cols)}")
        
        # Display row count
        st.info(f"Showing {len(filtered_df)} rows for {selected_month} {selected_year}")
        
        # Separate section for status input
        st.header("Update Status")
        status_updates = {}
        for index, row in filtered_df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Row {index + 2}: {row['Timestamp']}")  # +2 because of 0-indexing and header row
            with col2:
                status_options = ['', 'Accept', 'Reject']
                current_status = row.get('Status', '')
                new_status = st.selectbox(f"Status for row {index + 2}", 
                                          options=status_options, 
                                          index=status_options.index(current_status) if current_status in status_options else 0,
                                          key=f"status_{index}")
                if new_status != current_status:
                    status_updates[index] = new_status
        
        # Save button
        if st.button("Save Status Changes"):
            if status_updates:
                with st.spinner("Updating statuses..."):
                    for index, new_status in status_updates.items():
                        cell = f"{chr(65 + df.columns.get_loc('Status'))}{index + 2}"  # Get correct column letter
                        try:
                            result = update_sheet_cell(sheet_id, sheet_name, cell, new_status)
                            if result:
                                st.success(f"Updated status for row {index + 2} to {new_status}")
                            else:
                                st.error(f"Failed to update status for row {index + 2}. Please check your permissions and try again.")
                        except Exception as e:
                            st.error(f"Error updating row {index + 2}: {str(e)}")
                
                # Clear status updates after saving
                status_updates.clear()
                st.rerun()  # Refresh the page to show updated data
            else:
                st.info("No status changes to save.")
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please check your Sheet ID and Sheet Name.")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        show_login_page()
    else:
        st.set_page_config(layout="wide")
        st.title("Google Sheets Viewer")
        sheet_id = "1UmrtR6lqcLxClwrn99qlugMplGiY62TrWiEbzXiy1Bo"
        sheet_name = "Form Responses 1"
        show_main_page(sheet_id, sheet_name)

if __name__ == "__main__":
    main()
