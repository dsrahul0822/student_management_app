import streamlit as st

# ------------------ HARD-CODED USER CREDENTIALS ------------------
# You can later replace this with a Google Sheet or database
users = {
    "admin": "admin123",
    "rahul": "rahul123",
    "mentor": "mentor2025"
}

# ------------------ SETUP ------------------
st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login to Student Management System")

# ------------------ SESSION STATE SETUP ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# ------------------ LOGIN LOGIC ------------------
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")

    if login:
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")
else:
    st.success(f"✅ You are logged in as `{st.session_state.username}`.")
    st.info("Use the sidebar to access Registration or Search pages.")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
