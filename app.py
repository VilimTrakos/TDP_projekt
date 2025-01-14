import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

username = sys.argv[1]
region = sys.argv[2]

def open_details_window():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a record to view details.")
        return
    
    record = tree.item(selected_item, "values")
    record_str = ";".join(record)
    
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "general_info.py")
    
    subprocess.Popen([python_executable, script_path, record_str])

def search_table():
    query = search_var.get().lower()
    for row in tree.get_children():
        values = tree.item(row, "values")
        if any(query in str(value).lower() for value in values):
            tree.item(row, tags="match")
        else:
            tree.item(row, tags="nomatch")
    tree.tag_configure("match", background="white")
    tree.tag_configure("nomatch", background="gray")

app_window = tk.Tk()
app_window.title("Data Viewer")

tk.Label(app_window, text=f"Username: {username} | Region: {region}").pack(pady=5)

search_var = tk.StringVar()
tk.Label(app_window, text="Search:").pack(pady=5)
search_entry = tk.Entry(app_window, textvariable=search_var)
search_entry.pack(pady=5)
search_entry.bind("<KeyRelease>", lambda e: search_table())

columns = ("Name", "Surname", "OIB", "Date of Birth", "Gender", "Contact")
tree = ttk.Treeview(app_window, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col, command=lambda c=col: sort_table(c, False))
tree.pack(pady=5, fill="both", expand=True)

# dummy podaci
data = [
    ("John", "Cena", "123456789", "23.04.1980", "M", "john@example.com"),
    ("Jane", "Doe", "987654321", "15.09.1990", "F", "jane@example.com"),
    ("Paul", "Smith", "456123789", "05.12.1985", "M", "paul@example.com"),
    ("Anna", "Taylor", "321654987", "19.07.1992", "F", "anna@example.com")
]

for record in data:
    tree.insert("", "end", values=record)

def sort_table(col, reverse):
    data_list = [(tree.set(k, col), k) for k in tree.get_children("")]
    data_list.sort(reverse=reverse)
    for index, (val, k) in enumerate(data_list):
        tree.move(k, "", index)
    tree.heading(col, command=lambda: sort_table(col, not reverse))

tk.Button(app_window, text="View Details", command=open_details_window).pack(pady=10)

app_window.mainloop()
