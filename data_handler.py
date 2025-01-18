import couchdb
import os
from cryptography.fernet import Fernet, InvalidToken
from tkinter import messagebox
import uuid

def connect_to_couchdb():
    try:
        couch = couchdb.Server('http://admin:password@localhost:5985/')
        db_name = 'medical_records'
        if db_name in couch:
            db = couch[db_name]
            return db
        else:
            messagebox.showerror("Error", f"Database '{db_name}' does not exist.")
            return None
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to CouchDB: {e}")
        return None

def decrypt_field(encrypted_value, fernet, field_name=""):
    if not encrypted_value:
        return None
    try:
        return fernet.decrypt(encrypted_value.encode()).decode()
    except (InvalidToken, Exception):
        return None

def encrypt_field(plaintext, fernet, field_name=""):
    if not plaintext:
        return None
    try:
        return fernet.encrypt(plaintext.encode()).decode()
    except Exception:
        return None

def load_data(role, related_id):
    db = connect_to_couchdb()
    if not db:
        return []

    encryption_key_doctor = os.getenv('ENCRYPTION_KEY_DOCTOR')
    encryption_key_shared = os.getenv('ENCRYPTION_KEY_SHARED')
    encryption_key_staff = os.getenv('ENCRYPTION_KEY_STAFF')

    if not encryption_key_doctor or not encryption_key_shared or not encryption_key_staff:
        messagebox.showerror("Encryption Key Error", "Encryption keys for doctor, staff, and shared data are not set.")
        return []

    try:
        fernet_doctor = Fernet(encryption_key_doctor.encode())
        fernet_shared = Fernet(encryption_key_shared.encode())
        fernet_staff = Fernet(encryption_key_staff.encode())
    except ValueError as e:
        messagebox.showerror("Encryption Key Error", f"Invalid encryption key: {e}")
        return []

    patient_records = []
    try:
        user_doc = db.get(related_id)
        if not user_doc or "patients" not in user_doc:
            messagebox.showerror("Error", "User not found or no patients assigned.")
            return []

        assigned_patients = user_doc["patients"]
        for patient_id in assigned_patients:
            patient_doc = db.get(patient_id)
            if patient_doc and patient_doc.get("type") == "patient":
                decrypted_first_name = decrypt_field(patient_doc.get("first_name", ""), fernet_shared, "First Name")
                decrypted_last_name  = decrypt_field(patient_doc.get("last_name", ""),  fernet_shared, "Last Name")
                gender = patient_doc.get("gender", "")

                if role.lower() == 'doctor':
                    decrypted_oib = decrypt_field(patient_doc.get("oib", ""), fernet_shared, "OIB")
                    if decrypted_oib is None:
                        decrypted_oib = decrypt_field(patient_doc.get("oib", ""), fernet_doctor, "OIB")
                        if decrypted_oib is None:
                            decrypted_oib = "Decryption Failed"
                    decrypted_dob = decrypt_field(patient_doc.get("date_of_birth", ""), fernet_doctor, "Date of Birth")
                    decrypted_email = decrypt_field(patient_doc.get("email", ""), fernet_doctor, "Email")
                    
                else:
                    decrypted_oib   = "Encrypted"
                    decrypted_dob   = "Encrypted"
                    decrypted_email = "Encrypted"

                record_tuple = (
                    patient_doc.get("_id"),
                    decrypted_first_name,
                    decrypted_last_name,
                    decrypted_oib,
                    decrypted_dob,
                    gender,
                    decrypted_email
                )
                patient_records.append(record_tuple)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load patient data: {e}")
        return []
    return patient_records

def load_patient_doc(patient_id, role):
    db = connect_to_couchdb()
    if not db:
        return None
    encryption_key_doctor = os.getenv('ENCRYPTION_KEY_DOCTOR')
    encryption_key_shared = os.getenv('ENCRYPTION_KEY_SHARED')
    if not encryption_key_doctor or not encryption_key_shared:
        messagebox.showerror("Encryption Key Error", "ENCRYPTION_KEY_DOCTOR and/or ENCRYPTION_KEY_SHARED environment variables not set.")
        return None
    try:
        fernet_doctor = Fernet(encryption_key_doctor.encode())
        fernet_shared = Fernet(encryption_key_shared.encode())
    except ValueError as e:
        messagebox.showerror("Encryption Key Error", f"Invalid encryption key: {e}")
        return None
    try:
        patient_doc = db.get(patient_id)
        if not patient_doc or patient_doc.get("type") != "patient":
            return None

        if role.lower() == 'doctor':
            decrypted_first_name = decrypt_field(patient_doc.get("first_name", ""), fernet_shared, "First Name")
            decrypted_last_name = decrypt_field(patient_doc.get("last_name", ""), fernet_shared, "Last Name")
            decrypted_oib = decrypt_field(patient_doc.get("oib", ""), fernet_shared, "OIB")
            if decrypted_oib is None:
                decrypted_oib = decrypt_field(patient_doc.get("oib", ""), fernet_doctor, "OIB")
                if decrypted_oib is None:
                    decrypted_oib = "Decryption Failed"
            decrypted_dob = decrypt_field(patient_doc.get("date_of_birth", ""), fernet_doctor, "Date of Birth")
            decrypted_email = decrypt_field(patient_doc.get("email", ""), fernet_doctor, "Email")
            decrypted_doc = {
                "_id": patient_doc.get("_id"),
                "first_name": decrypted_first_name,
                "last_name": decrypted_last_name,
                "oib": decrypted_oib,
                "date_of_birth": decrypted_dob,
                "gender": patient_doc.get("gender", ""),
                "email": decrypted_email
            }
            return decrypted_doc

        else:
            decrypted_first_name = decrypt_field(patient_doc.get("first_name", ""), fernet_shared, "First Name")
            decrypted_last_name = decrypt_field(patient_doc.get("last_name", ""), fernet_shared, "Last Name")
            return {
                "_id": patient_doc.get("_id"),
                "first_name": decrypted_first_name,
                "last_name": decrypted_last_name,
                "oib": "Encrypted",
                "date_of_birth": "Encrypted",
                "gender": patient_doc.get("gender", ""),
                "email": "Encrypted"
            }

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load patient document: {e}")
        return None

