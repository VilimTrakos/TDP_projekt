import tkinter as tk
from tkinter import messagebox
from utils import launch_script
import sys

VALID_CREDENTIALS = {
    "john_doe": "password123",
    "jane_smith": "securepass",
    "":""
}

def check_login():
    username = username_entry.get()
    password = password_entry.get()
    selected_region = region_var.get()
    
    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        login_window.destroy()
        launch_script("app.py", username, selected_region)
    else:
        messagebox.showerror("Login Error", "Invalid username or password")
        password_entry.delete(0, tk.END)

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x250")

tk.Label(login_window, text="Username:").pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password:").pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

tk.Label(login_window, text="Select region:").pack(pady=5)
region_var = tk.StringVar(login_window)
region_var.set("Zagreb")
regions = ["Zagreb", "Osijek", "Varazdin", "Split"]
region_menu = tk.OptionMenu(login_window, region_var, *regions)
region_menu.pack(pady=5)

tk.Button(login_window, text="Login", command=check_login).pack(pady=10)

login_window.mainloop()
