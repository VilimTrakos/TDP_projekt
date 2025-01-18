import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os
import subprocess

from data_handler import load_patient_doc, load_visit_records

REGION_COUCHDB_MAPPING = {
    "Zagreb": 5986,    # couch_c
    "Osijek": 5985,    # couch_b
    "Varazdin": 5984,  # couch_a
}

app_window = None
visit_tree = None
couchdb_port = None

def refresh_visit_tree(patient_id, role):
    visit_tree.delete(*visit_tree.get_children())

    visit_data = load_visit_records(patient_id, role, couchdb_port)

    valid_visits = []
    for record in visit_data:
        if not record.get("visit_date"):
            record["visit_date"] = "ERROR"
        valid_visits.append(record)

    try:
        sorted_visit_data = sorted(
            valid_visits,
            key=lambda x: datetime.strptime(x["visit_date"], "%Y-%m-%d"),
            reverse=True
        )
    except (KeyError, ValueError) as e:
        messagebox.showerror("Error", f"Invalid date format in visit record: {e}")
        sorted_visit_data = valid_visits

    for visit_record in sorted_visit_data:
        if role.lower() == "doctor":
            visit_tree.insert(
                "", "end",
                values=(
                    visit_record.get("visit_date", ""),
                    visit_record.get("diagnosis", ""),
                    visit_record.get("medicine", ""),
                    visit_record.get("follow_up_date", "")
                )
            )
        else:
            visit_tree.insert("", "end", values=(visit_record.get("visit_date", ""),))

def sort_visit_tree(column):
    if not hasattr(sort_visit_tree, 'sort_states'):
        sort_visit_tree.sort_states = {"Date": False}
    if column == "Date":
        sort_visit_tree.sort_states[column] = not sort_visit_tree.sort_states[column]
        reverse = sort_visit_tree.sort_states[column]
        
        items = list(visit_tree.get_children())
        try:
            items_sorted = sorted(
                items,
                key=lambda x: datetime.strptime(visit_tree.set(x, column), "%Y-%m-%d"),
                reverse=reverse
            )
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format in column '{column}': {e}")
            return
        
        for index, item in enumerate(items_sorted):
            visit_tree.move(item, "", index)

