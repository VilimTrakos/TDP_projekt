import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import sys
import os

from data_handler import load_patient_doc, load_visit_records, save_visit_record

def add_new_record(oib):
    def submit_record():
        date = date_entry.get()
        diagnosis = diagnosis_text.get("1.0", tk.END).strip()
        medicine = medicine_text.get("1.0", tk.END).strip()
        follow_up_date = follow_up_calendar.get_date()
        
        if not date or not diagnosis or not medicine:
            messagebox.showwarning("Incomplete Data", "Please fill in all required fields.")
            return
        
        try:
            visit_datetime = datetime.strptime(date, "%d.%m.%Y")
            follow_up_datetime = datetime.strptime(follow_up_date, "%d.%m.%Y")
            if follow_up_datetime < datetime.now():
                messagebox.showwarning("Invalid Date", "Follow-up date cannot be in the past.")
                return
        except ValueError:
            messagebox.showwarning("Invalid Date Format", "Please enter dates in dd.mm.yyyy format.")
            return
        
        new_visit = {
            "OIB": oib,
            "Date": date,
            "Diagnosis": diagnosis,
            "Medicine": medicine,
            "Follow-up Date": follow_up_date
        }
        save_visit_record(new_visit)
        
        messagebox.showinfo("Success", f"New visit record added successfully!\nFollow-up on: {follow_up_date}")
        add_window.destroy()
        
        refresh_visit_tree(oib)
    
    def on_close():
        add_window.destroy()
    
    add_window = tk.Toplevel(app_window)
    add_window.title("New Visit Record")
    
    tk.Label(add_window, text="Date (Visit):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    current_date = datetime.now().strftime("%d.%m.%Y")
    date_entry = tk.Entry(add_window)
    date_entry.insert(0, current_date)
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
    
    submit_button = tk.Button(add_window, text="Add Record", command=submit_record)
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)
    
    add_window.protocol("WM_DELETE_WINDOW", on_close)

def refresh_visit_tree(oib):
    visit_tree.delete(*visit_tree.get_children())
    
    visit_data = load_visit_records(oib)
    sorted_visit_data = sorted(
        visit_data,
        key=lambda x: datetime.strptime(x["Date"], "%d.%m.%Y"),
        reverse=True 
    )
    
    for visit_record in sorted_visit_data:
        visit_tree.insert("", "end", values=(
            visit_record["Date"], 
            visit_record["Diagnosis"], 
            visit_record["Medicine"]
        ))

def sort_visit_tree(column):
    if not hasattr(sort_visit_tree, 'sort_states'):
        sort_visit_tree.sort_states = {"Date": False}
    if column == "Date":
        sort_visit_tree.sort_states[column] = not sort_visit_tree.sort_states[column]
        reverse = sort_visit_tree.sort_states[column]
        
        items = list(visit_tree.get_children())
        items_sorted = sorted(
            items,
            key=lambda x: datetime.strptime(visit_tree.set(x, column), "%d.%m.%Y"),
            reverse=reverse
        )
        for index, item in enumerate(items_sorted):
            visit_tree.move(item, "", index)

def view_record(oib, record):
    view_window = tk.Toplevel(app_window)
    view_window.title("View Record")
    
    tk.Label(view_window, text="Date (Visit):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    date_entry = tk.Entry(view_window)
    date_entry.insert(0, record["Date"])
    date_entry.config(state='disabled')
    date_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(view_window, text="Diagnosis:").grid(row=1, column=0, padx=10, pady=5, sticky="ne")
    diagnosis_text = tk.Text(view_window, height=5, width=30)
    diagnosis_text.insert("1.0", record["Diagnosis"])
    diagnosis_text.config(state='disabled')
    diagnosis_text.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(view_window, text="Medicine:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
    medicine_text = tk.Text(view_window, height=5, width=30)
    medicine_text.insert("1.0", record["Medicine"])
    medicine_text.config(state='disabled')
    medicine_text.grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(view_window, text="Follow-up Date:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    follow_up_entry = tk.Entry(view_window)
    follow_up_entry.insert(0, record["Follow-up Date"])
    follow_up_entry.config(state='disabled')
    follow_up_entry.grid(row=3, column=1, padx=10, pady=5)
    
    close_button = tk.Button(view_window, text="Close", command=view_window.destroy)
    close_button.grid(row=4, column=0, columnspan=2, pady=10)

def open_general_info(record):
    global current_oib, visit_tree, app_window
    app_window = tk.Tk()
    app_window.title("Record Details")
    
    current_oib = record[2]  

    patient_doc = load_patient_doc(current_oib)
    
    if patient_doc:
        name = patient_doc.get("first_name", "")
        surname = patient_doc.get("last_name", "")
        dob = patient_doc.get("date_of_birth", "")
        gender = patient_doc.get("gender", "")
        contact = patient_doc.get("email", "") 
    else:
        name, surname, _, dob, gender, contact = record
    
    general_info_frame = tk.Frame(app_window)
    general_info_frame.pack(side="left", padx=10, pady=10)
    
    tk.Label(general_info_frame, text="General Info", font=("Arial", 14, "bold")).pack()
    tk.Label(general_info_frame, text=f"Name: {name}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Surname: {surname}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"OIB: {current_oib}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Date of Birth: {dob}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Gender: {gender}").pack(anchor="w")
    tk.Label(general_info_frame, text=f"Contact: {contact}").pack(anchor="w")
    
    visit_frame = tk.Frame(app_window)
    visit_frame.pack(side="right", padx=10, pady=10)
    
    tk.Label(visit_frame, text="Visit Records", font=("Arial", 14, "bold")).pack()
    visit_columns = ("Date", "Diagnosis", "Medicine")
    visit_tree = ttk.Treeview(visit_frame, columns=visit_columns, show="headings")
    
    for col in visit_columns:
        if col == "Date":
            visit_tree.heading(col, text=col, command=lambda c=col: sort_visit_tree(c))
        else:
            visit_tree.heading(col, text=col)
        visit_tree.column(col, minwidth=0, width=100, stretch=True)
    
    visit_tree.pack(pady=5, fill="both", expand=True)
    
    refresh_visit_tree(current_oib)
    
    tk.Button(visit_frame, text="Add New Record", command=lambda: add_new_record(current_oib)).pack(pady=5)
    tk.Button(visit_frame, text="View Record", command=lambda: view_selected_record(current_oib)).pack(pady=5)
    
    app_window.mainloop()

def view_selected_record(oib):
    selected_item = visit_tree.focus()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a visit record to view.")
        return
    values = visit_tree.item(selected_item, "values")
    record = {
        "Date": values[0],
        "Diagnosis": values[1],
        "Medicine": values[2],
        "Follow-up Date": next(
            (visit["Follow-up Date"] for visit in load_visit_records(oib)
             if visit["Date"] == values[0] and visit["Diagnosis"] == values[1] and visit["Medicine"] == values[2]),
            ""
        )
    }
    view_record(oib, record)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        record_str = sys.argv[1]
        record = record_str.split(";")
        if len(record) == 6:
            open_general_info(record)
        else:
            messagebox.showerror("Error", "Invalid record data provided.")
    else:
        messagebox.showerror("Error", "No record data provided.")
