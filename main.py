import streamlit as st
from streamlit.runtime.scriptrunner import RerunException

def main_page():
    st.set_page_config(page_title="Welcome", layout="centered")
    
    # Custom CSS untuk styling
    st.markdown("""
    <style>
    .stButton>button {
        background: linear-gradient(to right, #00C0FF, #4E5FFF);
        color: white;
        font-weight: bold;
        padding: 10px 0;
        border: none;
        border-radius: 25px;
        cursor: pointer;
    }
    .centered-text {
        text-align: center;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .input-container {
        max-width: 300px;
        margin: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="centered-text">Welcome</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("LOGIN", type="primary", use_container_width=True):
            if username == "admin" and password == "tr1st3p":
                st.success("Login successful!")
                st.session_state.logged_in = True
                raise RerunException()
            else:
                st.error("Invalid username or password")
    
    st.markdown('<div class="centered-text" style="margin-top: 20px;">Don\'t have an account? <a href="#">Sign Up</a></div>', unsafe_allow_html=True)

def second_page():
    st.title("Welcome to the Second Page")
    st.write("This page is currently empty.")
    if st.button("Logout"):
        st.session_state.logged_in = False
        raise RerunException()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        second_page()
    else:
        main_page()

if __name__ == "__main__":
    try:
        main()
    except RerunException:
        st.rerun()
