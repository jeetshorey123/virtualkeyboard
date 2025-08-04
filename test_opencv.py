#!/usr/bin/env python3
"""
Simple Virtual Keyboard Test - OpenCV Only
Test OpenCV camera functionality and virtual keyboard display
"""

import cv2
import numpy as np
import time

class SimpleVirtualKeyboard:
    def __init__(self):
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Check if camera opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            exit()
        else:
            print("Camera opened successfully")
        
        # Keyboard layout
        self.keyboard_layout = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
            ['SPACE', 'BACK']
        ]
        
        # Key properties - smaller keys with more spacing
        self.key_width = 50
        self.key_height = 50
        self.key_margin = 20
        self.keyboard_start_x = 150
        self.keyboard_start_y = 450
        
        # Colors - semi-transparent
        self.key_color = (50, 50, 50)
        self.key_border_color = (255, 255, 255)
        self.key_text_color = (255, 255, 255)
        self.active_key_color = (0, 255, 0)
        self.alpha = 0.3  # Transparency level
        
        # Text display
        self.typed_text = ""
        
    def draw_keyboard(self, frame):
        """Draw the virtual keyboard on the frame with transparent background."""
        # Create overlay for transparency
        overlay = frame.copy()
        
        for row_idx, row in enumerate(self.keyboard_layout):
            for col_idx, key in enumerate(row):
                # Calculate key position
                x = self.keyboard_start_x + col_idx * (self.key_width + self.key_margin)
                y = self.keyboard_start_y + row_idx * (self.key_height + self.key_margin)
                
                # Draw key rectangle on overlay for transparency
                cv2.rectangle(overlay, (x, y), (x + self.key_width, y + self.key_height), 
                             self.key_color, -1)
                
                # Draw key border (always visible)
                cv2.rectangle(frame, (x, y), (x + self.key_width, y + self.key_height), 
                             self.key_border_color, 2)
                
                # Draw key text
                font_scale = 0.5 if len(key) > 1 else 0.7
                text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
                text_x = x + (self.key_width - text_size[0]) // 2
                text_y = y + (self.key_height + text_size[1]) // 2
                cv2.putText(frame, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                           font_scale, self.key_text_color, 2)
        
        # Apply transparency to key backgrounds
        cv2.addWeighted(overlay, self.alpha, frame, 1 - self.alpha, 0, frame)
        
        return frame
    
    def draw_ui(self, frame):
        """Draw UI elements like typed text and instructions."""
        # Draw typed text with larger, more prominent display
        text_bg = frame.copy()
        cv2.rectangle(text_bg, (30, 10), (frame.shape[1]-30, 120), (0, 0, 0), -1)
        cv2.addWeighted(text_bg, 0.8, frame, 0.2, 0, frame)
        
        # Display final typed text prominently
        cv2.putText(frame, "FINAL TEXT:", (50, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Show the actual typed text in a larger font
        display_text = self.typed_text if self.typed_text else "..."
        cv2.putText(frame, display_text, (50, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        # Draw instructions
        instructions = [
            "Small Transparent Keys - Click to Type",
            "Better visibility for finger tracking",
            "Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = 140 + i * 25
            cv2.putText(frame, instruction, (50, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw character count
        cv2.putText(frame, f"Characters: {len(self.typed_text)}", (50, 230), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        return frame
    
    def get_key_at_position(self, x, y):
        """Get the key at the given position."""
        for row_idx, row in enumerate(self.keyboard_layout):
            for col_idx, key in enumerate(row):
                key_x = self.keyboard_start_x + col_idx * (self.key_width + self.key_margin)
                key_y = self.keyboard_start_y + row_idx * (self.key_height + self.key_margin)
                
                if (key_x <= x <= key_x + self.key_width and 
                    key_y <= y <= key_y + self.key_height):
                    return key
        return None
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks on virtual keyboard."""
        if event == cv2.EVENT_LBUTTONDOWN:
            key = self.get_key_at_position(x, y)
            if key:
                if key == 'SPACE':
                    self.typed_text += ' '
                    print("Typed: SPACE")
                    print(f"FINAL TEXT: '{self.typed_text}'")
                elif key == 'BACK':
                    if self.typed_text:
                        self.typed_text = self.typed_text[:-1]
                        print("Typed: BACKSPACE")
                        print(f"FINAL TEXT: '{self.typed_text}'")
                else:
                    self.typed_text += key
                    print(f"Typed: {key}")
                    print(f"FINAL TEXT: '{self.typed_text}'")
    
    def run(self):
        """Main application loop."""
        print("Starting Simple Virtual Keyboard Test...")
        print("OpenCV version:", cv2.__version__)
        print("Click on keys to type!")
        print("Press 'q' to quit")
        
        # Create OpenCV window and set mouse callback
        cv2.namedWindow('Virtual Keyboard Test', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('Virtual Keyboard Test', self.mouse_callback)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame from camera")
                break
            
            # Get actual frame dimensions
            height, width = frame.shape[:2]
            print(f"Frame size: {width}x{height}", end='\r')  # Real-time update
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Draw virtual keyboard
            frame = self.draw_keyboard(frame)
            
            # Draw UI elements
            frame = self.draw_ui(frame)
            
            # Add frame info
            cv2.putText(frame, f"Frame: {width}x{height}", (width-200, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            
            # Display frame
            cv2.imshow('Virtual Keyboard Test', frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nQuit key pressed")
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("\n" + "="*50)
        print("VIRTUAL KEYBOARD TEST SESSION COMPLETE")
        print("="*50)
        print(f"FINAL TYPED TEXT: '{self.typed_text}'")
        print(f"Total Characters: {len(self.typed_text)}")
        print("="*50)

if __name__ == "__main__":
    # Create and run the simple virtual keyboard test
    keyboard_test = SimpleVirtualKeyboard()
    keyboard_test.run()
