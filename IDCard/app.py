import os
import random
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# Function to generate a 10-digit unique ID
def generate_id():
    return ''.join(random.choices('0123456789', k=10))

# Function to create the ID card
def create_id_card():
    # Get user inputs
    full_name = entry_name.get()
    address = entry_address.get()
    photo_path = entry_photo.get()

    if not full_name or not address or not photo_path:
        messagebox.showerror("Error", "Please fill all fields and select a photo.")
        return

    # Generate ID
    id_number = generate_id()

    # Load background image
    background = Image.open("background.png")  # Replace with your background image
    background = background.resize((800, 500))  # Resize to ID card size

    # Load user photo
    user_photo = Image.open(photo_path).resize((150, 150))

    # Paste user photo onto the background
    background.paste(user_photo, (50, 150))

    # Draw text on the image
    draw = ImageDraw.Draw(background)
    font = ImageFont.load_default()  # Use default font or load a custom font
    draw.text((220, 160), f"Name: {full_name}", fill="black", font=font)
    draw.text((220, 200), f"ID: {id_number}", fill="black", font=font)
    draw.text((220, 240), f"Address: {address}", fill="black", font=font)

    # Save the ID card image
    id_card_path = f"id_card_{id_number}.png"
    background.save(id_card_path)

    # Show success message
    messagebox.showinfo("Success", f"ID card saved as {id_card_path}")
    preview_id_card(id_card_path)

# Function to preview the ID card
def preview_id_card(image_path):
    preview_window = Toplevel(root)
    preview_window.title("ID Card Preview")

    img = Image.open(image_path)
    img = img.resize((400, 250))  # Resize for preview
    img = ImageTk.PhotoImage(img)

    label = Label(preview_window, image=img)
    label.image = img  # Keep a reference to avoid garbage collection
    label.pack()

    # Add a button to print the ID card as PDF
    Button(preview_window, text="Print as PDF", command=lambda: print_pdf(image_path)).pack()

# Function to print the ID card as PDF
def print_pdf(image_path):
    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        return

    # Create a PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    img = Image.open(image_path)
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Draw the image on the PDF
    c.drawImage(img_bytes, 50, 700, width=400, height=250)
    c.save()

    messagebox.showinfo("Success", f"PDF saved as {pdf_path}")

# Function to select a photo
def select_photo():
    photo_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
    entry_photo.delete(0, END)
    entry_photo.insert(0, photo_path)

# GUI setup
root = Tk()
root.title("ID Card Generator")

Label(root, text="Full Name:").grid(row=0, column=0, padx=10, pady=10)
entry_name = Entry(root, width=30)
entry_name.grid(row=0, column=1, padx=10, pady=10)

Label(root, text="Address:").grid(row=1, column=0, padx=10, pady=10)
entry_address = Entry(root, width=30)
entry_address.grid(row=1, column=1, padx=10, pady=10)

Label(root, text="Photo:").grid(row=2, column=0, padx=10, pady=10)
entry_photo = Entry(root, width=30)
entry_photo.grid(row=2, column=1, padx=10, pady=10)
Button(root, text="Browse", command=select_photo).grid(row=2, column=2, padx=10, pady=10)

Button(root, text="Generate ID Card", command=create_id_card).grid(row=3, column=1, pady=20)

root.mainloop()