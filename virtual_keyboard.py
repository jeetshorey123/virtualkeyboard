#!/usr/bin/env python3
"""
Virtual Keyboard using MediaPipe Hand Tracking
A computer vision-based virtual keyboard that recognizes finger gestures
to simulate keyboard input when index finger touches thumb.
"""

import cv2
import mediapipe as mp
import numpy as np
import math
import time
from typing import Optional, Tuple, List
import pyautogui

class VirtualKeyboard:
    def __init__(self):
        # Initialize MediaPipe hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
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
            ['SPACE', 'BACK']  # Added special keys
        ]
        
        # Key properties - smaller keys with more spacing
        self.key_width = 50
        self.key_height = 50
        self.key_margin = 20
        self.keyboard_start_x = 150
        self.keyboard_start_y = 450
        
        # Gesture detection
        self.touch_threshold = 30  # Distance threshold for finger touch
        self.last_key_time = 0
        self.key_press_delay = 0.5  # Minimum time between key presses
        
        # Text display
        self.typed_text = ""
        self.current_key = None
        
        # Colors - semi-transparent backgrounds
        self.key_color = (50, 50, 50)
        self.key_border_color = (255, 255, 255)
        self.key_text_color = (255, 255, 255)
        self.active_key_color = (0, 255, 0)
        self.alpha = 0.3  # Transparency level
        
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def is_finger_touching_thumb(self, landmarks) -> bool:
        """
        Detect if index finger tip is touching thumb tip.
        Returns True if the distance is below the threshold.
        """
        # Get thumb tip (landmark 4) and index finger tip (landmark 8)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Get actual frame dimensions
        ret, temp_frame = self.cap.read()
        if ret:
            h, w = temp_frame.shape[:2]
        else:
            h, w = 720, 1280  # fallback
        
        thumb_pos = (thumb_tip.x * w, thumb_tip.y * h)
        index_pos = (index_tip.x * w, index_tip.y * h)
        
        # Calculate distance
        distance = self.calculate_distance(thumb_pos, index_pos)
        is_touching = distance < self.touch_threshold
        if is_touching:
            print(f"Finger touch detected! Distance: {distance:.2f}")
        return is_touching
    
    def get_index_finger_position(self, landmarks) -> Tuple[int, int]:
        """Get the pixel position of the index finger tip."""
        index_tip = landmarks[8]
        # Get actual frame dimensions from the camera
        ret, temp_frame = self.cap.read()
        if ret:
            h, w = temp_frame.shape[:2]
        else:
            h, w = 720, 1280  # fallback
        return (int(index_tip.x * w), int(index_tip.y * h))
    
    def draw_hand_landmarks_with_coordinates(self, frame, hand_landmarks):
        """Draw hand landmarks with fingertip lines and coordinate display."""
        height, width = frame.shape[:2]
        
        # Define fingertip landmark indices
        fingertip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        fingertip_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        
        # Draw all hand landmarks and connections first
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        # Draw fingertip indicators with coordinates
        for i, (tip_id, name) in enumerate(zip(fingertip_ids, fingertip_names)):
            landmark = hand_landmarks.landmark[tip_id]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            # Draw larger circle for fingertips
            cv2.circle(frame, (x, y), 8, (0, 255, 255), -1)  # Yellow filled circle
            cv2.circle(frame, (x, y), 12, (255, 0, 0), 2)    # Blue border
            
            # Draw lines from fingertips (extending outward)
            line_length = 30
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
        
        # Draw palm center and wrist coordinates
        palm_landmarks = [0, 1, 5, 9, 13, 17]  # Key palm points
        for palm_id in palm_landmarks:
            landmark = hand_landmarks.landmark[palm_id]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            # Draw smaller circles for palm points
            cv2.circle(frame, (x, y), 4, (255, 255, 0), -1)  # Cyan circles
            
            # Display palm coordinates (smaller text)
            palm_text = f"P{palm_id}:({x},{y})"
            cv2.putText(frame, palm_text, (x+10, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 0), 1)
        
        return frame
    
    def draw_keyboard(self, frame) -> np.ndarray:
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
                
                # Draw key rectangle on overlay
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
    
    def get_key_at_position(self, x: int, y: int) -> Optional[str]:
        """
        Get the key at the given position.
        Returns the key character if position is over a key, None otherwise.
        """
        for row_idx, row in enumerate(self.keyboard_layout):
            for col_idx, key in enumerate(row):
                key_x = self.keyboard_start_x + col_idx * (self.key_width + self.key_margin)
                key_y = self.keyboard_start_y + row_idx * (self.key_height + self.key_margin)
                
                if (key_x <= x <= key_x + self.key_width and 
                    key_y <= y <= key_y + self.key_height):
                    return key
        return None
    
    def type_key(self, key: str):
        """Simulate typing the given key."""
        current_time = time.time()
        if current_time - self.last_key_time > self.key_press_delay:
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
            
            # Simulate actual key press (optional)
            try:
                if key == 'SPACE':
                    pyautogui.press('space')
                elif key == 'BACK':
                    pyautogui.press('backspace')
                else:
                    pyautogui.press(key.lower())
            except:
                pass  # Ignore errors if pyautogui can't simulate the key
            
            self.last_key_time = current_time
    
    def draw_ui(self, frame) -> np.ndarray:
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
        
        # Draw instructions with smaller font
        instructions = [
            "Touch index finger to thumb to type",
            "Yellow lines = fingertips with coordinates",
            "Cyan dots = palm landmarks", 
            "Press 'q' to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = 140 + i * 22
            cv2.putText(frame, instruction, (50, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        
        # Draw current key indicator
        if self.current_key:
            cv2.putText(frame, f"CURRENT KEY: {self.current_key}", (50, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
        
        # Draw character count
        cv2.putText(frame, f"Characters: {len(self.typed_text)}", (50, 280), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        return frame
    
    def run(self):
        """Main application loop."""
        print("Starting Virtual Keyboard...")
        print("OpenCV version:", cv2.__version__)
        print("Touch your index finger to your thumb to type keys!")
        print("Press 'q' to quit")
        
        # Create OpenCV window
        cv2.namedWindow('Virtual Keyboard', cv2.WINDOW_AUTOSIZE)
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame from camera")
                break
            
            # Get actual frame dimensions
            height, width = frame.shape[:2]
            print(f"Frame size: {width}x{height}")  # Debug info
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hand landmarks
            results = self.hands.process(frame_rgb)
            
            self.current_key = None
            
            if results.multi_hand_landmarks:
                print("Hand detected!")  # Debug info
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw enhanced hand landmarks with coordinates
                    frame = self.draw_hand_landmarks_with_coordinates(frame, hand_landmarks)
                    
                    # Get index finger position
                    index_pos = self.get_index_finger_position(hand_landmarks.landmark)
                    print(f"Index finger position: {index_pos}")  # Debug info
                    
                    # Check which key the finger is hovering over
                    self.current_key = self.get_key_at_position(index_pos[0], index_pos[1])
                    if self.current_key:
                        print(f"Hovering over key: {self.current_key}")  # Debug info
                    
                    # Draw main finger position indicator (larger for index finger)
                    cv2.circle(frame, index_pos, 15, (0, 0, 255), 3)  # Red circle for index finger
                    
                    # Check for finger touch gesture
                    if self.is_finger_touching_thumb(hand_landmarks.landmark):
                        if self.current_key:
                            self.type_key(self.current_key)
                            # Visual feedback for touch
                            cv2.circle(frame, index_pos, 25, (0, 255, 0), 5)
            else:
                print("No hand detected")  # Debug info
            
            # Draw virtual keyboard
            frame = self.draw_keyboard(frame)
            
            # Draw UI elements
            frame = self.draw_ui(frame)
            
            # Display frame
            cv2.imshow('Virtual Keyboard', frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quit key pressed")
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("\n" + "="*50)
        print("VIRTUAL KEYBOARD SESSION COMPLETE")
        print("="*50)
        print(f"FINAL TYPED TEXT: '{self.typed_text}'")
        print(f"Total Characters: {len(self.typed_text)}")
        print("="*50)

if __name__ == "__main__":
    # Create and run the virtual keyboard
    virtual_keyboard = VirtualKeyboard()
    virtual_keyboard.run()
