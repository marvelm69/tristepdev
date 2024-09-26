import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Fungsi untuk mengambil data dari Google Sheets menggunakan API Key
def get_sheet_data_with_api_key(sheet_id, api_key, sheet_name="Sheet1"):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/{sheet_name}?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        headers = data['values'][0]  # Mengambil header dari Google Sheets
        rows = data['values'][1:]    # Mengambil data di bawah header
        df = pd.DataFrame(rows, columns=headers)
        return df
    else:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

# Fungsi untuk menampilkan halaman pertama
def show_page_one(sheet_id, api_key):
    st.header("Data from Google Sheets")
    try:
        # Mendapatkan data dari Google Sheets
        df = get_sheet_data_with_api_key(sheet_id, api_key)
        
        # Menampilkan data di Streamlit
        st.dataframe(df)
    except Exception as e:
        st.error(f"An error occurred: {e}")

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
    
    # Sheet ID dari link Google Sheets Anda
    sheet_id = "1UmrtR6lqcLxClwrn99qlugMplGiY62TrWiEbzXiy1Bo"
    
    # API Key Anda
    api_key = "AIzaSyAz63oyhk1_rNgXiROi2ghHX4tBoPvkDOQ"
    
    # Membuat sidebar untuk navigasi
    page = st.sidebar.radio("Navigate", ["Data View", "Embedded Sheet"])
    
    if page == "Data View":
        show_page_one(sheet_id, api_key)
    elif page == "Embedded Sheet":
        show_page_two(sheet_id)

# Menjalankan aplikasi Streamlit
if __name__ == "__main__":
    main()
