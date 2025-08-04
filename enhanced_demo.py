#!/usr/bin/env python3
"""
Enhanced Virtual Keyboard Demo with Fingertip Visualization
Shows how fingertip lines and coordinates would appear with hand tracking
"""

import cv2
import numpy as np
import time
import math

class EnhancedVirtualKeyboard:
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
        self.current_key = None
        
        # Mouse simulation for hand tracking demonstration
        self.mouse_pos = (640, 360)  # Center of screen
        self.simulated_fingertips = []
        self.simulated_palm_points = []
        
    def simulate_hand_landmarks(self, mouse_x, mouse_y):
        """Simulate hand landmarks based on mouse position for demonstration."""
        # Simulate 5 fingertips relative to mouse position (index finger)
        self.simulated_fingertips = [
            (mouse_x - 60, mouse_y + 40, "Thumb"),    # Thumb
            (mouse_x, mouse_y, "Index"),              # Index (mouse position)
            (mouse_x + 20, mouse_y - 20, "Middle"),   # Middle
            (mouse_x + 40, mouse_y - 10, "Ring"),     # Ring
            (mouse_x + 60, mouse_y + 10, "Pinky")     # Pinky
        ]
        
        # Simulate palm landmarks
        self.simulated_palm_points = [
            (mouse_x - 30, mouse_y + 80, "Wrist"),
            (mouse_x - 10, mouse_y + 60, "Palm1"),
            (mouse_x + 10, mouse_y + 70, "Palm2"),
            (mouse_x + 30, mouse_y + 65, "Palm3"),
            (mouse_x, mouse_y + 50, "PalmCenter")
        ]
    
    def draw_simulated_hand_landmarks(self, frame):
        """Draw simulated hand landmarks with fingertip lines and coordinates."""
        if not self.simulated_fingertips:
            return frame
        
        # Draw connections between palm points
        for i in range(len(self.simulated_palm_points)-1):
            pt1 = self.simulated_palm_points[i][:2]
            pt2 = self.simulated_palm_points[i+1][:2]
            cv2.line(frame, pt1, pt2, (100, 100, 100), 2)
        
        # Draw fingertip indicators with coordinates
        for i, (x, y, name) in enumerate(self.simulated_fingertips):
            # Ensure coordinates are within frame bounds
            x = max(0, min(x, frame.shape[1]-1))
            y = max(0, min(y, frame.shape[0]-1))
            
            # Draw larger circle for fingertips
            cv2.circle(frame, (x, y), 8, (0, 255, 255), -1)  # Yellow filled circle
            cv2.circle(frame, (x, y), 12, (255, 0, 0), 2)    # Blue border
            
            # Draw lines from fingertips (extending outward)
            line_length = 40
            end_x = x + line_length
            end_y = y - line_length
            cv2.line(frame, (x, y), (end_x, end_y), (0, 255, 255), 3)
            
            # Display coordinates near fingertips
            coord_text = f"{name}: ({x},{y})"
            text_x = end_x + 5
            text_y = end_y
            
            # Add background for text readability
            text_size = cv2.getTextSize(coord_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            cv2.rectangle(frame, (text_x-2, text_y-text_size[1]-2), 
                         (text_x+text_size[0]+2, text_y+2), (0, 0, 0), -1)
            
            cv2.putText(frame, coord_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw palm landmarks with coordinates
        for x, y, name in self.simulated_palm_points:
            x = max(0, min(x, frame.shape[1]-1))
            y = max(0, min(y, frame.shape[0]-1))
            
            # Draw smaller circles for palm points
            cv2.circle(frame, (x, y), 4, (255, 255, 0), -1)  # Cyan circles
            
            # Display palm coordinates (smaller text)
            palm_text = f"{name}:({x},{y})"
            cv2.putText(frame, palm_text, (x+10, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
        
        # Draw distance line between thumb and index finger
        if len(self.simulated_fingertips) >= 2:
            thumb_pos = self.simulated_fingertips[0][:2]
            index_pos = self.simulated_fingertips[1][:2]
            
            # Draw line between thumb and index
            cv2.line(frame, thumb_pos, index_pos, (255, 0, 255), 2)
            
            # Calculate and display distance
            distance = math.sqrt((thumb_pos[0] - index_pos[0])**2 + 
                               (thumb_pos[1] - index_pos[1])**2)
            
            mid_x = (thumb_pos[0] + index_pos[0]) // 2
            mid_y = (thumb_pos[1] + index_pos[1]) // 2
            cv2.putText(frame, f"Distance: {distance:.1f}px", (mid_x, mid_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        return frame
    
    def draw_keyboard(self, frame):
        """Draw the virtual keyboard on the frame with transparent background."""
        # Create overlay for transparency
        overlay = frame.copy()
        
        for row_idx, row in enumerate(self.keyboard_layout):
            for col_idx, key in enumerate(row):
                # Calculate key position
                x = self.keyboard_start_x + col_idx * (self.key_width + self.key_margin)
                y = self.keyboard_start_y + row_idx * (self.key_height + self.key_margin)
                
                # Determine key color
                color = self.active_key_color if key == self.current_key else self.key_color
                
                # Draw key rectangle on overlay for transparency
                cv2.rectangle(overlay, (x, y), (x + self.key_width, y + self.key_height), 
                             color, -1)
                
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
        cv2.rectangle(text_bg, (30, 10), (frame.shape[1]-30, 130), (0, 0, 0), -1)
        cv2.addWeighted(text_bg, 0.8, frame, 0.2, 0, frame)
        
        # Display final typed text prominently
        cv2.putText(frame, "FINAL TEXT:", (50, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Show the actual typed text in a larger font
        display_text = self.typed_text if self.typed_text else "Move mouse to simulate hand tracking..."
        cv2.putText(frame, display_text, (50, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        # Draw instructions
        instructions = [
            "DEMO: Mouse simulates hand tracking",
            "Yellow lines = fingertips with coordinates",
            "Cyan dots = palm landmarks", 
            "Purple line = thumb-index distance",
            "Click keys to type - Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = 150 + i * 22
            cv2.putText(frame, instruction, (50, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        
        # Draw mouse position as current index finger
        cv2.putText(frame, f"Mouse (Index): ({self.mouse_pos[0]},{self.mouse_pos[1]})", 
                   (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
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
        """Handle mouse movement and clicks."""
        self.mouse_pos = (x, y)
        
        # Update current key based on mouse position
        self.current_key = self.get_key_at_position(x, y)
        
        # Handle mouse clicks for typing
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
        print("Starting Enhanced Virtual Keyboard Demo...")
        print("OpenCV version:", cv2.__version__)
        print("Move mouse to simulate hand tracking!")
        print("Click on keys to type - Press 'q' to quit")
        
        # Create OpenCV window and set mouse callback
        cv2.namedWindow('Enhanced Virtual Keyboard Demo', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('Enhanced Virtual Keyboard Demo', self.mouse_callback)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Simulate hand landmarks based on mouse position
            self.simulate_hand_landmarks(self.mouse_pos[0], self.mouse_pos[1])
            
            # Draw simulated hand landmarks with coordinates
            frame = self.draw_simulated_hand_landmarks(frame)
            
            # Draw virtual keyboard
            frame = self.draw_keyboard(frame)
            
            # Draw UI elements
            frame = self.draw_ui(frame)
            
            # Add demo info
            cv2.putText(frame, "DEMO MODE - Mouse simulates MediaPipe hand tracking", 
                       (frame.shape[1]-500, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # Display frame
            cv2.imshow('Enhanced Virtual Keyboard Demo', frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quit key pressed")
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("\n" + "="*60)
        print("ENHANCED VIRTUAL KEYBOARD DEMO SESSION COMPLETE")
        print("="*60)
        print(f"FINAL TYPED TEXT: '{self.typed_text}'")
        print(f"Total Characters: {len(self.typed_text)}")
        print("="*60)

if __name__ == "__main__":
    # Create and run the enhanced virtual keyboard demo
    keyboard_demo = EnhancedVirtualKeyboard()
    keyboard_demo.run()
