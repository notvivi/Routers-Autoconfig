import tkinter as tk
from tkinter import filedialog
import subprocess
import sys
import json
import os
import threading
import time
lib_path = sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lib")))
sys.path.append(lib_path)
import resource_path


def run_script():
    write_into_config()
    run_button.config(state="disabled")
    threading.Thread(target=run_main_process).start()

def run_main_process():
    main_path = resource_path.resource_path("src/main.py")
    working_dir = os.path.dirname(main_path)
    safe_write_output(f"Running: {main_path}\n")
    try:
        process = subprocess.Popen(
            [sys.executable, main_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=working_dir
        )

        while True:
            line = process.stdout.readline()
            if line:
                safe_write_output(line)
            elif process.poll() is not None:
                break
            else:
                time.sleep(0.05)

        process.stdout.close()
        process.wait()
        safe_write_output("\nProcess finished.\n")
        root.after(0, lambda: run_button.config(state="normal"))
    except Exception as e:
        safe_write_output(f"\nError: {e}\n")


def write_into_config():
    data = {
        "linux_vpss_file": vps_file_path.get(),
        "log_file": log_file_path.get(),
        "ssh_password": password_entry.get(),
        "threads": int(threads_entry.get()) if threads_entry.get().isdigit() else 1,
        "commands": ["uptime", "date"]
    }
    config_path = resource_path.resource_path("src/config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def select_log_file():
    path = filedialog.askopenfilename(
        title="Add log file",
        filetypes=(("Textové soubory", "*.txt"), ("Všechny soubory", "*.*"))
    )
    if path:
        log_file_path.set(path)

def select_vps_file():
    path = filedialog.askopenfilename(
        title="Vyber VPS soubor",
        filetypes=(("Textové soubory", "*.txt"), ("Všechny soubory", "*.*"))
    )
    if path:
        vps_file_path.set(path)

root = tk.Tk()
root.title("Will add later")
root.geometry("500x500")

tk.Label(root, text="Password").pack(pady=5)
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack()

tk.Label(root, text="Number of threads").pack(pady=5)
threads_entry = tk.Entry(root, width=30)
threads_entry.pack()

log_file_path = tk.StringVar()
tk.Label(root, text="LOG file").pack(pady=5)
tk.Entry(root, textvariable=log_file_path, width=45).pack()
tk.Button(root, text="Vybrat LOG soubor", command=select_log_file).pack(pady=5)

vps_file_path = tk.StringVar()
tk.Label(root, text="VPS file").pack(pady=5)
tk.Entry(root, textvariable=vps_file_path, width=45).pack()
tk.Button(root, text="Vybrat VPS soubor", command=select_vps_file).pack(pady=5)


run_button = tk.Button(root, text="Run script", command=run_script)
run_button.pack(pady=20)

tk.Label(root, text="Output").pack(pady=5)

output_text = tk.Text(root, height=12, width=60, state="disabled")
output_text.pack(pady=5)


def write_output(text):
    output_text.config(state="normal")
    output_text.insert(tk.END, text)
    output_text.see(tk.END)
    output_text.config(state="disabled")


def safe_write_output(text):
    root.after(0, lambda: write_output(text))

root.mainloop()