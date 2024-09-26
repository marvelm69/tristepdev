import streamlit as st

def main():
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
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="centered-text">Welcome</h1>', unsafe_allow_html=True)
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    st.button("LOGIN", type="primary", use_container_width=True)
    
    st.markdown('<div class="centered-text" style="margin-top: 20px;">Don\'t have an account? <a href="#">Sign Up</a></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
