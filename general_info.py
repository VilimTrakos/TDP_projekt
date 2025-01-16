import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import sys
import os
import subprocess

from data_handler import load_patient_doc, load_visit_records

def refresh_visit_tree(patient_id, role):
    visit_tree.delete(*visit_tree.get_children())

    visit_data = load_visit_records(patient_id, role)

    try:
        sorted_visit_data = sorted(
            visit_data,
            key=lambda x: datetime.strptime(x["visit_date"], "%d.%m.%Y"),
            reverse=True 
        )
    except KeyError as e:
        messagebox.showerror("Error", f"Missing field in visit record: {e}")
        sorted_visit_data = []
    except ValueError as e:
        messagebox.showerror("Error", f"Invalid date format in visit record: {e}")
        sorted_visit_data = []

    for visit_record in sorted_visit_data:
        visit_tree.insert("", "end", values=(
            visit_record.get("visit_date", ""), 
            visit_record.get("diagnosis", ""),
            visit_record.get("medicine", "")
        ))

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
                key=lambda x: datetime.strptime(visit_tree.set(x, column), "%d.%m.%Y"),
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

def open_new_record(patient_id):
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "new_record.py")
    if patient_id:
        try:
            subprocess.Popen([python_executable, script_path, patient_id])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch new_record.py: {e}")
    else:
        messagebox.showerror("Error", "No valid patient_id to link this new record.")

def open_general_info(record, role):
    global visit_tree, app_window

    app_window = tk.Tk()
    app_window.title("Record Details")

    oib_from_tuple = record[2]

    patient_doc = load_patient_doc(oib_from_tuple, role)

    if patient_doc:
        name = patient_doc.get("first_name", "")
        surname = patient_doc.get("last_name", "")
        dob = patient_doc.get("date_of_birth", "")
        gender = patient_doc.get("gender", "")
        contact = patient_doc.get("email", "")
        patient_id = patient_doc["_id"]
    else:
        name, surname, _, dob, gender, contact = record
        patient_id = None

    general_info_frame = tk.Frame(app_window)
    general_info_frame.pack(side="left", padx=10, pady=10)

    tk.Label(general_info_frame, text="General Info", font=("Arial", 14, "bold")).pack()
    tk.Label(general_info_frame, text=f"Name: {name}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Surname: {surname}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"OIB: {oib_from_tuple}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Date of Birth: {dob}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Gender: {gender}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Contact: {contact}").pack(anchor="w")

    visit_frame = tk.Frame(app_window)
    visit_frame.pack(side="right", padx=10, pady=10)

    tk.Label(visit_frame, text="Visit Records", font=("Arial", 14, "bold")).pack()

    if role == 'doctor':
        visit_columns = ("Date", "Diagnosis", "Medicine")
    elif role == 'staff':
        visit_columns = ("Date",)
    else:
        visit_columns = ("Date",)

    visit_tree = ttk.Treeview(visit_frame, columns=visit_columns, show="headings")

    for col in visit_columns:
        if col == "Date":
            visit_tree.heading(col, text=col, command=lambda c=col: sort_visit_tree(c))
        else:
            visit_tree.heading(col, text=col)
        visit_tree.column(col, minwidth=0, width=100, stretch=True)

    visit_tree.pack(pady=5, fill="both", expand=True)

    if patient_id:
        refresh_visit_tree(patient_id, role)

    if patient_id and role == 'doctor':
        tk.Button(
            visit_frame, 
            text="Add New Record", 
            command=lambda: open_new_record(patient_id)
        ).pack(pady=5)

        tk.Button(
            visit_frame, 
            text="View Record", 
            command=lambda: view_selected_record(patient_id)
        ).pack(pady=5)
    else:
        tk.Label(
            visit_frame, 
            text="No valid patient_id found or insufficient permissions to add/view visits."
        ).pack(pady=5)

    app_window.mainloop()

def view_selected_record(patient_id):
    selected_item = visit_tree.focus()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a visit record to view.")
        return
    values = visit_tree.item(selected_item, "values")
    matching_visits = [
        visit for visit in load_visit_records(patient_id, role)
        if visit.get("visit_date") == values[0] and
           visit.get("diagnosis") == values[1] and
           visit.get("medicine") == values[2]
    ]
    if matching_visits:
        record = matching_visits[0]
        view_record(patient_id, record)
    else:
        messagebox.showerror("Error", "Selected visit record not found.")

def main():
    if len(sys.argv) > 2:
        record_str = sys.argv[1]
        role = sys.argv[2].lower()
        record = record_str.split(";")
        if len(record) == 6:
            open_general_info(record, role)
        else:
            messagebox.showerror("Error", "Invalid record data provided.")
    else:
        messagebox.showerror("Error", "Record data and role must be provided.")
        sys.exit(1)

if __name__ == "__main__":
    main()
