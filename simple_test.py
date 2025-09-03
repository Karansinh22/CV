print("Python is working!")
try:
    import cv2
    print("OpenCV version:", cv2.__version__)
    import pytesseract
    print("pytesseract version:", pytesseract.get_tesseract_version())
    import pyttsx3
    print("pyttsx3 imported successfully")
except Exception as e:
    print("Error:", str(e))
