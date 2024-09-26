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
    st.header("Login")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        if st.button("Login"):
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
        st.dataframe(df)
        
        empty_cols = df.columns[df.isna().all()].tolist()
        if empty_cols:
            st.warning(f"Kolom berikut kosong atau tidak memiliki data: {', '.join(empty_cols)}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please check your Sheet ID, API Key, and Sheet Name.")

def main():
    st.set_page_config(layout="wide")
    st.title("Google Sheets Viewer")
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        show_login_page()
    else:
        sheet_id = "1UmrtR6lqcLxClwrn99qlugMplGiY62TrWiEbzXiy1Bo"
        api_key = "AIzaSyAz63oyhk1_rNgXiROi2ghHX4tBoPvkDOQ"
        sheet_name = "Form Responses 1"
        show_main_page(sheet_id, api_key, sheet_name)

if __name__ == "__main__":
    main()
