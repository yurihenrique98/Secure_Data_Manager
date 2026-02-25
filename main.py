import sqlite3
import re
import tkinter as tk
from tkinter import Tk, Label, Entry, Button, messagebox, filedialog, Canvas
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import os

# --- Configuration & Security ---
DB_NAME = "CustomerRegistry.db"
selected_image_path = None 

def load_encryption_key():
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    with open("secret.key", "rb") as key_file:
        return key_file.read()

encryption_key = load_encryption_key()
cipher_suite = Fernet(encryption_key)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Email TEXT UNIQUE,
            Phone TEXT,
            Image BLOB,
            CustomerDataXML TEXT
        )
    """)
    conn.commit()
    conn.close()

def connect_to_db():
    return sqlite3.connect(DB_NAME)

# --- Logic Functions ---
def validate_inputs(name, email, phone):
    if not name.strip():
        messagebox.showerror("Input Error", "Name cannot be empty!")
        return False
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        messagebox.showerror("Input Error", "Invalid email format!")
        return False
    if not phone.isdigit() or len(phone) != 10:
        messagebox.showerror("Input Error", "Phone number must be 10 digits!")
        return False
    return True

def insert_customer():
    global selected_image_path
    name = entry_name.get().strip()
    email = entry_email.get().strip()
    phone = entry_phone.get().strip()

    if not validate_inputs(name, email, phone):
        return

    # Encrypt sensitive data before saving
    encrypted_email = cipher_suite.encrypt(email.encode()).decode()
    image_data = None
    if selected_image_path:
        with open(selected_image_path, "rb") as f:
            image_data = f.read()

    conn = connect_to_db()
    try:
        conn.execute("INSERT INTO Customers (Name, Email, Phone, Image) VALUES (?, ?, ?, ?)", 
                       (name, encrypted_email, phone, image_data))
        conn.commit()
        messagebox.showinfo("Success", "Customer added (Encrypted) successfully!")
        clear_fields()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "This email already exists!")
    finally:
        conn.close()

def fetch_customer():
    search_email = entry_email.get().strip()
    if not search_email:
        messagebox.showerror("Input Error", "Enter email to search!")
        return

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT CustomerID, Name, Email, Phone FROM Customers")
    rows = cursor.fetchall()
    
    found = False
    for row in rows:
        try:
            # Decrypt to find a match
            decrypted_email = cipher_suite.decrypt(row[2].encode()).decode()
            if decrypted_email == search_email:
                entry_id.delete(0, "end")
                entry_id.insert(0, row[0])
                entry_name.delete(0, "end")
                entry_name.insert(0, row[1])
                entry_phone.delete(0, "end")
                entry_phone.insert(0, row[3])
                found = True
                break
        except: continue

    if not found:
        messagebox.showerror("Error", "Customer not found!")
    conn.close()

def select_image():
    global selected_image_path
    try:
        path = filedialog.askopenfilename(
            parent=root, 
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if path:
            selected_image_path = path
            img = Image.open(selected_image_path)
            img.thumbnail((100, 100))
            img_tk = ImageTk.PhotoImage(img)
            image_canvas.create_image(50, 50, anchor="center", image=img_tk)
            image_canvas.image = img_tk 
    except Exception as e:
        messagebox.showerror("Error", f"Dialog Error: {e}")

def store_xml():
    customer_id = entry_id.get().strip()
    if not customer_id:
        messagebox.showerror("Error", "Fetch a customer first!")
        return
    
    xml_data = f"<Customer><ID>{customer_id}</ID><Name>{entry_name.get()}</Name></Customer>"
    conn = connect_to_db()
    conn.execute("UPDATE Customers SET CustomerDataXML = ? WHERE CustomerID = ?", (xml_data, customer_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "XML Generated and Stored!")

def clear_fields():
    entry_id.delete(0, "end")
    entry_name.delete(0, "end")
    entry_email.delete(0, "end")
    entry_phone.delete(0, "end")
    image_canvas.delete("all")

# ... (all your previous imports and logic functions stay the same) ...

# --- GUI SETUP ---
init_db()
root = Tk()
root.title("Secure Data Manager")
root.geometry("600x800") # Increased height slightly for breathing room
root.configure(bg="#2c2c2c")

# Style Configurations
label_style = {"bg": "#2c2c2c", "fg": "#ffffff", "font": ("Helvetica", 12, "bold")}

# FIX: Changed entry foreground to a very light gray/white for better readability 
# inside the dark text boxes.
entry_style = {
    "bg": "#3d3d3d", 
    "fg": "#00ffcc",  # Neon cyan text inside boxes makes it super readable
    "insertbackground": "white", 
    "relief": "flat", 
    "font": ("Helvetica", 12), 
    "width": 30
}

# The button style you requested (Black text on Light background)
button_style = {
    "bg": "#f0f0f0", 
    "fg": "#000000", 
    "relief": "flat", 
    "activebackground": "#00adb5", 
    "activeforeground": "#ffffff", 
    "font": ("Helvetica", 11, "bold"), 
    "width": 18, 
    "pady": 10
}

# Main container
main_frame = tk.Frame(root, bg="#2c2c2c")
main_frame.place(relx=0.5, rely=0.5, anchor="center") 

# Input Section 
input_frame = tk.LabelFrame(main_frame, text="  Customer Information  ", bg="#2c2c2c", fg="#00adb5", font=("Helvetica", 14, "bold"), padx=25, pady=25)
input_frame.pack(fill="x", pady=20)

labels = ["ID:", "Name:", "Email:", "Phone:"]
entries = []

for i, text in enumerate(labels):
    Label(input_frame, text=text, **label_style).grid(row=i, column=0, sticky="w", pady=12)
    e = Entry(input_frame, **entry_style)
    e.grid(row=i, column=1, sticky="ew", padx=15)
    entries.append(e)

entry_id, entry_name, entry_email, entry_phone = entries

# Image Section
image_frame = tk.Frame(main_frame, bg="#2c2c2c")
image_frame.pack(pady=10)

image_canvas = Canvas(image_frame, width=150, height=150, bg="#3d3d3d", highlightthickness=2, highlightbackground="#00adb5")
image_canvas.pack(pady=10)

Button(image_frame, text="SELECT IMAGE", command=select_image, **button_style).pack()

# Action Buttons 
button_frame = tk.Frame(main_frame, bg="#2c2c2c")
button_frame.pack(pady=20)

Button(button_frame, text="ADD CUSTOMER", command=insert_customer, **button_style).grid(row=0, column=0, padx=10, pady=10)
Button(button_frame, text="SEARCH (EMAIL)", command=fetch_customer, **button_style).grid(row=0, column=1, padx=10, pady=10)
Button(button_frame, text="GENERATE XML", command=store_xml, **button_style).grid(row=1, column=0, padx=10, pady=10)
Button(button_frame, text="CLEAR ALL", command=clear_fields, **button_style).grid(row=1, column=1, padx=10, pady=10)

root.mainloop()