import tkinter as tk
from tkinter import ttk, messagebox
import couchdb
import re

COUCHDB_USER = 'admin'
COUCHDB_PASSWORD = 'password'

REGION_COUCHDB_MAPPING = {
    "Zagreb": "5986",
    "Osijek": "5985",
    "Varazdin": "5984",
}

def fetch_patients():
    try:
        return [doc_id for doc_id in db if db[doc_id].get("type") == "patient"]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch patients: {e}")
        return []

def display_patients():
    for row in patients_table.get_children():
        patients_table.delete(row)
    patients = fetch_patients()
    for patient in patients:
        patients_table.insert("", tk.END, values=(patient,))

def connect_to_region():
    selected_region = region_var.get()
    couchdb_port = REGION_COUCHDB_MAPPING.get(selected_region)
    if not couchdb_port:
        messagebox.showerror("Error", f"No CouchDB configuration found for region '{selected_region}'.")
        return
    try:
        global db, users_db
        couchdb_server_url = f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@localhost:{couchdb_port}"
        couch = couchdb.Server(couchdb_server_url)
        db_name = 'medical_records'
        users_db_name = '_users'
        if db_name in couch:
            db = couch[db_name]
        else:
            messagebox.showerror("Error", f"Database '{db_name}' does not exist in region '{selected_region}'.")
            db = None
            return
        if users_db_name in couch:
            users_db = couch[users_db_name]
        else:
            messagebox.showerror("Error", f"Database '{users_db_name}' does not exist in region '{selected_region}'.")
            users_db = None
            return
        display_patients()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to CouchDB: {e}")
        db = None
        users_db = None

def generate_entity_id(role):
    try:
        entity_prefix = f"{role}_"
        entity_ids = [doc_id for doc_id in db if doc_id.startswith(entity_prefix)]
        if not entity_ids:
            return f"{entity_prefix}001"
        numbers = [
            int(re.findall(rf'{role}_(\d+)', eid)[0])
            for eid in entity_ids
            if re.findall(rf'{role}_(\d+)', eid)
        ]
        return f"{entity_prefix}{max(numbers) + 1:03d}"
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate entity ID: {e}")
        return None

def is_username_unique(username):
    try:
        user_doc_id = f"org.couchdb.user:{username}"
        return user_doc_id not in users_db
    except Exception as e:
        messagebox.showerror("Error", f"Failed to verify username uniqueness: {e}")
        return False

def add_user():
    if db is None or users_db is None:
        messagebox.showerror("Error", "No valid database connection. Please select a valid region.")
        return
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    role = role_combo.get().strip()
    selected_patients = patients_table.selection()
    patient_ids = [patients_table.item(item, "values")[0] for item in selected_patients]
    if not all([username, password]):
        messagebox.showwarning("Input Error", "Please fill in all required fields (Username and Password).")
        return
    if not is_username_unique(username):
        messagebox.showerror("Error", "Username already exists. Please choose a different username.")
        return
    try:
        user_doc_id = f"org.couchdb.user:{username}"
        user_doc = {
            "_id": user_doc_id,
            "name": username,
            "type": "user",
            "roles": [role],
            "password": password
        }
        users_db.save(user_doc)
        entity_id = generate_entity_id(role)
        if not entity_id:
            users_db.delete(user_doc)
            return
        entity_doc = {
            "_id": entity_id,
            "type": role,
            "patients": patient_ids,
            "user_id": user_doc_id
        }
        db.save(entity_doc)
        messagebox.showinfo("Success", f"User '{username}' added successfully with ID '{entity_id}' in region '{region_var.get()}'.")
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        role_combo.current(0)
        patients_table.selection_remove(*patients_table.selection())
    except couchdb.http.ResourceConflict:
        messagebox.showerror("Error", f"Entity ID '{entity_id}' already exists.")
    except couchdb.http.ResourceNotFound:
        messagebox.showerror("Error", "Database 'medical_records' or '_users' not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

root = tk.Tk()
root.title("Add New User")

tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Password:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Role:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
role_combo = ttk.Combobox(root, values=["doctor", "medical_staff"], state="readonly")
role_combo.grid(row=2, column=1, padx=10, pady=5)
role_combo.current(0)

tk.Label(root, text="Select Region:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
region_var = tk.StringVar(root)
region_var.set("Zagreb")
regions = ["Zagreb", "Osijek", "Varazdin"]
region_menu = tk.OptionMenu(root, region_var, *regions)
region_menu.grid(row=3, column=1, padx=10, pady=5)
region_var.trace("w", lambda *args: connect_to_region())

tk.Label(root, text="Patients:").grid(row=4, column=0, padx=10, pady=5, sticky="ne")
patients_table = ttk.Treeview(root, columns=("ID",), show="headings", selectmode="extended", height=10)
patients_table.heading("ID", text="Patient ID")
patients_table.grid(row=4, column=1, padx=10, pady=5, sticky="w")
scrollbar = ttk.Scrollbar(root, orient="vertical", command=patients_table.yview)
patients_table.configure(yscroll=scrollbar.set)
scrollbar.grid(row=4, column=2, sticky='ns', pady=5)

tk.Button(root, text="Add User", command=add_user).grid(row=5, column=0, columnspan=3, pady=10)

connect_to_region()

root.mainloop()
