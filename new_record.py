import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime

def submit_record():
    date = date_entry.get()
    diagnosis = diagnosis_text.get("1.0", tk.END).strip()
    medicine = medicine_text.get("1.0", tk.END).strip()
    follow_up_date = follow_up_calendar.get_date()

    if not date or not diagnosis or not medicine:
        messagebox.showwarning("Incomplete Data", "Please fill in all required fields.")
        return

    if datetime.strptime(follow_up_date, "%d.%m.%Y") < datetime.now():
        messagebox.showwarning("Invalid Date", "Follow-up date cannot be in the past.")
        return
    
    messagebox.showinfo("Success", f"New record added successfully!\nFollow-up on: {follow_up_date}")
    new_record_window.destroy()

new_record_window = tk.Tk()
new_record_window.title("New Record")

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

new_record_window.mainloop()
