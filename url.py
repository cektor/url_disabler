import ctypes
import sys
import os
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk  # Tema desteği

# Yönetici izinleri kontrolü
def check_admin():
    system_platform = platform.system()
    if system_platform == 'Windows':
        try:
            if ctypes.windll.shell32.IsUserAnAdmin() != 1:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()
        except Exception as e:
            messagebox.showerror("Hata", f"Yönetici izinleri alınamadı: {e}")
            sys.exit()
    elif system_platform in ['Linux', 'Darwin']:
        if os.geteuid() != 0:
            messagebox.showerror("Hata", "Bu uygulama yönetici (sudo) izni gerektiriyor.")
            sys.exit()

# URL engelleme işlemi
def block_url():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("Hata", "Bir URL girin!")
        return

    system_platform = platform.system()
    hosts_path = ""
    redirect = "127.0.0.1"

    if system_platform == 'Windows':
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    elif system_platform in ['Darwin', 'Linux']:
        hosts_path = "/etc/hosts"

    try:
        with open(hosts_path, "r+") as file:
            lines = file.readlines()
            if any(url in line for line in lines):
                messagebox.showinfo("Bilgi", f"{url} zaten engellenmiş.")
                return

            file.write(f"\n{redirect} {url}")
        
        listbox.insert(tk.END, url)
        with open("engellenen_url.txt", "a") as f:
            f.write(f"{url}\n")
        messagebox.showinfo("Başarılı", f"{url} başarıyla engellendi.")
    except PermissionError:
        messagebox.showerror("Hata", "Yazma izniniz yok. Yönetici izinleri gerekebilir.")
    except Exception as e:
        messagebox.showerror("Hata", f"Hata oluştu: {e}")

# URL kaldırma işlemi
def unblock_url():
    try:
        selected_url = listbox.get(listbox.curselection())  # Listbox'dan seçilen URL
    except IndexError:
        messagebox.showwarning("Hata", "Kaldırmak için bir URL seçin!")
        return

    system_platform = platform.system()
    hosts_path = ""

    if system_platform == 'Windows':
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    elif system_platform in ['Darwin', 'Linux']:
        hosts_path = "/etc/hosts"

    try:
        with open(hosts_path, "r") as file:
            lines = file.readlines()

        with open(hosts_path, "w") as file:
            for line in lines:
                if selected_url not in line:
                    file.write(line)

        # Listbox ve dosyadan URL'yi kaldır
        listbox.delete(listbox.curselection())
        if os.path.exists("engellenen_url.txt"):
            with open("engellenen_url.txt", "r") as f:
                urls = f.readlines()
            with open("engellenen_url.txt", "w") as f:
                for line in urls:
                    if selected_url not in line.strip("\n"):
                        f.write(line)
        messagebox.showinfo("Başarılı", f"{selected_url} başarıyla kaldırıldı.")
    except PermissionError:
        messagebox.showerror("Hata", "Yazma izniniz yok. Yönetici izinleri gerekebilir.")
    except Exception as e:
        messagebox.showerror("Hata", f"Hata oluştu: {e}")

# Engellenen URL'leri yükle
def load_blocked_urls():
    if os.path.exists("engellenen_url.txt"):
        with open("engellenen_url.txt", "r") as file:
            for line in file:
                listbox.insert(tk.END, line.strip())

# Yönetici kontrolü
check_admin()

# GUI Tasarımı
root = ThemedTk(theme="arc")
root.title("URL Disabler")
root.geometry("500x400")

url_label = ttk.Label(root, text="Engellemek veya kaldırmak istediğiniz URL'yi girin:")
url_label.pack(pady=10)

url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=5)

block_button = ttk.Button(root, text="URL'yi Engelle", command=block_url)
block_button.pack(pady=10)

unblock_button = ttk.Button(root, text="URL'yi Kaldır", command=unblock_url)
unblock_button.pack(pady=10)

listbox_label = ttk.Label(root, text="Engellenen URL'ler:")
listbox_label.pack(pady=10)

listbox = tk.Listbox(root, width=60, height=10)
listbox.pack(pady=5)

# Engellenen URL'leri yükle
load_blocked_urls()

root.mainloop()
