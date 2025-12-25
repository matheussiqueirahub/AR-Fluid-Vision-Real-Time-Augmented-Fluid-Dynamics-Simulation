"""
Example: Test Gesture Recognition
Test hand tracking and gesture recognition without full AR
"""

import cv2
import sys
sys.path.append('..')

from src.interaction import GestureRecognizer
from src.computer_vision import CameraCapture


def main():
    """Test gesture recognition"""
    print("Starting gesture recognition test...")
    print("Show your hand to the camera")
    print("Try different gestures: point, open hand, fist, peace sign")
    print("Press Q to quit")
    
    # Initialize components
    camera = CameraCapture(camera_id=0)
    gesture_recognizer = GestureRecognizer()
    
    if not camera.start():
        print("Error: Could not start camera")
        return
    
    try:
        while True:
            frame = camera.read_frame()
            
            if frame is None:
                continue
            
            # Process gestures
            hand_positions, hand_velocities = gesture_recognizer.process_frame(frame)
            
            # Draw hand landmarks
            frame = gesture_recognizer.draw_hand_landmarks(frame)
            
            # Display gesture info
            if hand_positions:
                gesture_type = gesture_recognizer.gesture_type or "unknown"
                cv2.putText(
                    frame,
                    f"Gesture: {gesture_type}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2
                )
                
                # Display hand positions
                for i, pos in enumerate(hand_positions):
                    text = f"Hand {i+1}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"
                    cv2.putText(
                        frame,
                        text,
                        (10, 70 + i * 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2
                    )
            
            cv2.imshow('Gesture Recognition Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
    
    finally:
        camera.stop()
        gesture_recognizer.cleanup()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
