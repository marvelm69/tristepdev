import streamlit as st

def main():
    st.set_page_config(page_title="Welcome", page_icon="A", layout="centered")
    
    # Custom CSS untuk membuat box dan memperbaiki styling
    st.markdown("""
    <style>
    .login-box {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        max-width: 350px;
        margin: auto;
    }
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
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="centered-text">Welcome</h1>', unsafe_allow_html=True)
        st.markdown('<div class="centered-text" style="font-size: 24px; font-weight: bold; margin-bottom: 20px;">A</div>', unsafe_allow_html=True)
        
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        st.button("LOGIN", type="primary", use_container_width=True)
        
        st.markdown('<div class="centered-text" style="margin-top: 20px;">Don\'t have an account? <a href="#">Sign Up</a></div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
