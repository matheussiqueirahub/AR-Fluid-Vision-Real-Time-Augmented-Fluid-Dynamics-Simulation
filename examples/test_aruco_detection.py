"""
Example: Test ArUco Marker Detection
Test AR tracking with ArUco markers
"""

import cv2
import sys
sys.path.append('..')

from src.computer_vision import SurfaceDetector, CameraCapture


def main():
    """Test ArUco marker detection"""
    print("Starting ArUco marker detection test...")
    print("Show an ArUco marker (DICT_6X6_250) to the camera")
    print("You can generate markers at: https://chev.me/arucogen/")
    print("Press Q to quit")
    
    # Initialize components
    camera = CameraCapture(camera_id=0)
    surface_detector = SurfaceDetector()
    
    if not camera.start():
        print("Error: Could not start camera")
        return
    
    try:
        while True:
            frame = camera.read_frame()
            
            if frame is None:
                continue
            
            # Detect ArUco markers
            rvec, tvec = surface_detector.detect_aruco_markers(frame)
            
            # Draw markers and axes
            frame = surface_detector.draw_aruco_markers(frame)
            
            # Display marker info
            if rvec is not None and tvec is not None:
                cv2.putText(
                    frame,
                    "Marker detected!",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2
                )
                
                # Display position
                text = f"Position: ({tvec[0][0]:.2f}, {tvec[0][1]:.2f}, {tvec[0][2]:.2f})"
                cv2.putText(
                    frame,
                    text,
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )
            else:
                cv2.putText(
                    frame,
                    "No marker detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    2
                )
            
            cv2.imshow('ArUco Marker Detection Test', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
    
    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
