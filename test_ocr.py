import cv2
import pytesseract
import numpy as np

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Create a simple image with text
image = np.ones((100, 400, 3), dtype=np.uint8) * 255  # White background
cv2.putText(image, 'Hello, Tesseract!', (50, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

# Save the image
cv2.imwrite('test_image.png', image)
print("Created test_image.png")

# Try to read the text
try:
    text = pytesseract.image_to_string(image)
    print("Detected text:", text.strip())
except Exception as e:
    print("Error during OCR:", str(e))
