from manager.secure_password_manager import SecurePasswordManager

def main():
    manager = SecurePasswordManager()
    print("==============================")
    print(" Welcome to Secure Password Manager ")
    print("==============================")
    while True:
        print("\nMain Menu:")
        print("1. Login\n2. Signup\n3. Forgot Password\n4. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            if manager.login():
                while True:
                    print("\n1. Add Entry\n2. Update Entry\n3. Delete Entry\n4. Show All\n5. Delete User\n6. Logout\n7. Search Entry")
                    opt = input("Choose: ")
                    if opt == '1':
                        manager.add_entry()
                    elif opt == '2':
                        manager.update_entry()
                    elif opt == '3':
                        manager.delete_entry()
                    elif opt == '4':
                        manager.show_all_entries()
                    elif opt == '5':
                        manager.delete_user()
                        break
                    elif opt == '6':
                        manager.logout()
                        break
                    elif opt == '7':
                        manager.search_entry()
                    
        elif choice == '2':
            manager.signup()
        elif choice == '3':
            manager.forgot_password()
        elif choice == '4':
            print("Exiting application. Goodbye!")
            break

if __name__ == "__main__":
    main()