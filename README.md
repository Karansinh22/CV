# CV Text Reader with Speech Output

A real-time text detection and speech synthesis tool that captures video from your webcam, detects text using Tesseract OCR, and reads it aloud. It can also alert you when a specific target word is detected.

## Features

- Real-time text detection from camera feed
- Text-to-speech output
- Target word detection with visual and audio alerts
- Logging of detected text to CSV
- Cross-platform support (Windows, macOS, Linux)
- Configurable settings for better OCR accuracy

## Prerequisites

- Python 3.6 or higher
- Tesseract OCR engine
- A working webcam

## Installation

### 1. Install Tesseract OCR

**Windows:**
1. Download the installer from [UB Mannheim's Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer
3. Add Tesseract to your system PATH (usually `C:\Program Files\Tesseract-OCR\`)
4. Note: You'll need to update the path in the script if Tesseract is installed in a different location

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

### 2. Install Python Dependencies

```bash
pip install opencv-python pytesseract pyttsx3 pillow
```

## Usage

### Basic Usage

```bash
python cv_text_reader.py --target "your_target_word"
```

### Options

- `--target`: The word to search for (required)
- `--log`: Path to the log file (default: 'text_detection_log.csv')

Example:
```bash
python cv_text_reader.py --target "hello" --log "my_logs/detection.csv"
```

### Controls

- Press 'q' to quit the application

## How It Works

1. The application captures video from your default camera
2. Each frame is processed to detect text using Tesseract OCR
3. Detected text is displayed on screen with bounding boxes
4. The application checks if the target word appears in the detected text
5. If found, it highlights the word in red and speaks an alert
6. All detections are logged to a CSV file with timestamps

## Improving Accuracy

For better text detection, ensure:
1. Good lighting conditions
2. The text is clear and not too small
3. The camera is steady

You can also uncomment and adjust the image preprocessing settings in the `preprocess_image` method for better results in different conditions.

## Logging

The application logs all detections to a CSV file with the following columns:
- `timestamp`: When the detection occurred
- `detected_text`: The text that was detected
- `target_found`: Whether the target word was found

## Troubleshooting

1. **Tesseract not found**:
   - Make sure Tesseract is installed and in your system PATH
   - On Windows, you may need to update the path in the script

2. **No text is being detected**:
   - Check that the text is clear and well-lit
   - Try adjusting the camera position
   - Uncomment and adjust the image preprocessing settings

3. **TTS not working**:
   - On Linux, you may need to install espeak: `sudo apt install espeak`
   - On Windows, make sure you have a TTS engine installed

## License

This project is open source and available under the MIT License.
