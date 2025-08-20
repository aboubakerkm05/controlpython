import socket
import threading
import tkinter as tk
from tkinter import messagebox
import time

widgets = {}
code_buffer = None  # لتخزين الكود الجديد عند استلامه

def connect_server():
    global client_socket
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(("localhost", 12345))  # غيّر localhost إلى IP السيرفر
            threading.Thread(target=listen_server, daemon=True).start()
            print("[+] Connected to server")
            break
        except:
            print("[-] Could not connect to server, retrying in 3s...")
            time.sleep(3)

def listen_server():
    buffer = ""
    while True:
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break
            buffer += data
            while "<END>" in buffer:
                msg, buffer = buffer.split("<END>", 1)
                root.after(0, handle_message, msg.strip())
        except:
            break

def handle_message(msg):
    global code_buffer

    if msg == "FULL_CODE_START":
        code_buffer = ""
    elif msg == "FULL_CODE_END":
        if code_buffer is not None:
            try:
                with open("mygame.py", "w", encoding="utf-8") as f:
                    f.write(code_buffer)
                exec(code_buffer, globals())
                messagebox.showinfo("Update", "Application code updated. Restart recommended.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        code_buffer = None
    elif code_buffer is not None:
        code_buffer += msg + "\n"

    elif msg.startswith("CMD:"):
        cmd = msg[4:].strip()
        if cmd == "update":
            if "update_btn" not in widgets:
                btn = tk.Button(root, text="Update Now", command=lambda: messagebox.showinfo("Update", "Updating..."))
                btn.pack()
                widgets["update_btn"] = btn
        elif cmd == "remove update":
            if "update_btn" in widgets:
                widgets["update_btn"].destroy()
                del widgets["update_btn"]
        elif cmd == "newlabel":
            if "label" not in widgets:
                lbl = tk.Label(root, text="New Label from server")
                lbl.pack()
                widgets["label"] = lbl
        elif cmd == "remove newlabel":
            if "label" in widgets:
                widgets["label"].destroy()
                del widgets["label"]
        else:
            messagebox.showinfo("Message", cmd)

def app():
    global root
    root = tk.Tk()
    root.title("Client App")
    root.geometry("400x300")

    tk.Label(root, text="salam khalil").pack(pady=20)

    threading.Thread(target=connect_server, daemon=True).start()

    root.mainloop()

app()
