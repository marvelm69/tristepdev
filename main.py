import streamlit as st

def main():
    st.set_page_config(page_title="Login", page_icon="🔒", layout="centered")

    st.title("Login")

    # Create input fields
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Create login button with gradient
    login_button = st.button(
        "LOGIN",
        type="primary",
        use_container_width=True,
    )

    # Check login credentials when button is pressed
    if login_button:
        # Here you would typically check against a database
        # For this example, we'll use a simple condition
        if email == "admin@example.com" and password == "password":
            st.success("Login successful!")
        else:
            st.error("Invalid email or password")

    # Add some space and a footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("Only accessible by authorized personnel", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
