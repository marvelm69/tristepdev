import streamlit as st

def main():
    st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")

    st.title("Login")

    # Create input fields
    email = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Create login button
    login_button = st.button(
        "LOGIN",
        type="primary",
        use_container_width=True,
    )

    # Check login credentials when button is pressed
    if login_button:
        # Check if the username is 'admin' and the password is 'tr1st3p'
        if email == "admin" and password == "tr1st3p":
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

    # Add some space and a footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("Only accessible by authorized personnel", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
