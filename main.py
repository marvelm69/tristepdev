import pandas as pd
import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page configuration
st.set_page_config(layout="wide")

# Helper functions
def get_google_sheets_service():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=creds)
    return service

def send_email(recipient_email, full_name, title, status, entity_type):
    sender_email = "tristepcompany@gmail.com"
    sender_password = "yuvc rpls jtwy btle"  # Use Gmail App Password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = f'Verification Result of {entity_type} "{title}" for TriStep Platform'

    if status == 'Accept':
        body = f'''
Dear {full_name},

Congratulations! We are pleased to inform you that your {entity_type}, "{title}", has been approved for the TRISTEP platform. Your contribution aligns well with our content standards, and we believe it will be a valuable addition to our offerings.

Thank you for your contribution to our learning community. We look forward to seeing it engage and educate our users.

Best regards,
TRISTEP Admin
        '''
    else:  # Reject
        body = f'''
Dear {full_name},

Thank you for submitting your {entity_type}, "{title}", for consideration on the TRISTEP platform. After a thorough review, we regret to inform you that it does not fully align with our current content standards, and we cannot proceed with its approval at this time.

We highly value the effort you've put in and encourage you to make the necessary adjustments. Should you choose to revise and resubmit, please ensure it aligns with our platform's standards.

Thank you for your understanding.

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

def append_to_online_courses(service, source_spreadsheet_id, destination_spreadsheet_id, source_sheet_name, destination_sheet_name, row_data):
    source_range = f"'{source_sheet_name}'!D:Q"
    result = service.spreadsheets().values().get(spreadsheetId=source_spreadsheet_id, range=source_range).execute()
    values = result.get('values', [])
    
    if not values:
        raise Exception('No data found in source sheet.')
    
    source_data = values[row_data - 1]  # -1 because sheet rows are 1-indexed
    
    # Ensure we have exactly 14 columns (D to Q)
    if len(source_data) < 14:
        source_data.extend([''] * (14 - len(source_data)))
    elif len(source_data) > 14:
        source_data = source_data[:14]
    
    # Add an empty string at the beginning to shift data to start from column B
    destination_data = [''] + source_data
    
    destination_range = f"'{destination_sheet_name}'!A:O"
    body = {
        'values': [destination_data]
    }
    
    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=destination_spreadsheet_id,
            range=destination_range,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return result
    except Exception as e:
        st.error(f"Error appending course data: {str(e)}")
        return None

def append_to_online_jobs(service, source_spreadsheet_id, destination_spreadsheet_id, source_sheet_name, destination_sheet_name, row_data):
    source_range = f"'{source_sheet_name}'!D:T"
    result = service.spreadsheets().values().get(spreadsheetId=source_spreadsheet_id, range=source_range).execute()
    values = result.get('values', [])
    
    if not values:
        raise Exception('No data found in source sheet.')
    
    source_data = values[row_data - 1]  # -1 because sheet rows are 1-indexed
    
    # Ensure we have exactly 17 columns (D to T)
    if len(source_data) < 17:
        source_data.extend([''] * (17 - len(source_data)))
    elif len(source_data) > 17:
        source_data = source_data[:17]
    
    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=destination_spreadsheet_id,
            range=f"{destination_sheet_name}!A:Q",  # Specify the range A:Q in the destination sheet
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [source_data]}
        ).execute()
        return result
    except Exception as e:
        st.error(f"Error appending data: {str(e)}")
        return None
        
def get_sheet_data(service, spreadsheet_id, range_name):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=f"'{range_name}'!A:Z").execute()
    values = result.get('values', [])
    
    if not values:
        raise Exception('No data found.')
    
    headers = values[0]
    rows = values[1:]
    max_cols = max(len(headers), max(len(row) for row in rows))
    
    headers = headers + [''] * (max_cols - len(headers))
    rows = [row + [''] * (max_cols - len(row)) for row in rows]
    
    df = pd.DataFrame(rows, columns=headers)
    return df

def update_sheet_cell(service, spreadsheet_id, sheet_name, row, column_name, value, entity_type):
    header_range = f"'{sheet_name}'"
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=header_range).execute()
    values = result.get('values', [])
    
    if not values:
        st.error("No data found in the sheet.")
        return False
    
    headers = values[0]
    
    try:
        column_index = headers.index(column_name)
    except ValueError:
        st.error(f"Column '{column_name}' not found in the sheet headers.")
        return False
    
    column_letter = chr(65 + column_index)  # A is 65 in ASCII
    range_name = f"'{sheet_name}'!{column_letter}{row}"
    
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

        if column_name == 'Status' and (value == 'Accept' or value == 'Reject'):
            row_data = values[row - 1] if row <= len(values) else []

            gmail_index = headers.index('Gmail') if 'Gmail' in headers else -1
            full_name_index = headers.index('Full Name') if 'Full Name' in headers else -1
            title_index = headers.index('Title') if 'Title' in headers else -1

            recipient_email = row_data[gmail_index] if gmail_index != -1 and gmail_index < len(row_data) else ''
            full_name = row_data[full_name_index] if full_name_index != -1 and full_name_index < len(row_data) else ''
            title = row_data[title_index] if title_index != -1 and title_index < len(row_data) else ''

            if recipient_email and full_name and title:
                if send_email(recipient_email, full_name, title, value, entity_type):
                    st.success(f"Email sent to {recipient_email}")
                else:
                    st.error(f"Failed to send email to {recipient_email}")
            else:
                st.warning(f"Unable to send email due to missing information. Email: {recipient_email}, Name: {full_name}, Title: {title}")

        # Append to the destination sheet if the status is "Accept"
        if value == 'Accept':
            if entity_type == "job":
                destination_spreadsheet_id = st.secrets["google_sheets_job"]["online_jobs_spreadsheet_id"]
                append_result = append_to_online_jobs(service, spreadsheet_id, destination_spreadsheet_id, "Form Responses 1", "Sheet1", row)
                if append_result:
                    st.success(f"Data from row {row} has been added to the Online_Jobs sheet.")
                else:
                    st.error(f"Failed to add data from row {row} to the Online_Jobs sheet.")
            elif entity_type == "course":
                destination_spreadsheet_id = st.secrets["google_sheets"]["online_courses_spreadsheet_id"]
                append_result = append_to_online_courses(service, spreadsheet_id, destination_spreadsheet_id, "Form Responses 1", "Online_Courses", row)
                if append_result:
                    st.success(f"Data from row {row} has been added to the Online_Courses sheet.")
                else:
                    st.error(f"Failed to add data from row {row} to the Online_Courses sheet.")

        return True
    except Exception as e:
        st.error(f"Error updating cell: {str(e)}")
        return False
        
def show_course_page(service, spreadsheet_id, sheet_name, online_courses_spreadsheet_id):
    st.header("Manage Courses")
    show_management_page(service, spreadsheet_id, "Form Responses 1", "course", online_courses_spreadsheet_id)

def show_job_page(service, spreadsheet_id, sheet_name, online_jobs_spreadsheet_id):
    st.header("Manage Jobs")
    show_management_page(service, spreadsheet_id, "Form Responses 1", "job", online_jobs_spreadsheet_id)

def show_management_page(service, spreadsheet_id, sheet_name, entity_type, destination_spreadsheet_id):
    if 'status_updates' not in st.session_state:
        st.session_state.status_updates = {}

    col1, col2, col3 = st.columns([3,1,1])
    with col3:
        if st.button("Logout", key="logout_button"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    st.header(f"Data from Google Sheets ({entity_type.capitalize()})")
    try:
        df = get_sheet_data(service, spreadsheet_id, sheet_name)
        
        if 'Timestamp' not in df.columns:
            st.error("The 'Timestamp' column is missing from the sheet data.")
            return
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        if df['Timestamp'].isnull().all():
            st.error("Unable to parse any dates from the 'Timestamp' column.")
            return
        
        df = df.dropna(subset=['Timestamp'])
        
        if df.empty:
            st.warning("No valid data remaining.")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            years = sorted(df['Timestamp'].dt.year.unique(), reverse=True)
            if not years:
                st.error("No valid years found.")
                return
            selected_year = st.selectbox("Select Year", years)
        
        with col2:
            months = [
                "January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"
            ]
            selected_month = st.selectbox("Select Month", months)
        
        filtered_df = df[
            (df['Timestamp'].dt.year == selected_year) & 
            (df['Timestamp'].dt.month == months.index(selected_month) + 1)
        ]
        
        if filtered_df.empty:
            st.warning(f"No data available for {selected_month} {selected_year}")
            return
        
        st.subheader(f"All Entries ({entity_type.capitalize()})")
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
            key=f"data_editor_{entity_type}"
        )
        
        status_changed = False
        for index, row in edited_df.iterrows():
            if row['Status'] != filtered_df.loc[index, 'Status']:
                status_changed = True
                st.session_state.status_updates[index + 2] = row['Status']
        
        empty_cols = filtered_df.columns[filtered_df.isna().all()].tolist()
        if empty_cols:
            st.warning(f"The following columns are empty: {', '.join(empty_cols)}")
        
        st.info(f"Showing {len(filtered_df)} rows for {selected_month} {selected_year}")
        
        if st.button(f"Save {entity_type.capitalize()} Status Changes", key=f"save_status_changes_{entity_type}", disabled=not status_changed):
            if st.session_state.status_updates:
                for row, new_status in st.session_state.status_updates.items():
                    try:
                        if update_sheet_cell(service, spreadsheet_id, "Form Responses 1", row, 'Status', new_status, entity_type):
                            st.success(f"Updated status for row {row} to {new_status}")
                        else:
                            st.error(f"Failed to update status for row {row}")
                    except Exception as e:
                        st.error(f"Error updating row {row}: {str(e)}")
                
                st.session_state.status_updates.clear()
                st.rerun()
            else:
                st.info("No changes to save.")
        
        st.subheader(f"Accepted Entries ({entity_type.capitalize()})")
        accepted_df = filtered_df[filtered_df['Status'] == 'Accept']
        if accepted_df.empty:
            st.info(f"No accepted entries for {selected_month} {selected_year}")
        else:
            st.dataframe(accepted_df, hide_index=True)
            st.info(f"Showing {len(accepted_df)} accepted entries")
        
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
        course_spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        job_spreadsheet_id = st.secrets["google_sheets_job"]["spreadsheet_id"]
        online_jobs_spreadsheet_id = st.secrets["google_sheets_job"]["online_jobs_spreadsheet_id"]
        online_jobs_spreadsheet_id = "1huKbxP4W5c5sBWAQ5LzerhdId6TR9glCRFKn7DNOKEE"
        
        page = st.sidebar.selectbox("Select Page", ["Manage Courses", "Manage Jobs"])
        
        if page == "Manage Courses":
            show_course_page(service, course_spreadsheet_id, "Form Responses 1", "1PM_ifqhHQbvVau26xH2rU7xEw8ib1t2D6s_eDRPzJVI")
        elif page == "Manage Jobs":
            show_job_page(service, job_spreadsheet_id, "Sheet1", online_jobs_spreadsheet_id)

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

if __name__ == "__main__":
    main()
