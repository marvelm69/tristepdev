import pandas as pd
import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page configuration at the very beginning
st.set_page_config(layout="wide")

def get_google_sheets_service():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    return service

def send_email(recipient_email, full_name, title, status, is_course=True):
    sender_email = "tristepcompany@gmail.com"
    sender_password = "yuvc rpls jtwy btle"  # Use Gmail App Password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = f'Verification Result of {"Online Course" if is_course else "Job Posting"} "{title}" for TriStep Platform'

    if status == 'Accept':
        body = f'''
Dear {full_name},

Congratulations! We are pleased to inform you that your {"online course" if is_course else "job posting"}, "{title}", has been approved for the TRISTEP platform. Your {"course" if is_course else "job posting"} aligns well with our content standards, and we believe it will be a valuable addition to our offerings.

Thank you for your contribution to our {"learning" if is_course else "job"} community. We look forward to seeing your {"course engage and educate our users" if is_course else "job posting attract qualified candidates"}.

Best regards,
TRISTEP Admin
        '''
    else:  # Reject
        body = f'''
Dear {full_name},

Thank you for submitting your {"online course" if is_course else "job posting"}, "{title}", for consideration on the TRISTEP platform. After a thorough review by our team, we regret to inform you that your {"course" if is_course else "job posting"} does not fully align with our current content standards, and therefore we cannot proceed with its approval at this time.

We highly value the effort you've put into creating this {"course" if is_course else "job posting"} and encourage you to make the necessary adjustments. Should you choose to revise and resubmit, please ensure your content aligns with our platform's standards.

Thank you for your understanding and continued interest in contributing to TRISTEP.

Best regards,
TRISTEP Admin
        '''

    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

def append_to_destination_sheet(service, source_spreadsheet_id, destination_spreadsheet_id, source_sheet_name, destination_sheet_name, row_data):
    # Get data from source sheet
    source_range = f"'{source_sheet_name}'!A:Z"  # Adjust range as needed
    result = service.spreadsheets().values().get(spreadsheetId=source_spreadsheet_id, range=source_range).execute()
    values = result.get('values', [])
    
    if not values:
        raise Exception('No data found in source sheet.')
    
    # Prepare data for destination sheet
    source_data = values[row_data - 1]  # -1 because sheet rows are 1-indexed
    
    # Add an empty string at the beginning to shift data one column to the right
    destination_data = [[''] + source_data]
    
    # Append to destination sheet, starting from column A
    destination_range = f"'{destination_sheet_name}'!A:Z"  # Adjust range as needed
    body = {
        'values': destination_data
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=destination_spreadsheet_id,
        range=destination_range,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    
    return result

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
            valueInputOption='RAW',
            body=body
        ).execute()

        return True
    except Exception as e:
        st.error(f"Error updating cell: {str(e)}")
        return False

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

def show_main_page(service):
    st.title("Admin Dashboard")
    
    # Sidebar for navigation
    page = st.sidebar.radio("Choose a page", ("Courses", "Jobs"))
    
    if page == "Courses":
        show_courses_page(service)
    else:
        show_jobs_page(service)

def show_courses_page(service):
    spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
    sheet_name = st.secrets["google_sheets"]["worksheet_name"]
    online_courses_spreadsheet_id = st.secrets["google_sheets"]["online_courses_spreadsheet_id"]
    online_courses_sheet_name = "Sheet1"  # atau sesuaikan dengan nama sheet yang benar
    
    st.header("Course Management")
    show_data_page(service, spreadsheet_id, sheet_name, online_courses_spreadsheet_id, online_courses_sheet_name, is_course=True)

def show_jobs_page(service):
    job_spreadsheet_id = "1ym1Y-CM3mDp9QVPqIAj-C1WKSJ9eSB22oQT5BMOZ_c4"
    job_sheet_name = "Sheet1"
    approved_jobs_spreadsheet_id = "1AlunlNxwIM664-1SC08Ankuka6zlNmQoQ3BoMoYQFBg"
    approved_jobs_sheet_name = "preprocessed_linkedin"
    
    st.header("Job Management")
    show_data_page(service, job_spreadsheet_id, job_sheet_name, approved_jobs_spreadsheet_id, approved_jobs_sheet_name, is_course=False)

