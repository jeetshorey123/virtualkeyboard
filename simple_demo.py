#!/usr/bin/env python3
"""
Simple Virtual Keyboard Demo
A basic version of the virtual keyboard for testing and demonstration.
"""

import cv2
import mediapipe as mp
import numpy as np
import math

class SimpleVirtualKeyboard:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Camera
        self.cap = cv2.VideoCapture(0)
        
        # Simple keyboard layout
        self.keys = ['A', 'B', 'C', 'D', 'E']
        self.key_positions = []
        self.setup_keyboard()
        
        # Settings
        self.touch_threshold = 40
        self.typed_text = ""
        
    def setup_keyboard(self):
        """Set up keyboard key positions."""
        start_x, start_y = 100, 400
        key_width, key_height = 100, 100
        spacing = 120
        
        for i, key in enumerate(self.keys):
            x = start_x + i * spacing
            y = start_y
            self.key_positions.append({
                'key': key,
                'x': x,
                'y': y,
                'width': key_width,
                'height': key_height
            })
    
    def get_distance(self, p1, p2):
        """Calculate distance between two points."""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    def is_touching(self, landmarks):
        """Check if thumb and index finger are touching."""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        h, w = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        
        thumb_pos = (thumb_tip.x * w, thumb_tip.y * h)
        index_pos = (index_tip.x * w, index_tip.y * h)
        
        distance = self.get_distance(thumb_pos, index_pos)
        return distance < self.touch_threshold
    
    def get_finger_position(self, landmarks):
        """Get index finger tip position."""
        index_tip = landmarks[8]
        h, w = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        return (int(index_tip.x * w), int(index_tip.y * h))
    
    def draw_keyboard(self, frame):
        """Draw the virtual keyboard."""
        for key_info in self.key_positions:
            x, y = key_info['x'], key_info['y']
            w, h = key_info['width'], key_info['height']
            key = key_info['key']
            
            # Draw key
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
            
            # Draw key label
            text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            cv2.putText(frame, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    def get_key_at_position(self, pos):
        """Get key at given position."""
        x, y = pos
        for key_info in self.key_positions:
            kx, ky = key_info['x'], key_info['y']
            kw, kh = key_info['width'], key_info['height']
            
            if kx <= x <= kx + kw and ky <= y <= ky + kh:
                return key_info['key']
        return None
    
    def run(self):
        """Main loop."""
        print("Simple Virtual Keyboard Demo")
        print("Touch your index finger to thumb to type!")
        print("Press ESC to exit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process hands
            results = self.hands.process(rgb_frame)
            
            current_key = None
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Get finger position
                    finger_pos = self.get_finger_position(hand_landmarks.landmark)
                    
                    # Draw finger indicator
                    cv2.circle(frame, finger_pos, 15, (0, 255, 0), -1)
                    
                    # Check which key finger is over
                    current_key = self.get_key_at_position(finger_pos)
                    
                    # Check for touch gesture
                    if self.is_touching(hand_landmarks.landmark) and current_key:
                        self.typed_text += current_key
                        print(f"Typed: {current_key}")
                        cv2.circle(frame, finger_pos, 25, (0, 0, 255), 5)
            
            # Draw keyboard
            self.draw_keyboard(frame)
            
            # Show typed text
            cv2.putText(frame, f"Typed: {self.typed_text}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show current key
            if current_key:
                cv2.putText(frame, f"Hovering: {current_key}", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Show instructions
            cv2.putText(frame, "Touch index to thumb to type", (50, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Simple Virtual Keyboard', frame)
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print(f"Final text: {self.typed_text}")

if __name__ == "__main__":
    demo = SimpleVirtualKeyboard()
    demo.run()
