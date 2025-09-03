#!/usr/bin/env python3
#python cv_text_reader.py --target "hello" to run the program
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

    def save_screenshot(self, display_frame, boxes, target_word_boxes):
        """Save the current display frame as a screenshot with all annotations."""
        # Create a copy of the frame to avoid modifying the original
        screenshot = display_frame.copy()
        
        # Add a semi-transparent overlay for better text visibility
        overlay = screenshot.copy()
        cv2.rectangle(overlay, (0, 0), (screenshot.shape[1], 50), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, screenshot, 0.4, 0, screenshot)
        
        # Add detection header
        cv2.putText(screenshot, f"DETECTED: '{self.target_word.upper()}'", 
                   (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Highlight all target word boxes in red
        for (x1, y1, x2, y2, text) in target_word_boxes:
            # Draw a red rectangle around the target word
            cv2.rectangle(screenshot, (x1-5, y1-5), (x2+5, y2+5), (0, 0, 255), 2)
            # Add a label above the box
            cv2.putText(screenshot, f"'{text}' found!", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Add timestamp at the bottom
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(screenshot, f"Detected at: {timestamp}", 
                   (20, screenshot.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Save the enhanced screenshot
        filename = f'detected_{self.target_word}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        cv2.imwrite(filename, screenshot)
        print(f"\nScreenshot saved as: {filename}")
        return filename

    def run(self):
        """Run the main application loop."""
        # Initialize video capture
        cap = cv2.VideoCapture(0)
        
        # Set a reasonable resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        last_spoken = ""
        last_alert_time = 0
        target_detected = False
        
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
                
                # If target found and not already detected
                if target_found and not target_detected:
                    target_detected = True
                    # Get all boxes that contain the target word
                    target_boxes = [box for box in boxes if self.check_target_word(box[4])]
                    
                    # Save the screenshot with enhanced annotations
                    screenshot_path = self.save_screenshot(display_frame, boxes, target_boxes)
                    print(f"Target word '{self.target_word}' detected! Screenshot saved as {screenshot_path}")
                    self.speak(f"Found {self.target_word}! Screenshot saved.")
                    
                    # Create a final display frame with larger text for visibility
                    final_display = display_frame.copy()
                    h, w = final_display.shape[:2]
                    
                    # Add a semi-transparent overlay
                    overlay = final_display.copy()
                    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
                    cv2.addWeighted(overlay, 0.7, final_display, 0.3, 0, final_display)
                    
                    # Add large detection text
                    text = f"DETECTED: '{self.target_word.upper()}'"
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
                    text_x = (w - text_size[0]) // 2
                    text_y = (h + text_size[1]) // 2
                    
                    cv2.putText(final_display, text, 
                               (text_x, text_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4, cv2.LINE_AA)
                    
                    # Show the final frame with detection for 3 seconds
                    cv2.imshow('CV Text Reader', final_display)
                    cv2.waitKey(3000)
                    
                    # Release the camera and close all windows
                    cap.release()
                    cv2.destroyAllWindows()
                    return  # Exit the run method
                    
                    # Draw a big green border around the frame
                    cv2.rectangle(display_frame, (10, 10), (frame.shape[1]-10, frame.shape[0]-10), (0, 255, 0), 20)
                    cv2.putText(display_frame, f"FOUND: {self.target_word.upper()}", 
                               (frame.shape[1]//4, frame.shape[0]//2), 
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4, cv2.LINE_AA)
                
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
                
                # Show the frame
                cv2.imshow('CV Text Reader', display_frame)
                
                # Exit on 'q' key press or if target was detected
                if cv2.waitKey(1) & 0xFF == ord('q') or target_detected:
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
