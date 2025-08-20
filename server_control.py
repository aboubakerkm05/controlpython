import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

clients = {}          # {conn: ip}
commands_log = []     # كل الأوامر المرسلة

def handle_client(conn, addr):
    ip = addr[0]
    clients[conn] = ip
    update_status(f"New connection from {ip}")
    update_clients_list()

    # نرسل كل الأوامر السابقة للعميل الجديد
    for cmd in commands_log:
        try:
            conn.sendall(("CMD:" + cmd + "\n<END>\n").encode("utf-8"))
        except:
            pass

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
        except:
            break

    # العميل خرج
    if conn in clients:
        ip = clients.pop(conn)
        update_status(f"Client disconnected: {ip}")
        update_clients_list()
    conn.close()

def broadcast(msg, save=True):
    if msg.startswith("CMD:") and save:
        cmd = msg[4:]
        commands_log.append(cmd)
        listbox.insert(tk.END, cmd)

    for conn in list(clients.keys()):
        try:
            conn.sendall((msg + "\n<END>\n").encode("utf-8"))
        except:
            pass

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.listen(5)
    update_status("Server started, waiting for connections...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def send_command():
    cmd = simpledialog.askstring("Send Command", "Enter command:")
    if cmd:
        broadcast("CMD:" + cmd)

def remove_command():
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Warning", "Select a command to remove")
        return
    idx = sel[0]
    cmd = commands_log.pop(idx)
    listbox.delete(idx)
    if cmd in ["update", "newlabel"]:
        broadcast("CMD:remove " + cmd, save=True)
    else:
        messagebox.showinfo("Info", f"No remove action defined for '{cmd}'")

def edit_code():
    try:
        with open("mygame.py", "r", encoding="utf-8") as f:
            content = f.read()
    except:
        content = ""

    editor = tk.Toplevel(root)
    editor.title("Edit mygame.py")
    editor.geometry("700x500")

    frame = tk.Frame(editor)
    frame.pack(fill=tk.BOTH, expand=True)

    text = tk.Text(frame, wrap="none")
    text.insert("1.0", content)

    yscroll = tk.Scrollbar(frame, orient="vertical", command=text.yview)
    xscroll = tk.Scrollbar(frame, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

    text.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")

    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    def save_and_send():
        new_code = text.get("1.0", "end-1c")
        try:
            with open("mygame.py", "w", encoding="utf-8") as f:
                f.write(new_code)

            # إرسال الكود باستخدام بروتوكول خاص
            broadcast("FULL_CODE_START", save=False)
            for line in new_code.splitlines():
                broadcast(line, save=False)
            broadcast("FULL_CODE_END", save=False)

            messagebox.showinfo("Done", "New code sent to all clients.")
            editor.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(editor, text="Done", command=save_and_send).pack(pady=5)

def update_status(msg):
    count = len(clients)
    root.after(0, lambda: status_label.config(
        text=f"{msg} | Clients connected: {count}"
    ))

def update_clients_list():
    root.after(0, lambda: (
        clients_list.delete(0, tk.END),
        [clients_list.insert(tk.END, ip) for ip in clients.values()]
    ))

def run_gui():
    global root, listbox, status_label, clients_list
    root = tk.Tk()
    root.title("Server Control")
    root.geometry("700x500")

    # أزرار التحكم
    topbar = tk.Frame(root)
    topbar.pack(fill=tk.X, side=tk.TOP)
    tk.Button(topbar, text="Add Code", command=edit_code).pack(side=tk.RIGHT, padx=5, pady=2)
    tk.Button(topbar, text="Send Command", command=send_command).pack(side=tk.RIGHT, padx=5, pady=2)

    # قائمة الأوامر
    listbox = tk.Listbox(root, width=80, height=12)
    listbox.pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack()
    tk.Button(btn_frame, text="Remove", command=remove_command, width=15).grid(row=0, column=0, padx=5)

    # قائمة العملاء
    tk.Label(root, text="Connected Clients:").pack()
    clients_list = tk.Listbox(root, width=50, height=6)
    clients_list.pack(pady=5)

    # الحالة أسفل النافذة
    status_label = tk.Label(root, text="Starting server...", fg="blue")
    status_label.pack(pady=10)

    # تشغيل السيرفر في خلفية
    threading.Thread(target=start_server, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    run_gui()
