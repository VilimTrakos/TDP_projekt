import couchdb
import uuid

def connect_to_couchdb():
    try:
        couch = couchdb.Server('http://admin:admin@localhost:5984/') 
        db = couch['medical_records']
        return db
    except Exception as e:
        print(f"Error connecting to CouchDB: {e}")
        return None

def load_data(role, related_id):
    db = connect_to_couchdb()
    if not db:
        return []

    user_doc = db.get(related_id)
    if not user_doc:
        print("No user document found with related_id:", related_id)
        return []

    assigned_patients = user_doc.get("patients", [])

    patient_data = []
    for pid in assigned_patients:
        patient_doc = db.get(pid)
        if patient_doc and patient_doc.get("type") == "patient":
            name = patient_doc.get("first_name", "")
            surname = patient_doc.get("last_name", "")
            oib = patient_doc.get("oib", "")
            dob = patient_doc.get("date_of_birth", "")
            gender = patient_doc.get("gender", "")
            contact = patient_doc.get("email", "") 

            patient_data.append((name, surname, oib, dob, gender, contact))

    return patient_data

def load_patient_doc(oib):
    db = connect_to_couchdb()
    if not db:
        return None

    for doc_id in db:
        doc = db[doc_id]
        if doc.get("type") == "patient" and doc.get("oib") == oib:
            return doc
    return None

def load_visit_records(patient_id):
    db = connect_to_couchdb()
    if not db:
        return []

    visits = []
    for doc_id in db:
        doc = db[doc_id]
        if doc.get("type") == "visit" and doc.get("patient_id") == patient_id:
            visits.append(doc)
    return visits

def save_visit_record(visit):
    db = connect_to_couchdb()
    if not db:
        print("No database connection. Cannot save visit record.")
        return

    visit_id = f"visit_{uuid.uuid4()}"
    visit_doc = {
        "_id": visit_id,
        "type": "visit",
        "patient_id": visit["patient_id"],
        "visit_date": visit["visit_date"],
        "diagnosis": visit["diagnosis"],
        "medicine": visit["medicine"],
        "follow_up_date": visit["follow_up_date"]
    }

    try:
        db.save(visit_doc)
        print(f"Saved new visit: {visit_id}, linked to patient_id: {visit['patient_id']}")
    except Exception as e:
        print(f"Error saving visit: {e}")
        return
