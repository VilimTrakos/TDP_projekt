import tkinter as tk
from tkinter import messagebox
from utils import launch_script
import sys
import requests
import couchdb

def check_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    selected_region = region_var.get()

    if not username or not password:
        messagebox.showerror("Login Error", "Please enter both username and password.")
        return

    try:
        # Authenticate using CouchDB's _session API
        auth_url = f"{COUCHDB_SERVER_URL}/_session"
        payload = {'name': username, 'password': password}
        response = requests.post(auth_url, data=payload)

        if response.status_code == 200 and response.json().get('ok'):
            # Successful authentication
            user_doc_id = f"org.couchdb.user:{username}"
            user_doc = users_db.get(user_doc_id)

            if not user_doc:
                messagebox.showerror("Login Error", "User document not found.")
                return

            role = user_doc.get("roles")[0] if user_doc.get("roles") else "undefined"

            # Fetch related entity (doctor or medical_staff) from medical_records
            related_id = None
            for doc_id in db:
                doc = db[doc_id]
                if doc.get("user_id") == user_doc_id:
                    related_id = doc_id
                    break

            if not related_id:
                messagebox.showerror("Login Error", "Related user entity not found.")
                return

            login_window.destroy()
            launch_script("app.py", username, role, related_id, selected_region)
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")
            password_entry.delete(0, tk.END)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to connect to CouchDB: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# CouchDB Connection Details
COUCHDB_USER = 'admin'        # Replace with your CouchDB admin username
COUCHDB_PASSWORD = 'admin'    # Replace with your CouchDB admin password
COUCHDB_SERVER_URL = f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@localhost:5984"

# Connect to CouchDB
try:
    couch = couchdb.Server(COUCHDB_SERVER_URL)
    db_name = 'medical_records'
    users_db_name = '_users'

    if db_name in couch:
        db = couch[db_name]
    else:
        messagebox.showerror("Error", f"Database '{db_name}' does not exist.")
        sys.exit(1)

    if users_db_name in couch:
        users_db = couch[users_db_name]
    else:
        messagebox.showerror("Error", f"Database '{users_db_name}' does not exist.")
        sys.exit(1)
except Exception as e:
    messagebox.showerror("Error", f"Failed to connect to CouchDB: {e}")
    sys.exit(1)

# Initialize Tkinter window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x250")

# Username Label and Entry
tk.Label(login_window, text="Username:").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

# Password Label and Entry
tk.Label(login_window, text="Password:").pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

# Region Selection
tk.Label(login_window, text="Select region:").pack(pady=5)
region_var = tk.StringVar(login_window)
region_var.set("Zagreb")  # Default value
regions = ["Zagreb", "Osijek", "Varazdin", "Split"]
region_menu = tk.OptionMenu(login_window, region_var, *regions)
region_menu.pack(pady=5)

# Login Button
tk.Button(login_window, text="Login", command=check_login).pack(pady=10)

login_window.mainloop()
