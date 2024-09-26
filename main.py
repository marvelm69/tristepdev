import requests
import pandas as pd
import streamlit as st

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

# Main function untuk Streamlit app
def main():
    st.title("Google Sheets Data with API Key")
    
    # Sheet ID dari link Google Sheets Anda
    sheet_id = "1UmrtR6lqcLxClwrn99qlugMplGiY62TrWiEbzXiy1Bo"
    
    # API Key Anda
    api_key = "AIzaSyAz63oyhk1_rNgXiROi2ghHX4tBoPvkDOQ"
    
    try:
        # Mendapatkan data dari Google Sheets
        df = get_sheet_data_with_api_key(sheet_id, api_key)
        
        # Menampilkan data di Streamlit
        st.write("Data from Google Sheets:")
        st.dataframe(df)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Menjalankan aplikasi Streamlit
if __name__ == "__main__":
    main()
