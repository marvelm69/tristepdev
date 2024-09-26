import streamlit as st

def main():
    st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")
    
    # Custom CSS to create a box and improve styling
    st.markdown("""
    <style>
    .login-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Login")
    
    # Create a container for the login box
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        # Create input fields
        email = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Create login button
        login_button = st.button(
            "LOGIN",
            type="primary",
            use_container_width=True,
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Check login credentials when button is pressed
    if login_button:
        if email and password:  # Check if both fields are filled
            # Check if the username is 'admin' and the password is 'tr1st3p'
            if email == "admin" and password == "tr1st3p":
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter both username and password")

    # Add some space and a footer
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center; color: #888;'>"
        "Only accessible by authorized personnel"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
