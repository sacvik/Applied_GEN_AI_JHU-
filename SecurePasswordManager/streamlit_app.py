import streamlit as st
import json

from manager.encryption import encrypt_data, decrypt_data
from manager.secure_password_manager import SecurePasswordManager

st.set_page_config(page_title="Secure Password Manager", page_icon="🔐")
st.title("🔐 Secure Password Manager")

manager = SecurePasswordManager()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Signup section
with st.expander("📝 New User? Sign Up"):
    new_username = st.text_input("Username", key="signup_user")
    new_password = st.text_input("Password", type="password", key="signup_pass")
    new_email = st.text_input("Email", key="signup_email")
    if st.button("Sign Up"):
        if not manager.is_strong_password(new_password):
            st.error("Weak password. Must include upper, lower, number, special char and be 8+ characters.")
        elif not manager.is_valid_email(new_email):
            st.error("Invalid email format.")
        else:
            with open(manager.MASTER_LOGIN_FILE, 'r+') as f:
                data = json.load(f)
                if new_username in data:
                    st.warning("Username already exists.")
                else:
                    data[new_username] = encrypt_data({"password": new_password, "email": new_email})
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
                    manager.log_activity(f"Streamlit sign up: {new_username}")
                    st.success("Signup successful. Please log in.")

# Login section
st.subheader("🔐 Login")
login_user = st.text_input("Username")
login_pass = st.text_input("Password", type="password")
if st.button("Login"):
    with open(manager.MASTER_LOGIN_FILE, 'r') as f:
        data = json.load(f)
        if login_user in data:
            stored = decrypt_data(data[login_user])
            if stored["password"] == login_pass:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                manager.current_user = login_user
                manager.log_activity(f"Streamlit login success: {login_user}")
                st.success(f"Welcome, {login_user}!")
            else:
                st.error("Incorrect password.")
                manager.log_activity(f"Streamlit login failed: {login_user} - wrong password")
        else:
            st.error("Username not found.")
            manager.log_activity(f"Streamlit login failed: {login_user} - username not found")

# After login
if st.session_state.logged_in:
    st.subheader("🔐 Manage Your Entries")
    options = ["Add Entry", "Update Entry", "Delete Entry", "Show All", "Delete User", "Logout"]
    choice = st.selectbox("Choose an action", options)

    if choice == "Add Entry":
        site = st.text_input("Website")
        username = st.text_input("Site Username")
        password = st.text_input("Site Password", type="password")
        if st.button("Save Entry"):
            data = manager.load_user_data()
            data[site] = encrypt_data({"username": username, "password": password})
            manager.save_user_data(data)
            manager.log_activity(f"Added password for {site}")
            st.success("Entry saved.")

    elif choice == "Show All":
        data = manager.load_user_data()
        for site, cred in data.items():
            info = decrypt_data(cred)
            st.write(f"**{site}** | Username: {info['username']} | Password: {info['password']}")

    elif choice == "Update Entry":
        data = manager.load_user_data()
        sites = list(data.keys())
        site = st.selectbox("Select site to update", sites)
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        if st.button("Update"):
            data[site] = encrypt_data({"username": username, "password": password})
            manager.save_user_data(data)
            manager.log_activity(f"Updated password for {site}")
            st.success("Entry updated.")

    elif choice == "Delete Entry":
        data = manager.load_user_data()
        site = st.selectbox("Select site to delete", list(data.keys()))
        if st.button("Delete"):
            del data[site]
            manager.save_user_data(data)
            manager.log_activity(f"Deleted entry for {site}")
            st.success("Entry deleted.")

    elif choice == "Delete User":
        if st.button("Confirm Delete User"):
            manager.delete_user()
            st.session_state.logged_in = False
            st.success("User deleted.")

    elif choice == "Logout":
        manager.logout()
        st.session_state.logged_in = False
        st.success("Logged out.")
