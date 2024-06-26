import qrcode

# Define the URL you want to encode in the QR code
url = "https://www.example.com"

# Create a QR code instance
qr = qrcode.QRCode(
    version=1,  # QR code version (1-40, higher is denser)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
    box_size=10,  # Size of each box in the QR code
    border=4,  # Border size around the QR code
)

# Add the data (URL) to the QR code
qr.add_data(url)
qr.make(fit=True)

# Create an image of the QR code
img = qr.make_image(fill_color="black", back_color="white")

# Save the QR code as an image file
img.save("qr_code.png")

# Display the QR code (optional)
img.show()