import os
import random
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime, timedelta
import barcode
from barcode.writer import ImageWriter

# Australian standard card size in pixels (85.6 mm x 54 mm at 300 DPI)
CARD_WIDTH = 1010  # 85.6 mm * 300 DPI / 25.4 mm/inch
CARD_HEIGHT = 637   # 54 mm * 300 DPI / 25.4 mm/inch

# Function to generate a 9-digit unique ID
def generate_id():
    return ''.join(random.choices('0123456789', k=9))

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

# Function to generate a barcode with a transparent background
def generate_barcode(id_number):
    # Generate a Code39 barcode
    code = barcode.get('code39', id_number, writer=ImageWriter())
    barcode_path = f"barcode_{id_number}"
    code.save(barcode_path)  # Save the barcode as an image

    # Open the barcode image and make the background transparent
    barcode_img = Image.open(f"{barcode_path}.png")
    barcode_img = barcode_img.convert("RGBA")  # Convert to RGBA for transparency
    data = barcode_img.getdata()

    # Make white pixels transparent
    new_data = []
    for item in data:
        if item[:3] == (255, 255, 255):  # Check if the pixel is white
            new_data.append((255, 255, 255, 0))  # Make it transparent
        else:
            new_data.append((255, 255, 255, 255))  # Make black pixels white

    barcode_img.putdata(new_data)
    os.remove(f"{barcode_path}.png")  # Delete the temporary barcode file
    return barcode_img

# Function to create the ID card (front side)
def create_id_card_front(full_name, dob, position, id_number, address, photo_path, issue_date, validity_date):
    # Load front side background image
    background = Image.open("images/front_background.jpg")  # Replace with your front background image
    background = background.resize((CARD_WIDTH, CARD_HEIGHT))  # Resize to card size
    background = round_corners(background, radius=30)  # Apply rounded corners to the background

    # Load user photo
    user_photo = Image.open(photo_path).resize((200, 200))
    user_photo = round_corners(user_photo, radius=20)  # Apply rounded corners to the photo

    # Paste user photo onto the background
    background.paste(user_photo, (50, 50), user_photo)

    # Draw text on the image
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("arial.ttf", 28)  # Use a custom font
    draw.text((300, 60), f"Name: {full_name}", fill="white", font=font)
    draw.text((300, 100), f"DOB: {dob}", fill="white", font=font)  # Add date of birth
    draw.text((300, 140), f"Position: {position}", fill="white", font=font)  # Add position
    draw.text((300, 180), f"ID: {id_number}", fill="white", font=font)
    draw.text((300, 220), f"Address: {address}", fill="white", font=font)
    draw.text((50, 570), f"Issue Date: {issue_date}", fill="white", font=font)
    draw.text((650, 570), f"Valid Until: {validity_date}", fill="white", font=font)

    # Generate and add barcode (under the photo)
    barcode_img = generate_barcode(id_number)
    barcode_img = barcode_img.resize((200, 50))  # Resize barcode
    background.paste(barcode_img, (50, 300), barcode_img)  # Place barcode under the photo

    return background

# Function to create the ID card (back side)
def create_id_card_back():
    # Load back side background image
    background = Image.open("images/back_background.jpg")  # Replace with your back background image
    background = background.resize((CARD_WIDTH, CARD_HEIGHT))  # Resize to card size
    background = round_corners(background, radius=30)  # Apply rounded corners to the background

    draw = ImageDraw.Draw(background)

      # Add magnetic strip (black rectangle at the top)
    magnetic_strip_height = 100
    draw.rectangle([(0, 50), (CARD_WIDTH, magnetic_strip_height)], fill="black")

    # Add text to the magnetic strip
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text((50, 15), "Magnetic Strip (For Digital Data Storage)", fill="white", font=font)

     # Add back side content below the magnetic strip
    font = ImageFont.truetype("arial.ttf", 28)
    draw.text((50, 120), "KHMER DEMOCRACY ORGANIZATION(KDO) INC.", fill="white", font=font)
    draw.text((50, 170), "Terms of Use:", fill="white", font=font)
    draw.text((50, 220), "1. This card is property of the KDO.", fill="white", font=font)
    draw.text((50, 270), "2. If found, please return to:", fill="white", font=font)
    draw.text((50, 320), "HQ Office at:", fill="white", font=font)
    draw.text((50, 370), "6 Temple CT,Noble Park,VIC 3174, Australia.", fill="white", font=font)
    draw.text((50, 500), "Contact: +61 0395444950", fill="white", font=font)
    draw.text((50, 570), "Website: kdo.org.au", fill="white", font=font)
    draw.text((650, 570), "ABN: 43 435 683 952", fill="white", font=font)

    return background


# Function to generate the ID card
def generate_id_card():
    # Get user inputs
    full_name = entry_name.get()
    dob = entry_dob.get()  # Get date of birth
    position = entry_position.get()  # Get member position
    address = entry_address.get()
    photo_path = entry_photo.get()

    if not full_name or not dob or not position or not address or not photo_path:
        messagebox.showerror("Error", "Please fill all fields and select a photo.")
        return

    # Generate ID, validity date, and issue date
    id_number = generate_id()
    issue_date = datetime.now().strftime("%d-%m-%Y")
    validity_date = (datetime.now() + timedelta(days=1825)).strftime("%d-%m-%Y")

    # Create front and back sides of the ID card
    front_side = create_id_card_front(full_name, dob, position, id_number, address, photo_path, issue_date, validity_date)
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
    front_img = front_img.resize((CARD_WIDTH // 2, CARD_HEIGHT // 2))  # Resize for preview
    front_img = ImageTk.PhotoImage(front_img)  # Use ImageTk to display in Tkinter
    Label(preview_window, image=front_img).pack()
    Label(preview_window, text="Front Side").pack()

    # Display back side
    back_img = Image.open(back_side_path)
    back_img = back_img.resize((CARD_WIDTH // 2, CARD_HEIGHT // 2))  # Resize for preview
    back_img = ImageTk.PhotoImage(back_img)  # Use ImageTk to display in Tkinter
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
    c.drawImage(front_img_bytes, 50, 700, width=CARD_WIDTH // 2, height=CARD_HEIGHT // 2)

    # Draw back side on the PDF
    back_img_bytes = BytesIO()
    back_img.save(back_img_bytes, format="PNG")
    back_img_bytes.seek(0)
    c.drawImage(back_img_bytes, 50, 400, width=CARD_WIDTH // 2, height=CARD_HEIGHT // 2)

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

Label(root, text="Date of Birth (DOB):").grid(row=1, column=0, padx=10, pady=10)  # Add DOB field
entry_dob = Entry(root, width=30)
entry_dob.grid(row=1, column=1, padx=10, pady=10)

Label(root, text="Position:").grid(row=2, column=0, padx=10, pady=10)  # Add position field
entry_position = Entry(root, width=30)
entry_position.grid(row=2, column=1, padx=10, pady=10)

Label(root, text="Address:").grid(row=3, column=0, padx=10, pady=10)
entry_address = Entry(root, width=30)
entry_address.grid(row=3, column=1, padx=10, pady=10)

Label(root, text="Photo:").grid(row=4, column=0, padx=10, pady=10)
entry_photo = Entry(root, width=30)
entry_photo.grid(row=4, column=1, padx=10, pady=10)
Button(root, text="Browse", command=select_photo).grid(row=4, column=2, padx=10, pady=10)

Button(root, text="Generate ID Card", command=generate_id_card).grid(row=5, column=1, pady=20)

root.mainloop()
