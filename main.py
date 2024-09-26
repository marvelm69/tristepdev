import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

def get_sheet_data_with_api_key(sheet_id, api_key, sheet_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{sheet_name}?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'values' in data and len(data['values']) > 1:
            headers = data['values'][0]
            rows = data['values'][1:]
            
            max_cols = max(len(headers), max(len(row) for row in rows))
            headers = headers + [''] * (max_cols - len(headers))
            rows = [row + [''] * (max_cols - len(row)) for row in rows]
            
            df = pd.DataFrame(rows, columns=headers)
            return df
        else:
            raise Exception("No data found in the sheet or sheet is empty")
    else:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

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

def show_main_page(sheet_id, api_key, sheet_name):
    col1, col2, col3 = st.columns([3,1,1])
    with col3:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()
    
    st.header("Data from Google Sheets")
    try:
        df = get_sheet_data_with_api_key(sheet_id, api_key, sheet_name)
        
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
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please check your Sheet ID, API Key, and Sheet Name.")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        show_login_page()
    else:
        st.set_page_config(layout="wide")
        st.title("Google Sheets Viewer")
        sheet_id = "1UmrtR6lqcLxClwrn99qlugMplGiY62TrWiEbzXiy1Bo"
        api_key = "AIzaSyAz63oyhk1_rNgXiROi2ghHX4tBoPvkDOQ"
        sheet_name = "Form Responses 1"
        show_main_page(sheet_id, api_key, sheet_name)


if __name__ == "__main__":
    main()