def show_data_page(service, spreadsheet_id, sheet_name, destination_spreadsheet_id, destination_sheet_name, is_course=True):
    if 'status_updates' not in st.session_state:
        st.session_state.status_updates = {}

    col1, col2, col3 = st.columns([3,1,1])
    with col3:
        if st.button("Logout", key="logout_button"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    st.subheader(f"Data from {'Courses' if is_course else 'Jobs'} Google Sheet")
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
        
        st.subheader("All Entries")
        # Use st.data_editor for an editable table
        edited_df = st.data_editor(
            filtered_df,
            column_config={
                "Timestamp": st.column_config.DatetimeColumn("Timestamp", disabled=True),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=['', 'Accept', 'Reject'],
                    required=False
                )
            },
            hide_index=True,
            key="data_editor"
        )
        
        # Check for changes in the Status column
        status_changed = False
        for index, row in edited_df.iterrows():
            if row['Status'] != filtered_df.loc[index, 'Status']:
                status_changed = True
                # Use index + 2 to account for 0-indexing and header row in Google Sheets
                st.session_state.status_updates[index + 2] = row['Status']
        
        # Display information about empty columns
        empty_cols = filtered_df.columns[filtered_df.isna().all()].tolist()
        if empty_cols:
            st.warning(f"The following columns are empty or have no data: {', '.join(empty_cols)}")
        
        # Display row count
        st.info(f"Showing {len(filtered_df)} rows for {selected_month} {selected_year}")
        
        # Save button
        if st.button("Save Status Changes", key="save_status_changes", disabled=not status_changed):
            if st.session_state.status_updates:
                for row, new_status in st.session_state.status_updates.items():
                    try:
                        if update_sheet_cell(service, spreadsheet_id, sheet_name, row, 'Status', new_status):
                            st.success(f"Updated status for row {row} to {new_status}")
                            
                            # Get the necessary data for email and appending
                            row_data = service.spreadsheets().values().get(
                                spreadsheetId=spreadsheet_id,
                                range=f"'{sheet_name}'!{row}:{row}"
                            ).execute().get('values', [[]])[0]
                            
                            # Get the indices of required columns
                            headers = service.spreadsheets().values().get(
                                spreadsheetId=spreadsheet_id,
                                range=f"'{sheet_name}'!1:1"
                            ).execute().get('values', [[]])[0]
                            
                            gmail_index = headers.index('Gmail')
                            full_name_index = headers.index('Full Name')
                            title_index = headers.index('Title')
                            
                            # Extract required data
                            recipient_email = row_data[gmail_index]
                            full_name = row_data[full_name_index]
                            title = row_data[title_index]
                            
                            # Send email
                            if send_email(recipient_email, full_name, title, new_status, is_course):
                                st.success(f"Email sent to {recipient_email}")
                            else:
                                st.error(f"Failed to send email to {recipient_email}")
                            
                            # If status is changed to 'Accept', append data to destination sheet
                            if new_status == 'Accept':
                                append_result = append_to_destination_sheet(service, spreadsheet_id, destination_spreadsheet_id, sheet_name, destination_sheet_name, row)
                                if append_result:
                                    st.success(f"Data from row {row} has been added to the approved {'courses' if is_course else 'jobs'} sheet.")
                                else:
                                    st.error(f"Failed to add data from row {row} to the approved {'courses' if is_course else 'jobs'} sheet.")
                        else:
                            st.error(f"Failed to update status for row {row}")
                    except Exception as e:
                        st.error(f"Error updating row {row}: {str(e)}")
                
                # Clear status updates after saving
                st.session_state.status_updates.clear()
                st.rerun()  # Refresh the page to show updated data
            else:
                st.info("No changes to save.")
        
        # New table for Accepted entries
        st.subheader(f"Accepted {'Courses' if is_course else 'Jobs'}")
        accepted_df = filtered_df[filtered_df['Status'] == 'Accept']
        if accepted_df.empty:
            st.info(f"No accepted {'courses' if is_course else 'jobs'} for the selected period.")
        else:
            st.dataframe(accepted_df, hide_index=True)
            st.info(f"Showing {len(accepted_df)} accepted {'courses' if is_course else 'jobs'} for {selected_month} {selected_year}")
        
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
        show_main_page(service)

if __name__ == "__main__":
    main()
