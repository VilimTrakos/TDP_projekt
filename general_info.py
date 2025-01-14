import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

def open_general_info(record):
    details_window = tk.Tk()
    details_window.title("Record Details")

    general_info_frame = tk.Frame(details_window)
    general_info_frame.pack(side="left", padx=10, pady=10)

    tk.Label(general_info_frame, text="General Info", font=("Arial", 14, "bold")).pack()
    info_labels = ["Name:", "Surname:", "OIB:", "Date of Birth:", "Gender:", "Contact:"]
    for i, value in enumerate(record):
        tk.Label(general_info_frame, text=f"{info_labels[i]} {value}").pack(anchor="w")

    visit_frame = tk.Frame(details_window)
    visit_frame.pack(side="right", padx=10, pady=10)

    tk.Label(visit_frame, text="Visit Records", font=("Arial", 14, "bold")).pack()
    visit_columns = ("Date", "Diagnosis", "Medicines")
    visit_tree = ttk.Treeview(visit_frame, columns=visit_columns, show="headings")
    for col in visit_columns:
        visit_tree.heading(col, text=col)
    visit_tree.pack(pady=5, fill="both", expand=True)

    visit_data = [
        ("25.05.2024", "Cold", "Paracetamol"),
        ("20.01.2024", "Flu", "Ibuprofen"),
        ("12.12.2023", "Allergy", "Antihistamine")
    ]
    for visit_record in visit_data:
        visit_tree.insert("", "end", values=visit_record)

    tk.Button(visit_frame, text="Add New Record", command=lambda: open_new_record(visit_tree)).pack(pady=10)

    details_window.mainloop()

def open_new_record(tree):
    """
    Otvara `new_record.py` skriptu za unos novog zapisa pomoću subprocessa.
    """
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "new_record.py")
    
    subprocess.Popen([python_executable, script_path])

if __name__ == "__main__":
    dummy_record = ["John", "Cena", "123456789", "23.04.1980", "M", "john@example.com"]
    open_general_info(dummy_record)
