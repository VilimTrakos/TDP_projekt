import tkinter as tk
from tkinter import ttk, messagebox
import couchdb
import re
import os
import sys
from cryptography.fernet import Fernet
import argparse

COUCHDB_USER = 'admin'
COUCHDB_PASSWORD = 'password'

REGION_COUCHDB_MAPPING = {
    "Zagreb": "5986",
    "Osijek": "5985",
    "Varazdin": "5984",
}

shared_key = os.getenv('ENCRYPTION_KEY_SHARED')
doctor_key = os.getenv('ENCRYPTION_KEY_DOCTOR')

if not shared_key or not doctor_key:
    raise EnvironmentError("ENCRYPTION_KEY_SHARED and/or ENCRYPTION_KEY_DOCTOR environment variables not set.")

shared_fernet = Fernet(shared_key.encode())
doctor_fernet = Fernet(doctor_key.encode())

db = None
first_name_entry = None
last_name_entry = None
oib_entry = None
dob_entry = None
gender_combo = None
email_entry = None
region_var = None

def connect_to_db(region):
    couchdb_port = REGION_COUCHDB_MAPPING.get(region)
    if not couchdb_port:
        raise ValueError(f"No CouchDB configuration found for region '{region}'.")
    try:
        couchdb_server_url = f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@localhost:{couchdb_port}"
        couch = couchdb.Server(couchdb_server_url)
        db_name = 'medical_records'
        if db_name in couch:
            return couch[db_name]
        else:
            raise ValueError(f"Database '{db_name}' does not exist in region '{region}'.")
    except Exception as e:
        raise ConnectionError(f"Failed to connect to CouchDB in region '{region}': {e}")

def generate_patient_id():
    try:
        patient_ids = [doc_id for doc_id in db if doc_id.startswith("patient_")]
        if not patient_ids:
            return "patient_001"
        numbers = [int(re.findall(r'patient_(\d+)', pid)[0]) for pid in patient_ids]
        return f"patient_{max(numbers) + 1:03d}"
    except Exception as e:
        raise RuntimeError(f"Failed to generate patient ID: {e}")

def validate_oib(oib):
    return re.fullmatch(r'\d{11}', oib) is not None

def encrypt_field(field_value, fernet):
    return fernet.encrypt(field_value.encode()).decode()

def is_oib_unique(oib_encrypted):
    return all(db[doc_id].get("oib") != oib_encrypted for doc_id in db if db[doc_id].get("type") == "patient")

def add_patient(data, region):
    global db
    try:
        db = connect_to_db(region)

        patient_id = generate_patient_id()
        encrypted_oib = encrypt_field(data['oib'], shared_fernet)
        encrypted_first_name = encrypt_field(data['first_name'], shared_fernet)
        encrypted_last_name = encrypt_field(data['last_name'], shared_fernet)
        encrypted_dob = encrypt_field(data['dob'], doctor_fernet)
        encrypted_email = encrypt_field(data['email'], doctor_fernet)

        if not is_oib_unique(encrypted_oib):
            raise ValueError("OIB already exists.")

        patient_doc = {
            "_id": patient_id,
            "type": "patient",
            "first_name": encrypted_first_name,
            "last_name": encrypted_last_name,
            "oib": encrypted_oib,
            "date_of_birth": encrypted_dob,
            "gender": data['gender'],
            "email": encrypted_email
        }

        db.save(patient_doc)
        print(f"Patient '{data['first_name']} {data['last_name']}' added successfully with ID '{patient_id}' in '{region}'.")

    except Exception as e:
        print(f"Error adding patient: {e}")
        sys.exit(1)

def add_patient_gui():
    global db
    first_name = first_name_entry.get().strip()
    last_name = last_name_entry.get().strip()
    oib = oib_entry.get().strip()
    dob = dob_entry.get().strip()
    gender = gender_combo.get().strip()
    email = email_entry.get().strip()
    region = region_var.get()

    if not all([first_name, last_name, oib, dob, gender, email]):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    if not validate_oib(oib):
        messagebox.showwarning("Input Error", "OIB must be exactly 11 digits.")
        return

    try:
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "oib": oib,
            "dob": dob,
            "gender": gender,
            "email": email
        }
        add_patient(data, region)
        messagebox.showinfo("Success", f"Patient '{first_name} {last_name}' added successfully.")
        first_name_entry.delete(0, tk.END)
        last_name_entry.delete(0, tk.END)
        oib_entry.delete(0, tk.END)
        dob_entry.delete(0, tk.END)
        gender_combo.current(0)
        email_entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to add patient: {e}")

def start_gui():
    global first_name_entry, last_name_entry, oib_entry, dob_entry, gender_combo, email_entry, region_var

    root = tk.Tk()
    root.title("Add New Patient")

    tk.Label(root, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    first_name_entry = tk.Entry(root)
    first_name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    last_name_entry = tk.Entry(root)
    last_name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(root, text="OIB:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    oib_entry = tk.Entry(root)
    oib_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(root, text="Date of Birth (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    dob_entry = tk.Entry(root)
    dob_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(root, text="Gender:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    gender_combo = ttk.Combobox(root, values=["Male", "Female", "Other"], state="readonly")
    gender_combo.grid(row=4, column=1, padx=10, pady=5)
    gender_combo.current(0)

    tk.Label(root, text="Email:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    email_entry = tk.Entry(root)
    email_entry.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(root, text="Select Region:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    region_var = tk.StringVar()
    region_var.set("Zagreb")
    region_menu = ttk.Combobox(root, textvariable=region_var, values=list(REGION_COUCHDB_MAPPING.keys()), state="readonly")
    region_menu.grid(row=6, column=1, padx=10, pady=5)
    region_menu.current(0)

    tk.Button(root, text="Add Patient", command=add_patient_gui).grid(row=7, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    if "--terminal" in sys.argv:
        parser = argparse.ArgumentParser(description="Add a new patient.")
        parser.add_argument("--first_name", type=str, required=True, help="First name of the patient")
        parser.add_argument("--last_name", type=str, required=True, help="Last name of the patient")
        parser.add_argument("--oib", type=str, required=True, help="OIB of the patient")
        parser.add_argument("--dob", type=str, required=True, help="Date of birth (YYYY-MM-DD)")
        parser.add_argument("--gender", type=str, choices=["Male", "Female", "Other"], required=True, help="Gender of the patient")
        parser.add_argument("--email", type=str, required=True, help="Email address of the patient")
        parser.add_argument("--baza", type=str, choices=["Zagreb", "Osijek", "Varazdin"], required=True, help="Database region")

        args = parser.parse_args(sys.argv[2:])
        data = vars(args)
        add_patient(data, args.baza)
    else:
        start_gui()