def load_visit_records(patient_id, role):
    db = connect_to_couchdb()
    if not db:
        return []
    encryption_key_doctor = os.getenv('ENCRYPTION_KEY_DOCTOR')
    encryption_key_staff = os.getenv('ENCRYPTION_KEY_STAFF')
    encryption_key_shared = os.getenv('ENCRYPTION_KEY_SHARED')
    if not encryption_key_doctor or not encryption_key_staff or not encryption_key_shared:
        messagebox.showerror("Encryption Key Error", 
            "ENCRYPTION_KEY_DOCTOR, ENCRYPTION_KEY_STAFF, and/or ENCRYPTION_KEY_SHARED environment variables not set.")
        return []
    try:
        fernet_doctor = Fernet(encryption_key_doctor.encode())
        fernet_staff = Fernet(encryption_key_staff.encode())
        fernet_shared = Fernet(encryption_key_shared.encode())
    except ValueError as e:
        messagebox.showerror("Encryption Key Error", f"Invalid encryption key: {e}")
        return []
    visit_records = []
    try:
        for doc_id in db:
            doc = db[doc_id]
            if doc.get("type") == "visit" and doc.get("patient_id") == patient_id:
                if role.lower() == 'doctor':
                    decrypted_visit_date = decrypt_field(doc.get("visit_date", ""), fernet_shared, "Visit Date")
                    decrypted_diagnosis = decrypt_field(doc.get("diagnosis", ""), fernet_doctor, "Diagnosis")
                    decrypted_medicine = decrypt_field(doc.get("medicine", ""), fernet_doctor, "Medicine")
                    decrypted_follow_up_date = decrypt_field(doc.get("follow_up_date", ""), fernet_doctor, "Follow-up Date")
                elif role.lower() == 'staff':
                    decrypted_visit_date = decrypt_field(doc.get("visit_date", ""), fernet_shared, "Visit Date")
                    decrypted_diagnosis = "Encrypted"
                    decrypted_medicine = "Encrypted"
                    decrypted_follow_up_date = "Encrypted"

                else:
                    decrypted_visit_date = decrypt_field(doc.get("visit_date", ""), fernet_shared, "Visit Date")
                    decrypted_diagnosis = "Encrypted"
                    decrypted_medicine = "Encrypted"
                    decrypted_follow_up_date = "Encrypted"

                visit_record = {
                    "visit_date": decrypted_visit_date,
                    "diagnosis": decrypted_diagnosis,
                    "medicine": decrypted_medicine,
                    "follow_up_date": decrypted_follow_up_date
                }
                visit_records.append(visit_record)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visit records: {e}")
        return []
    return visit_records

def save_visit_record(visit_data):
    db = connect_to_couchdb()
    if not db:
        return
    encryption_key_doctor = os.getenv('ENCRYPTION_KEY_DOCTOR')
    encryption_key_shared = os.getenv('ENCRYPTION_KEY_SHARED')
    if not encryption_key_doctor or not encryption_key_shared:
        messagebox.showerror(
            "Encryption Key Error", 
            "ENCRYPTION_KEY_DOCTOR and/or ENCRYPTION_KEY_SHARED environment variables not set."
        )
        return
    try:
        fernet_doctor = Fernet(encryption_key_doctor.encode())
        fernet_shared = Fernet(encryption_key_shared.encode())
    except ValueError as e:
        messagebox.showerror("Encryption Key Error", f"Invalid encryption key: {e}")
        return

    try:
        encrypted_visit_date = encrypt_field(visit_data['visit_date'], fernet_shared, "Visit Date")
        encrypted_diagnosis = encrypt_field(visit_data['diagnosis'], fernet_doctor, "Diagnosis")
        encrypted_medicine = encrypt_field(visit_data['medicine'], fernet_doctor, "Medicine")
        encrypted_follow_up_date = encrypt_field(visit_data['follow_up_date'], fernet_doctor, "Follow-up Date")
        
        if None in [encrypted_visit_date, encrypted_diagnosis, encrypted_medicine, encrypted_follow_up_date]:
            messagebox.showerror("Encryption Error", "Failed to encrypt one or more fields.")
            return
        
        visit_id = f"visit_{uuid.uuid4()}"
        visit_doc = {
            "_id": visit_id,
            "type": "visit",
            "patient_id": visit_data['patient_id'],
            "visit_date": encrypted_visit_date,
            "diagnosis": encrypted_diagnosis,
            "medicine": encrypted_medicine,
            "follow_up_date": encrypted_follow_up_date
        }
        
        db.save(visit_doc)
        messagebox.showinfo("Success", f"Visit record added successfully with ID '{visit_id}'.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save visit record: {e}")
