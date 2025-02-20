import os
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont, ImageOps
import barcode
from barcode.writer import ImageWriter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/id_cards'

# Australian standard card size in pixels (85.6 mm x 54 mm at 300 DPI)
CARD_WIDTH = 1010  # 85.6 mm * 300 DPI / 25.4 mm/inch
CARD_HEIGHT = 637   # 54 mm * 300 DPI / 25.4 mm/inch

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

# Function to generate a barcode with a white foreground and transparent background
def generate_barcode(id_number):
    code = barcode.get('code39', id_number, writer=ImageWriter())
    barcode_path = f"static/id_cards/barcode_{id_number}"
    code.save(barcode_path)  # Save the barcode as an image

    # Open the barcode image and make the background transparent
    barcode_img = Image.open(f"{barcode_path}.png")
    barcode_img = barcode_img.convert("RGBA")  # Convert to RGBA for transparency
    data = barcode_img.getdata()

    # Make white pixels transparent and black pixels white
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
    background = Image.open("static/images/front_background.jpg")  # Replace with your front background image
    background = background.resize((CARD_WIDTH, CARD_HEIGHT))  # Resize to card size
    background = round_corners(background, radius=30)  # Apply rounded corners to the background

    # Load user photo
    user_photo = Image.open(photo_path).resize((200, 200))
    user_photo = round_corners(user_photo, radius=20)  # Apply rounded corners to the photo

    # Paste user photo onto the background
    background.paste(user_photo, (50, 50), user_photo)

    # Draw text on the image
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("arial.ttf", 30)  # Use a custom font
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

    # Save the front side image
    front_side_path = f"static/id_cards/id_card_front_{id_number}.png"
    background.save(front_side_path)
    return front_side_path

# Function to create the ID card (back side)
def create_id_card_back(id_number):
    # Load back side background image
    background = Image.open("static/images/back_background.jpg")  # Replace with your back background image
    background = background.resize((CARD_WIDTH, CARD_HEIGHT))  # Resize to card size
    background = round_corners(background, radius=30)  # Apply rounded corners to the background

    draw = ImageDraw.Draw(background)

    # Add magnetic strip (black rectangle at the top)
    magnetic_strip_height = 50
    draw.rectangle([(0, 0), (CARD_WIDTH, magnetic_strip_height)], fill="black")

    # Add text to the magnetic strip
    font = ImageFont.truetype("arial.ttf", 20)
    draw.text((10, 15), "Magnetic Strip (For Digital Data Storage)", fill="white", font=font)

    # Add back side content below the magnetic strip
    font = ImageFont.truetype("arial.ttf", 30)
    draw.text((50, 70), "KHMER DEMOCRACY ORGANIZATION(KDO) INC.", fill="white", font=font)
    draw.text((50, 120), "Terms of Use:", fill="white", font=font)
    draw.text((50, 170), "1. This card is property of the KDO.", fill="white", font=font)
    draw.text((50, 220), "2. If found, please return to:", fill="white", font=font)
    draw.text((50, 270), "Lost & Return Address:", fill="white", font=font)
    draw.text((50, 320), "6 Temple CT Noble Park St, Melbourne, VIC 3174", fill="white", font=font)
    draw.text((50, 370), "Contact: +61 0395444950", fill="white", font=font)
    draw.text((50, 570), "Website: kdo.org.au", fill="white", font=font)
    draw.text((650, 570), "ABN: 43 435 683 952", fill="white", font=font)

    # Save the back side image
    back_side_path = f"static/id_cards/id_card_back_{id_number}.png"
    background.save(back_side_path)
    return back_side_path

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get form data
        full_name = request.form.get("full_name")
        dob = request.form.get("dob")
        position = request.form.get("position")
        address = request.form.get("address")
        photo = request.files.get("photo")

        if not full_name or not dob or not position or not address or not photo:
            return "Please fill all fields and upload a photo."

        # Save the uploaded photo
        photo_path = f"static/id_cards/{photo.filename}"
        photo.save(photo_path)

        # Generate ID, validity date, and issue date
        id_number = generate_id()
        issue_date = datetime.now().strftime("%Y-%m-%d")
        validity_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

        # Create front and back sides of the ID card
        front_side_path = create_id_card_front(full_name, dob, position, id_number, address, photo_path, issue_date, validity_date)
        back_side_path = create_id_card_back(id_number)

        # Redirect to the preview page
        return redirect(url_for("preview", front=front_side_path, back=back_side_path))

    return render_template("index.html")

@app.route("/preview")
def preview():
    front_side_path = request.args.get("front")
    back_side_path = request.args.get("back")
    return render_template("preview.html", front=front_side_path, back=back_side_path)

@app.route("/download/<path:filename>")
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