def view_record(patient_id, record):
    view_window = tk.Toplevel(app_window)
    view_window.title("View Record")
    
    tk.Label(view_window, text="Visit Date:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    date_entry = tk.Entry(view_window)
    date_entry.insert(0, record["visit_date"])
    date_entry.config(state='disabled')
    date_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(view_window, text="Diagnosis:").grid(row=1, column=0, padx=10, pady=5, sticky="ne")
    diagnosis_text = tk.Text(view_window, height=5, width=30)
    diagnosis_text.insert("1.0", record["diagnosis"])
    diagnosis_text.config(state='disabled')
    diagnosis_text.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(view_window, text="Medicine:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
    medicine_text = tk.Text(view_window, height=5, width=30)
    medicine_text.insert("1.0", record["medicine"])
    medicine_text.config(state='disabled')
    medicine_text.grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(view_window, text="Follow-up Date:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    follow_up_entry = tk.Entry(view_window)
    follow_up_entry.insert(0, record["follow_up_date"])
    follow_up_entry.config(state='disabled')
    follow_up_entry.grid(row=3, column=1, padx=10, pady=5)
    
    close_button = tk.Button(view_window, text="Close", command=view_window.destroy)
    close_button.grid(row=4, column=0, columnspan=2, pady=10)

def open_new_record(patient_id, role, region):
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "new_record.py")

    if patient_id:
        try:
            subprocess.Popen([python_executable, script_path, patient_id, role, region])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch new_record.py: {e}")
    else:
        messagebox.showerror("Error", "No valid patient_id to link this new record.")

def open_general_info(patient_id, role, region):
    global visit_tree, app_window, couchdb_port

    app_window = tk.Tk()
    app_window.title("Record Details")

    couchdb_port = REGION_COUCHDB_MAPPING.get(region)
    if couchdb_port is None:
        messagebox.showerror("Error", f"No CouchDB port mapping found for region '{region}'.")
        app_window.destroy()
        return
    
    patient_doc = load_patient_doc(patient_id, role, couchdb_port)
    if not patient_doc:
        messagebox.showerror("Error", "Patient document not found.")
        app_window.destroy()
        return

    name    = patient_doc.get("first_name", "")
    surname = patient_doc.get("last_name", "")
    oib     = patient_doc.get("oib", "")
    dob     = patient_doc.get("date_of_birth", "")
    gender  = patient_doc.get("gender", "")
    contact = patient_doc.get("email", "")

    general_info_frame = tk.Frame(app_window)
    general_info_frame.pack(side="left", padx=10, pady=10)

    tk.Label(general_info_frame, text="General Info", font=("Arial", 14, "bold")).pack()
    tk.Label(general_info_frame, text=f"Name: {name}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Surname: {surname}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"OIB: {oib}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Date of Birth: {dob}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Gender: {gender}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Contact: {contact}").pack(anchor="w")

    visit_frame = tk.Frame(app_window)
    visit_frame.pack(side="right", padx=10, pady=10)

    tk.Label(visit_frame, text="Visit Records", font=("Arial", 14, "bold")).pack()

    if role.lower() == 'doctor':
        visit_columns = ("Date", "Diagnosis", "Medicine", "Follow-up")
    else:
        visit_columns = ("Date",)

    visit_tree = ttk.Treeview(visit_frame, columns=visit_columns, show="headings")

    for col in visit_columns:
        if col == "Date":
            visit_tree.heading(col, text=col, command=lambda c=col: sort_visit_tree(c))
        else:
            visit_tree.heading(col, text=col)
        visit_tree.column(col, minwidth=0, width=120, stretch=True)

    visit_tree.pack(pady=5, fill="both", expand=True)

    refresh_visit_tree(patient_id, role)

    if role.lower() == 'doctor':
        tk.Button(
            visit_frame, 
            text="Add New Record", 
            command=lambda: open_new_record(patient_id, role, region)
        ).pack(pady=5)

        tk.Button(
            visit_frame, 
            text="View Record", 
            command=lambda: view_selected_record(patient_id, role)
        ).pack(pady=5)
    else:
        tk.Label(visit_frame, text="Insufficient permissions to add/view visits.").pack(pady=5)

    app_window.mainloop()

def view_selected_record(patient_id, role):
    selected_item = visit_tree.focus()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a visit record to view.")
        return

    values = visit_tree.item(selected_item, "values")
    if role.lower() == "doctor" and len(values) < 4:
        messagebox.showerror("Error", "Selected visit record is incomplete.")
        return
    if role.lower() != "doctor" and len(values) < 1:
        messagebox.showerror("Error", "Selected visit record is incomplete.")
        return

    visit_date = values[0]
    diagnosis  = values[1] if role.lower() == "doctor" else ""
    medicine   = values[2] if role.lower() == "doctor" else ""

    matching_visits = [
        v for v in load_visit_records(patient_id, role, couchdb_port)
        if (
            v.get("visit_date") == visit_date
            and (role.lower() != "doctor" or v.get("diagnosis") == diagnosis)
            and (role.lower() != "doctor" or v.get("medicine") == medicine)
        )
    ]

    if matching_visits:
        record = matching_visits[0]
        view_record(patient_id, record)
    else:
        messagebox.showerror("Error", "Selected visit record not found.")

def main():
    if len(sys.argv) < 4:
        messagebox.showerror("Error", "Patient ID, role, and region must be provided.")
        sys.exit(1)

    patient_id = sys.argv[1]
    role = sys.argv[2].lower()
    region = sys.argv[3]

    open_general_info(patient_id, role, region)

if __name__ == "__main__":
    main()
