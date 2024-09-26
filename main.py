import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import hashlib

# Fungsi untuk mengambil data dari Google Sheets menggunakan API Key
def get_sheet_data_with_api_key(sheet_id, api_key, sheet_name):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{sheet_name}?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'values' in data and len(data['values']) > 1:
            headers = data['values'][0]  # Mengambil header dari Google Sheets
            rows = data['values'][1:]    # Mengambil data di bawah header
            df = pd.DataFrame(rows, columns=headers)
            return df
        else:
            raise Exception("No data found in the sheet or sheet is empty")
    else:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

# Fungsi untuk menampilkan halaman login
def show_login_page():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Fungsi untuk memeriksa kredensial (contoh sederhana, ganti dengan sistem autentikasi yang lebih aman)
def check_credentials(username, password):
    # Contoh: username = "admin", password = "password123"
    correct_username = "admin"
    correct_password = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # SHA-256 hash of "password123"
    return username == correct_username and hashlib.sha256(password.encode()).hexdigest() == correct_password

# Fungsi untuk menampilkan halaman pertama
def show_page_one(sheet_id, api_key, sheet_name):
    st.header("Data from Google Sheets")
    try:
        # Mendapatkan data dari Google Sheets
        df = get_sheet_data_with_api_key(sheet_id, api_key, sheet_name)
        
        # Menampilkan data di Streamlit
        st.dataframe(df)
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please check your Sheet ID, API Key, and Sheet Name.")

# Fungsi untuk menampilkan halaman kedua
def show_page_two(sheet_id):
    st.header("Embedded Google Sheets")
    # URL untuk embedding Google Sheets
    embed_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/pubhtml?widget=true&headers=false"
    
    # Menggunakan components.iframe untuk menampilkan Google Sheets
    components.iframe(embed_url, width=800, height=600)

# Main function untuk Streamlit app
def main():
    st.title("Google Sheets Viewer")
    
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Jika belum login, tampilkan halaman login
    if not st.session_state['logged_in']:
        show_login_page()
    else:
        # Input untuk Sheet ID dan API Key
        sheet_id = st.sidebar.text_input("Sheet ID", "1UmrtR6lqcLxClwrn99qlugMplGiY62TrWiEbzXiy1Bo")
        api_key = st.sidebar.text_input("API Key", "AIzaSyAz63oyhk1_rNgXiROi2ghHX4tBoPvkDOQ")
        sheet_name = "Form Responses 1"  # Set nama sheet yang benar
        
        # Membuat sidebar untuk navigasi
        page = st.sidebar.radio("Navigate", ["Data View", "Embedded Sheet"])
        
        if page == "Data View":
            show_page_one(sheet_id, api_key, sheet_name)
        elif page == "Embedded Sheet":
            show_page_two(sheet_id)

        # Tombol logout
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.experimental_rerun()

# Menjalankan aplikasi Streamlit
if __name__ == "__main__":
    main()
