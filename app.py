import tkinter as tk
from tkinter import ttk, messagebox
from utils import launch_script
import sys
import os
from data_handler import load_data

def open_details_window():
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a record to view details.")
        return
    
    record = tree.item(selected_item, "values")
    record_str = ";".join(record)
    launch_script("general_info.py", record_str, role)

def search_table(event=None):
    query = search_var.get().lower()
    for row in tree.get_children():
        values = tree.item(row, "values")
        if any(query in str(value).lower() for value in values):
            tree.item(row, tags="match")
        else:
            tree.item(row, tags="nomatch")
    tree.tag_configure("match", background="white")
    tree.tag_configure("nomatch", background="gray")

def sort_table(col):
    global sort_states
    sort_states[col] = not sort_states[col]
    reverse = sort_states[col]
    data_list = [(tree.set(k, col), k) for k in tree.get_children("")]
    data_list.sort(reverse=reverse)
    for index, (val, k) in enumerate(data_list):
        tree.move(k, "", index)
    tree.heading(col, command=lambda: sort_table(col))

if len(sys.argv) < 5:
    messagebox.showerror("Error", "Username, role, related_id, and region must be provided.")
    sys.exit(1)

username = sys.argv[1]
role = sys.argv[2].lower()
related_id = sys.argv[3]
region = sys.argv[4]

app_window = tk.Tk()
app_window.title("Data Viewer")

tk.Label(app_window, text=f"Username: {username} | Role: {role.capitalize()} | Region: {region}").pack(pady=5)

search_var = tk.StringVar()
tk.Label(app_window, text="Search:").pack(pady=5)
search_entry = tk.Entry(app_window, textvariable=search_var)
search_entry.pack(pady=5)
search_entry.bind("<KeyRelease>", search_table)

columns = ("Name", "Surname", "OIB", "Date of Birth", "Gender", "Contact")
tree = ttk.Treeview(app_window, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col, command=lambda c=col: sort_table(c))
    tree.column(col, minwidth=0, width=100, stretch=True)
tree.pack(pady=5, fill="both", expand=True)

data = load_data(role, related_id)
for record in data:
    tree.insert("", "end", values=record)

sort_states = {col: False for col in columns}

tk.Button(app_window, text="View Details", command=open_details_window).pack(pady=10)

app_window.mainloop()
