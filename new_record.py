import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime
import sys
from data_handler import save_visit_record

def submit_record():
    date = date_entry.get()
    diagnosis = diagnosis_text.get("1.0", tk.END).strip()
    medicine = medicine_text.get("1.0", tk.END).strip()
    follow_up_date = follow_up_calendar.get_date()
    
    if not date or not diagnosis or not medicine:
        messagebox.showwarning("Incomplete Data", "Please fill in all required fields.")
        return
    
    try:
        follow_up_datetime = datetime.strptime(follow_up_date, "%d.%m.%Y")
        if follow_up_datetime < datetime.now():
            messagebox.showwarning("Invalid Date", "Follow-up date cannot be in the past.")
            return
    except ValueError:
        messagebox.showwarning("Invalid Date Format", "Please enter the date in dd.mm.yyyy format.")
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
    new_record_window.destroy()
    

def on_close():
    new_record_window.destroy()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        messagebox.showerror("Error", "OIB must be provided.")
        sys.exit(1)
    
    oib = sys.argv[1]
    
    new_record_window = tk.Tk()
    new_record_window.title("New Visit Record")
    
    tk.Label(new_record_window, text="Date (Visit):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    current_date = datetime.now().strftime("%d.%m.%Y")
    date_entry = tk.Entry(new_record_window)
    date_entry.insert(0, current_date)
    date_entry.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(new_record_window, text="Diagnosis:").grid(row=1, column=0, padx=10, pady=5, sticky="ne")
    diagnosis_text = tk.Text(new_record_window, height=5, width=30)
    diagnosis_text.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(new_record_window, text="Medicine:").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
    medicine_text = tk.Text(new_record_window, height=5, width=30)
    medicine_text.grid(row=2, column=1, padx=10, pady=5)
    
    tk.Label(new_record_window, text="Follow-up Date:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    follow_up_calendar = Calendar(new_record_window, date_pattern="dd.mm.yyyy", mindate=datetime.now())
    follow_up_calendar.grid(row=3, column=1, padx=10, pady=5)
    
    submit_button = tk.Button(new_record_window, text="Add Record", command=submit_record)
    submit_button.grid(row=4, column=0, columnspan=2, pady=10)
    
    new_record_window.protocol("WM_DELETE_WINDOW", on_close)
    new_record_window.mainloop()
