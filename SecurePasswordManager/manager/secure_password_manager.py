"""
secure_password_manager.py

This module provides the core functionality for the SecurePasswordManager application.
It handles user authentication, encrypted storage of credentials, and full CRUD 
(Create, Read, Update, Delete) operations for managing passwords associated with various websites or applications.

Key Features:
- Secure signup and login with strong password and email validation
- Encrypted storage and retrieval of user credentials using Base64 encoding
- Password recovery through ZIP file encryption
- Activity logging for traceability
- Full account management including user deletion

Dependencies:
- Python standard libraries: os, json, re, datetime, getpass
- Internal modules: encryption (for data encoding/decoding)

Author: Sachin
Created: May 2025
"""

import os
import json
import re
from getpass import getpass
from datetime import datetime
from manager.encryption import encrypt_data, decrypt_data



DATA_DIR = "data"
MASTER_LOGIN_FILE = os.path.join(DATA_DIR, "master_login.json")
APP_PASSWORD_FILE = os.path.join(DATA_DIR, "app_password.json")
LOG_FILE = os.path.join(DATA_DIR, "log.txt")

class SecurePasswordManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)


        for file in [MASTER_LOGIN_FILE, APP_PASSWORD_FILE, LOG_FILE]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    if file.endswith('.json'):
                        json.dump({}, f)
        self.current_user = None

    def search_entry(self):
        data = self.load_user_data()
        site = input("Enter website name to search: ").lower()
        found = False
        for stored_site, encrypted_info in data.items():
            if site in stored_site.lower():
                info = decrypt_data(encrypted_info)
                print(f"Site: {stored_site} | Username: {info['username']} | Password: {info['password']}")
                found = True
        if not found:
            print("No matching entries found.")


    def log_activity(self, message):
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"{datetime.now()} - {message}\n")

    def is_strong_password(self, password):
        return bool(re.fullmatch(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}', password))

    def is_valid_email(self, email):
        return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+", email))

    def signup(self):
        with open(MASTER_LOGIN_FILE, 'r+') as f:
            data = json.load(f)
            username = input("Enter new username: ")
            if username in data:
                print("User already exists.")
                return
            while True:
                password = getpass("Enter password (min 8 chars, upper, lower, digit, special char): ")
                if self.is_strong_password(password):
                    break
                else:
                    print("Weak password. Try again.")
            while True:
                email = input("Enter email: ")
                if self.is_valid_email(email):
                    break
                else:
                    print("Invalid email. Try again.")
            data[username] = encrypt_data({"password": password, "email": email})
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            print("Signup successful.")
            self.log_activity(f"New user signed up: {username}")

    def login(self):
        with open(MASTER_LOGIN_FILE, 'r') as f:
            data = json.load(f)
            username = input("Username: ")
            password = getpass("Password: ")
            if username in data and decrypt_data(data[username])["password"] == password:
                self.current_user = username
                self.log_activity(f"User logged in: {username}")
                return True
            else:
                print("Invalid login.")
                return False

    def forgot_password(self):
        username = input("Enter your username for password recovery: ")
        with open(MASTER_LOGIN_FILE, 'r') as f:
            data = json.load(f)
        if username in data:
            user_data = decrypt_data(data[username])
            password = user_data["password"]
            with open("recovered_password.txt", 'w') as f:
                f.write(f"Your password is: {password}")
            os.system("zip -P admin123 recovered_password.zip recovered_password.txt && rm recovered_password.txt")
            print("Password has been saved in 'recovered_password.zip'. Use password 'admin123' to unzip.")
            self.log_activity(f"Password recovery requested by user: {username}")
        else:
            print("Username not found.")

    def logout(self):
        self.log_activity(f"User logged out: {self.current_user}")
        self.current_user = None
        print("Logged out.")

    def load_user_data(self):
        with open(APP_PASSWORD_FILE, 'r') as f:
            data = json.load(f)
        return data.get(self.current_user, {})

    def save_user_data(self, user_data):
        with open(APP_PASSWORD_FILE, 'r+') as f:
            data = json.load(f)
            data[self.current_user] = user_data
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def add_entry(self):
        data = self.load_user_data()
        site = input("Website: ")
        username = input("Username: ")
        password = getpass("Password: ")
        data[site] = encrypt_data({"username": username, "password": password})
        self.save_user_data(data)
        self.log_activity(f"Password added for site: {site} by {self.current_user}")

    def update_entry(self):
        data = self.load_user_data()
        site = input("Enter website to update: ")
        if site not in data:
            print("Site not found.")
            return
        username = input("New username: ")
        password = getpass("New password: ")
        data[site] = encrypt_data({"username": username, "password": password})
        self.save_user_data(data)
        self.log_activity(f"Password updated for site: {site} by {self.current_user}")

    def delete_entry(self):
        data = self.load_user_data()
        site = input("Enter site to delete: ")
        if site in data:
            del data[site]
            self.save_user_data(data)
            self.log_activity(f"Password deleted for site: {site} by {self.current_user}")

    def show_all_entries(self):
        data = self.load_user_data()
        for site in data:
            info = decrypt_data(data[site])
            print(f"Site: {site} | Username: {info['username']} | Password: {info['password']}")

    def delete_user(self):
        with open(MASTER_LOGIN_FILE, 'r+') as f:
            master_data = json.load(f)
        with open(APP_PASSWORD_FILE, 'r+') as f:
            app_data = json.load(f)
        master_data.pop(self.current_user, None)
        app_data.pop(self.current_user, None)
        with open(MASTER_LOGIN_FILE, 'w') as f:
            json.dump(master_data, f, indent=4)
        with open(APP_PASSWORD_FILE, 'w') as f:
            json.dump(app_data, f, indent=4)
        self.log_activity(f"Deleted all data for user: {self.current_user}")
        self.current_user = None
        print("Your data has been deleted.")