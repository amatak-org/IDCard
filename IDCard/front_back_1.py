import os
import random
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime, timedelta

# Function to generate a 10-digit unique ID
def generate_id():
    return ''.join(random.choices('0123456789', k=10))

# Function to create rounded corners for the ID card
def round_corners(image, radius=30):
    circle = Image.new('L', (radius * 2, radius * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radius * 2, radius * 2), fill=255)
    alpha = Image.new('L', image.size, 255)
    w, h = image.size
    alpha.paste(circle.crop((0, 0, radius, radius)), (0, 0))
    alpha.paste(circle.crop((radius, 0, radius * 2, radius)), (w - radius, 0))
    alpha.paste(circle.crop((0, radius, radius, radius * 2)), (0, h - radius))
    alpha.paste(circle.crop((radius, radius, radius * 2, radius * 2)), (w - radius, h - radius))
    image.putalpha(alpha)
    return image

# Function to create the ID card (front side)
def create_id_card_front(full_name, id_number, address, photo_path, validity_date):
    # Load background image
    background = Image.open("background.png")  # Replace with your background image
    background = background.resize((800, 500))  # Resize to ID card size

    # Load user photo
    user_photo = Image.open(photo_path).resize((150, 150))
    user_photo = round_corners(user_photo, radius=20)  # Apply rounded corners to the photo

    # Paste user photo onto the background
    background.paste(user_photo, (50, 150), user_photo)

    # Draw text on the image
    draw = ImageDraw.Draw(background)
    font = ImageFont.load_default()  # Use default font or load a custom font
    draw.text((220, 160), f"Name: {full_name}", fill="black", font=font)
    draw.text((220, 200), f"ID: {id_number}", fill="black", font=font)
    draw.text((220, 240), f"Address: {address}", fill="black", font=font)
    draw.text((220, 280), f"Valid Until: {validity_date}", fill="black", font=font)

    return background

# Function to create the ID card (back side)
def create_id_card_back():
    # Create a simple back side design
    back_side = Image.new("RGB", (800, 500), color="white")
    draw = ImageDraw.Draw(back_side)
    font = ImageFont.load_default()
    draw.text((50, 200), "Khmer Democracy Orgnaization(KDO) Inc.", fill="black", font=font)
    draw.text((50, 250), "Contact: +61 395444950", fill="black", font=font)
    draw.text((50, 300), "Website: www.kdo.org.au", fill="black", font=font)
    return back_side

# Function to generate the ID card
def generate_id_card():
    # Get user inputs
    full_name = entry_name.get()
    address = entry_address.get()
    photo_path = entry_photo.get()

    if not full_name or not address or not photo_path:
        messagebox.showerror("Error", "Please fill all fields and select a photo.")
        return

    # Generate ID and validity date
    id_number = generate_id()
    validity_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

    # Create front and back sides of the ID card
    front_side = create_id_card_front(full_name, id_number, address, photo_path, validity_date)
    back_side = create_id_card_back()

    # Save the ID card images
    front_side_path = f"id_card_front_{id_number}.png"
    back_side_path = f"id_card_back_{id_number}.png"
    front_side.save(front_side_path)
    back_side.save(back_side_path)

    # Show success message
    messagebox.showinfo("Success", f"ID card saved as {front_side_path} and {back_side_path}")
    preview_id_card(front_side_path, back_side_path)

# Function to preview the ID card
def preview_id_card(front_side_path, back_side_path):
    preview_window = Toplevel(root)
    preview_window.title("ID Card Preview")

    # Display front side
    front_img = Image.open(front_side_path)
    front_img = front_img.resize((400, 250))  # Resize for preview
    front_img = ImageTk.PhotoImage(front_img)
    Label(preview_window, image=front_img).pack()
    Label(preview_window, text="Front Side").pack()

    # Display back side
    back_img = Image.open(back_side_path)
    back_img = back_img.resize((400, 250))  # Resize for preview
    back_img = ImageTk.PhotoImage(back_img)
    Label(preview_window, image=back_img).pack()
    Label(preview_window, text="Back Side").pack()

    # Add a button to print the ID card as PDF
    Button(preview_window, text="Print as PDF", command=lambda: print_pdf(front_side_path, back_side_path)).pack()

# Function to print the ID card as PDF
def print_pdf(front_side_path, back_side_path):
    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        return

    # Create a PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    front_img = Image.open(front_side_path)
    back_img = Image.open(back_side_path)

    # Draw front side on the PDF
    front_img_bytes = BytesIO()
    front_img.save(front_img_bytes, format="PNG")
    front_img_bytes.seek(0)
    c.drawImage(front_img_bytes, 50, 700, width=400, height=250)

    # Draw back side on the PDF
    back_img_bytes = BytesIO()
    back_img.save(back_img_bytes, format="PNG")
    back_img_bytes.seek(0)
    c.drawImage(back_img_bytes, 50, 400, width=400, height=250)

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

Button(root, text="Generate ID Card", command=generate_id_card).grid(row=3, column=1, pady=20)

root.mainloop()