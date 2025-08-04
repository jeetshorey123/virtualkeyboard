# Virtual Keyboard with MediaPipe Hand Tracking

A computer vision-based virtual keyboard that uses MediaPipe for hand tracking and gesture recognition. Type by touching your index finger to your thumb while hovering over virtual keys displayed on your camera feed.

## Features

- **Real-time Hand Tracking**: Uses MediaPipe to detect and track hand landmarks
- **Gesture Recognition**: Detects when index finger touches thumb for key activation
- **Virtual Keyboard Display**: On-screen keyboard overlay with visual feedback
- **Live Text Display**: Shows typed text in real-time
- **Key Simulation**: Optional integration with pyautogui for actual key presses

## Requirements

- Python 3.7+
- Webcam/Camera
- Windows/macOS/Linux

## Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python virtual_keyboard.py
   ```

## How to Use

1. **Start the application** - Your camera feed will open with a virtual keyboard overlay
2. **Position your hand** - Make sure your hand is visible to the camera
3. **Hover over keys** - Move your index finger over the key you want to type
4. **Touch to type** - Touch your index finger to your thumb to "press" the key
5. **Press 'q'** to quit the application

## Controls

- **Index Finger Position**: Controls the cursor/selector on the virtual keyboard
- **Index + Thumb Touch**: Activates the key press
- **'Q' Key**: Quit the application

## Technical Details

### Hand Landmark Detection
- Uses MediaPipe's hand tracking solution
- Tracks 21 hand landmarks in real-time
- Focuses on thumb tip (landmark 4) and index finger tip (landmark 8)

### Gesture Recognition
- Calculates Euclidean distance between finger tips
- Configurable touch threshold (default: 30 pixels)
- Includes debouncing to prevent multiple rapid key presses

### Virtual Keyboard Layout
- Standard QWERTY layout
- Configurable key size and spacing
- Visual feedback for key selection and activation

## Customization

You can modify these parameters in the `VirtualKeyboard` class:

```python
# Key appearance
self.key_width = 80          # Key width in pixels
self.key_height = 80         # Key height in pixels
self.key_margin = 10         # Spacing between keys

# Gesture sensitivity
self.touch_threshold = 30    # Distance for finger touch detection
self.key_press_delay = 0.5   # Minimum time between key presses

# Camera settings
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # Frame width
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)   # Frame height
```

## Troubleshooting

### Camera Issues
- Ensure your camera is not being used by another application
- Try changing the camera index in `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` or higher

### Hand Detection Issues
- Ensure good lighting conditions
- Keep your hand at a reasonable distance from the camera
- Make sure your entire hand is visible in the frame

### Performance Issues
- Close other applications using the camera
- Reduce frame resolution if needed
- Adjust MediaPipe confidence thresholds

## Dependencies

- **mediapipe**: Hand tracking and pose estimation
- **opencv-python**: Computer vision and camera handling
- **numpy**: Numerical operations
- **pyautogui**: Optional keyboard simulation
- **Pillow**: Image processing utilities

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to contribute by:
- Adding new keyboard layouts
- Improving gesture recognition accuracy
- Adding new features like word prediction
- Optimizing performance

## Future Enhancements

- [ ] Multiple hand support
- [ ] Custom keyboard layouts
- [ ] Word prediction and autocomplete
- [ ] Sound feedback
- [ ] Gesture customization
- [ ] Mobile support
