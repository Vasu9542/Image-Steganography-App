import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import secrets
import string
import smtplib, ssl
from email.message import EmailMessage
import mimetypes
import webbrowser
import sys
import time

# ------------------------------------------
# Handle paths for PyInstaller executable
# ------------------------------------------
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller .exe """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

# ------------------------------------------
# Constants
# ------------------------------------------
PASSWORD_FILE = "passwords.txt"
UPLOAD_DIR = "output_images"
PROJECT_INFO_HTML = resource_path("project_info.html")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------------------------------
# Utility functions
# ------------------------------------------
def generate_password(length=8):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def send_password_via_email(sender_email, smtp_password, receiver_email, password, attachment_path):
    message = EmailMessage()
    message["Subject"] = "Your Steganography Password and Image"
    message["From"] = sender_email
    message["To"] = receiver_email
    message.set_content(f"Your password to extract the hidden message is:\n\n{password}")

    mime_type, _ = mimetypes.guess_type(attachment_path)
    mime_type, mime_subtype = mime_type.split('/')

    with open(attachment_path, 'rb') as ap:
        message.add_attachment(ap.read(),
                               maintype=mime_type,
                               subtype=mime_subtype,
                               filename=os.path.basename(attachment_path))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, smtp_password)
        server.send_message(message)

def hide_text_in_image(image_path, message):
    img = Image.open(image_path)
    encoded = img.copy()
    width, height = encoded.size
    message += chr(0)
    binary_msg = ''.join(format(ord(c), '08b') for c in message)

    pixels = encoded.load()
    idx = 0
    for y in range(height):
        for x in range(width):
            if idx >= len(binary_msg):
                break
            pixel = pixels[x, y]
            r, g, b = pixel[:3]
            r = (r & ~1) | int(binary_msg[idx])
            idx += 1
            if idx < len(binary_msg):
                g = (g & ~1) | int(binary_msg[idx])
                idx += 1
            if idx < len(binary_msg):
                b = (b & ~1) | int(binary_msg[idx])
                idx += 1
            pixels[x, y] = (r, g, b) + pixel[3:] if len(pixel) == 4 else (r, g, b)
        if idx >= len(binary_msg):
            break

    timestamp = int(time.time())
    out_filename = f"stego_{timestamp}_{os.path.basename(image_path)}"
    out_path = os.path.join(UPLOAD_DIR, out_filename)
    encoded.save(out_path)

    password = generate_password()
    with open(PASSWORD_FILE, 'a') as f:
        f.write(f"{out_filename}:{password}\n")

    return password, out_path

def extract_text_from_image(image_path, password_input):
    filename = os.path.basename(image_path).strip()
    password_input = password_input.strip()
    actual_password = None

    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            for line in f:
                try:
                    name, pw = line.strip().split(":", 1)
                    name = name.strip()
                    pw = pw.strip()
                    if filename == name:
                        actual_password = pw
                        break
                except ValueError:
                    continue

    if not actual_password:
        raise ValueError("No password found for this image.")
    if password_input != actual_password:
        raise ValueError("Incorrect password.")

    img = Image.open(image_path)
    width, height = img.size
    pixels = img.load()

    binary_data = ""
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            r, g, b = pixel[:3]
            binary_data += str(r & 1) + str(g & 1) + str(b & 1)

    chars = [chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8)]
    return ''.join(chars).split(chr(0))[0]

# ------------------------------------------
# GUI
# ------------------------------------------
def create_main_window():
    root = tk.Tk()
    root.title("Image Steganography")
    root.geometry("500x400")

    title_label = tk.Label(root, text="Image Steganography", font=("Arial", 18, "bold"), fg="blue", cursor="hand2")
    title_label.pack(pady=10)
    title_label.bind("<Button-1>", lambda e: webbrowser.open_new(PROJECT_INFO_HTML))

    try:
        img = Image.open(resource_path("logo.png"))
        img = img.resize((200, 200))
        logo = ImageTk.PhotoImage(img)
        tk.Label(root, image=logo).pack(pady=5)
        root.logo = logo
    except:
        tk.Label(root, text="[Logo image not found]", fg="gray").pack()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="Hide Text", command=open_hide_window, width=20).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Extract Text", command=open_extract_window, width=20).grid(row=0, column=1, padx=10)

    root.mainloop()

def open_hide_window():
    win = tk.Toplevel()
    win.title("Hide Text")

    fields = ["Image File:", "Message:", "Sender Email:", "SMTP Password:", "Receiver Email:"]
    for i, label in enumerate(fields):
        tk.Label(win, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)

    img_entry = tk.Entry(win, width=40)
    img_entry.grid(row=0, column=1, padx=5)
    tk.Button(win, text="Browse", command=lambda: img_entry.insert(0, filedialog.askopenfilename())).grid(row=0, column=2, padx=5)

    msg_entry = tk.Text(win, height=4, width=30)
    msg_entry.grid(row=1, column=1, columnspan=2, padx=5)

    sender_entry = tk.Entry(win, width=40)
    sender_entry.grid(row=2, column=1, columnspan=2, padx=5)

    pass_entry = tk.Entry(win, width=40, show="*")
    pass_entry.grid(row=3, column=1, columnspan=2, padx=5)

    recv_entry = tk.Entry(win, width=40)
    recv_entry.grid(row=4, column=1, columnspan=2, padx=5)

    def handle_hide():
        try:
            password, out_img = hide_text_in_image(img_entry.get(), msg_entry.get("1.0", tk.END).strip())
            send_password_via_email(sender_entry.get(), pass_entry.get(), recv_entry.get(), password, out_img)
            messagebox.showinfo("Success", f"Saved: {out_img}\nPassword sent to {recv_entry.get()}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text="Hide Text", command=handle_hide, width=20).grid(row=5, column=1, pady=10)

def open_extract_window():
    win = tk.Toplevel()
    win.title("Extract Text")

    tk.Label(win, text="Image File:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
    img_entry = tk.Entry(win, width=40)
    img_entry.grid(row=0, column=1, padx=5)
    tk.Button(win, text="Browse", command=lambda: img_entry.insert(0, filedialog.askopenfilename())).grid(row=0, column=2, padx=5)

    tk.Label(win, text="Password:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
    pwd_entry = tk.Entry(win, width=40, show="*")
    pwd_entry.grid(row=1, column=1, columnspan=2, padx=5)

    def handle_extract():
        try:
            message = extract_text_from_image(img_entry.get(), pwd_entry.get())
            messagebox.showinfo("Hidden Message", message)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text="Extract Text", command=handle_extract, width=20).grid(row=2, column=1, pady=10)

# ------------------------------------------
# Run the App
# ------------------------------------------
if __name__ == "__main__":
    create_main_window()
