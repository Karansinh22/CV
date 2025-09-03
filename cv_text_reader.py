#!/usr/bin/env python3
"""
CV Text Reader with Speech Output
--------------------------------
A real-time text detection and speech synthesis tool that:
1. Captures video from the default camera
2. Detects text using Tesseract OCR
3. Speaks detected text using pyttsx3
4. Alerts when a target word is found
"""

import cv2
import pytesseract
import pyttsx3
import re
import csv
import sys
import os
import subprocess
from datetime import datetime
import argparse

# Set the path to Tesseract executable
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Verify Tesseract is accessible
print(f"Tesseract path set to: {TESSERACT_PATH}")
try:
    # Try to get Tesseract version using subprocess
    result = subprocess.run(
        [TESSERACT_PATH, "--version"],
        capture_output=True,
        text=True,
        check=True
    )
    print("Tesseract version check:")
    print(result.stdout.strip())
except Exception as e:
    print(f"Error accessing Tesseract: {e}")
    print("Please ensure Tesseract is installed at the specified path.")
    sys.exit(1)

print("All dependencies verified. Starting CV Text Reader...")

class CVTextReader:
    def __init__(self, target_word: str, log_file: str = 'text_detection_log.csv'):
        """Initialize the CV Text Reader.
        
        Args:
            target_word: The word to search for in the detected text
            log_file: Path to the CSV log file
        """
        self.target_word = target_word.lower()
        self.log_file = log_file
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.target_found = False
        self.setup_log_file()

    def setup_log_file(self):
        """Initialize the log file with headers if it doesn't exist."""
        try:
            with open(self.log_file, 'x', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'detected_text', 'target_found'])
        except FileExistsError:
            pass  # File already exists, no need to create

    def log_detection(self, text: str, target_found: bool):
        """Log the detection results to a CSV file.
        
        Args:
            text: The detected text
            target_found: Whether the target word was found
        """
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                text,
                str(target_found)
            ])

    def preprocess_image(self, image):
        """Preprocess the image to improve OCR accuracy.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Preprocessed grayscale image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        # You can experiment with different thresholding methods
        # _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply dilation and erosion to remove noise
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        
        return gray

    def detect_text(self, image):
        """Detect text in the given image using Tesseract OCR.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Tuple of (detected_text, bounding_boxes)
        """
        # Preprocess the image
        processed = self.preprocess_image(image)
        
        # Use Tesseract to detect text and get bounding boxes
        data = pytesseract.image_to_data(
            processed, 
            output_type=pytesseract.Output.DICT,
            config='--psm 6'  # Assume a single uniform block of text
        )
        
        # Combine all detected text
        detected_text = ' '.join([word for word in data['text'] if word.strip()])
        
        # Get bounding boxes for each word
        boxes = []
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # Only consider confident detections
                (x, y, w, h) = (
                    data['left'][i], 
                    data['top'][i], 
                    data['width'][i], 
                    data['height'][i]
                )
                text = data['text'][i].strip()
                if text:  # Only add non-empty text
                    boxes.append((x, y, x + w, y + h, text))
        
        return detected_text, boxes

    def check_target_word(self, text: str) -> bool:
        """Check if the target word is in the detected text.
        
        Args:
            text: The text to search in
            
        Returns:
            True if target word is found, False otherwise
        """
        # Use word boundaries to match whole words only
        pattern = fr'\b{re.escape(self.target_word)}\b'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def speak(self, text: str):
        """Speak the given text using TTS.
        
        Args:
            text: The text to speak
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error with TTS: {e}")

    def run(self):
        """Run the main application loop."""
        # Initialize video capture
        cap = cv2.VideoCapture(0)
        
        # Set a reasonable resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        last_spoken = ""
        last_alert_time = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Flip the frame horizontally for a more intuitive mirror-like display
                frame = cv2.flip(frame, 1)
                
                # Make a copy for display
                display_frame = frame.copy()
                
                # Detect text in the frame
                detected_text, boxes = self.detect_text(frame)
                
                # Check if target word is in the detected text
                target_found = self.check_target_word(detected_text)
                
                # Log the detection
                self.log_detection(detected_text, target_found)
                
                # Draw bounding boxes and highlight target word
                for (x1, y1, x2, y2, text) in boxes:
                    # Check if this is the target word
                    is_target = self.check_target_word(text)
                    
                    # Draw the bounding box
                    color = (0, 0, 255) if is_target else (0, 255, 0)  # Red for target, green for others
                    thickness = 3 if is_target else 1
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, thickness)
                    
                    # Add the text above the box
                    cv2.putText(display_frame, text, (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Show the detected text
                cv2.putText(display_frame, f"Detected: {detected_text[:50]}{'...' if len(detected_text) > 50 else ''}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Show status
                status = f"Target '{self.target_word}' found!" if target_found else f"Looking for: {self.target_word}"
                cv2.putText(display_frame, status, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if target_found else (0, 255, 0), 2)
                
                # Alert if target word is found
                current_time = cv2.getTickCount()
                if target_found and (current_time - last_alert_time) / cv2.getTickFrequency() > 5:  # 5 seconds cooldown
                    self.speak(f"Target word {self.target_word} found!")
                    last_alert_time = current_time
                
                # Display the resulting frame
                cv2.imshow('CV Text Reader', display_frame)
                
                # Break the loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        finally:
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            self.engine.stop()

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='CV Text Reader with Speech Output')
    parser.add_argument('--target', type=str, required=True,
                        help='The target word to search for')
    parser.add_argument('--log', type=str, default='text_detection_log.csv',
                        help='Path to the log file (CSV format)')
    
    args = parser.parse_args()
    
    print(f"Starting CV Text Reader. Looking for target word: '{args.target}'")
    print("Press 'q' to quit.")
    
    # Create and run the application
    app = CVTextReader(target_word=args.target, log_file=args.log)
    app.run()

if __name__ == "__main__":
    main()
