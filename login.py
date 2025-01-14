import tkinter as tk
from tkinter import messagebox
import subprocess

def check_login():
    username = username_entry.get()
    password = password_entry.get()
    selected_region = region_var.get()
    
    if username == "" and password == "": 
        login_window.destroy()
        subprocess.Popen(["python", "app.py", username, selected_region])
        app_window.attributes('-topmost', True) 
    else:
        messagebox.showerror("Login Error", "Invalid username or password")

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
