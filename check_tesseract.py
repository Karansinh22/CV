import os

def find_tesseract():
    # Common installation paths for Tesseract on Windows
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%ProgramFiles%\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Tesseract-OCR\tesseract.exe")
    ]
    
    print("Checking for Tesseract installation...")
    found = False
    for path in common_paths:
        if os.path.isfile(path):
            print(f"✅ Found Tesseract at: {path}")
            found = True
    
    if not found:
        print("❌ Tesseract not found in common locations.")
        print("\nPlease install Tesseract from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
        print("\nAfter installation, make sure to add Tesseract to your system PATH.")

if __name__ == "__main__":
    find_tesseract()
