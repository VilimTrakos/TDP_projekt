import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime
import sys
from data_handler import save_visit_record

REGION_COUCHDB_MAPPING = {
    "Zagreb": 5986,    # couch_c
    "Osijek": 5985,    # couch_b
    "Varazdin": 5984,  # couch_a
}

def submit_record(patient_id, role, region):
    visit_date = date_entry.get()
    diagnosis = diagnosis_text.get("1.0", tk.END).strip()
    medicine = medicine_text.get("1.0", tk.END).strip()
    follow_up_date_str = follow_up_calendar.get_date()

    if not visit_date or not diagnosis or not medicine:
        messagebox.showwarning("Incomplete Data", "Please fill in all required fields.")
        return

    try:
        visit_datetime = datetime.strptime(visit_date, "%d.%m.%Y")
        visit_date_formatted = visit_datetime.strftime("%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Invalid Date Format", "Please enter the visit date in dd.mm.yyyy format.")
        return

    try:
        follow_up_datetime = datetime.strptime(follow_up_date_str, "%d.%m.%Y")
        if follow_up_datetime < datetime.now():
            messagebox.showwarning("Invalid Date", "Follow-up date cannot be in the past.")
            return
        follow_up_date_formatted = follow_up_datetime.strftime("%Y-%m-%d")
    except ValueError:
        messagebox.showwarning("Invalid Date Format", "Please enter the follow-up date in dd.mm.yyyy format.")
        return

    couchdb_port = REGION_COUCHDB_MAPPING.get(region)
    if not couchdb_port:
        messagebox.showerror("Error", f"No CouchDB port mapping found for region '{region}'.")
        return

    new_visit = {
        "patient_id": patient_id,            
        "visit_date": visit_date_formatted,             
        "diagnosis": diagnosis,
        "medicine": medicine,
        "follow_up_date": follow_up_date_formatted
    }
    
    save_visit_record(new_visit, couchdb_port)

    messagebox.showinfo("Success", f"New visit record added successfully!\nFollow-up on: {follow_up_date_formatted}")
    add_window.destroy()

def on_close():
    add_window.destroy()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        messagebox.showerror("Error", "Patient ID, role, and region must be provided.")
        sys.exit(1)
    
    patient_id = sys.argv[1]
    role = sys.argv[2].lower()
    region = sys.argv[3]

    add_window = tk.Tk()
    add_window.title("New Visit Record")

    tk.Label(add_window, text="Visit Date (dd.mm.yyyy):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    current_date_str = datetime.now().strftime("%d.%m.%Y")
    date_entry = tk.Entry(add_window)
    date_entry.insert(0, current_date_str)
    date_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Diagnosis:").grid(row=1, column=0, padx=10, pady=5, sticky="ne")
    diagnosis_text = tk.Text(add_window, height=5, width=30)
    diagnosis_text.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Medicine:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
    medicine_text = tk.Text(add_window, height=5, width=30)
    medicine_text.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Follow-up Date:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    follow_up_calendar = Calendar(add_window, date_pattern="dd.mm.yyyy", mindate=datetime.now())
    follow_up_calendar.grid(row=3, column=1, padx=10, pady=5)

    submit_button = tk.Button(
        add_window,
        text="Add Record",
        command=lambda: submit_record(patient_id, role, region)
    )
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)

    add_window.protocol("WM_DELETE_WINDOW", on_close)
    add_window.mainloop()
