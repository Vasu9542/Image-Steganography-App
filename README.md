# Image-Steganography-App
from pathlib import Path

# 🖼️ Image Steganography App (Python + Tkinter)

This is a GUI-based desktop application to **hide** and **extract** secret messages in images using **LSB steganography**. It also securely emails the password and stego image using your Gmail credentials.

---

## 📁 Project Structure

.
- ├── image_steganography_app.py # Main application script                   
- ├── passwords.txt # Stores image-password mappings
- ├── output_images/ # Directory for saved stego images
- ├── logo.png # Optional logo displayed on the main screen
---

## 🔧 Features

- Hide text messages inside `.png` or `.jpg` images
- Automatically generate a secure password
- Email the stego image and password to the recipient
- Extract message only with the correct password
- Secure GUI with email and file browsing
- Uses only **Python** and **Tkinter**

---

## 🚀 How It Works

### 1. Main Window
- Shows heading and logo image
- Buttons:
  - 🔐 **Hide Text**: Opens message embedding window
  - 🔓 **Extract Text**: Opens message extraction window

### 2. Hide Text Page
- Upload an image using a file dialog
- Enter:
  - Secret message
  - Sender email (Gmail)
  - App password (Gmail App Password)
  - Receiver email
- Output:
  - Message is hidden inside image
  - Image is saved to `output_images/`
  - Password + image sent to recipient

### 3. Extract Text Page
- Upload stego image
- Enter the password received by email
- Extracts and displays the secret message

---

## 🔐 Security & Email

- Passwords are stored in `passwords.txt`
- Emails are sent securely using `smtplib` with SSL
- You must use a **Gmail App Password**, not your real Gmail password

---





