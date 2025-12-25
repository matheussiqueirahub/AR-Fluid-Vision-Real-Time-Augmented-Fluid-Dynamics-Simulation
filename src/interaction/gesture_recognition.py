"""
Interaction Module - Gesture Recognition and User Interaction
Implements hand tracking, gesture recognition, and interaction with fluid particles
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, List, Tuple
from config import GESTURE_CONFIG


class GestureRecognizer:
    """
    Recognizes hand gestures and tracks hand position for fluid interaction
    Uses MediaPipe for real-time hand tracking
    """
    
    def __init__(self, config: dict = None):
        self.config = config or GESTURE_CONFIG
        
        # MediaPipe hand tracking
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.config['min_detection_confidence'],
            min_tracking_confidence=self.config['min_tracking_confidence']
        )
        
        # Interaction parameters
        self.interaction_radius = self.config['interaction_radius']
        self.force_multiplier = self.config['force_multiplier']
        
        # State
        self.hand_positions = []
        self.hand_velocities = []
        self.previous_positions = []
        self.gesture_type = None
        
    def process_frame(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Process frame to detect hands and compute positions/velocities
        Returns: (hand_positions, hand_velocities)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame
        results = self.hands.process(rgb_frame)
        
        self.hand_positions = []
        self.hand_velocities = []
        
        if results.multi_hand_landmarks:
            height, width = frame.shape[:2]
            
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get palm center (approximate as average of key points)
                palm_x = 0.0
                palm_y = 0.0
                palm_z = 0.0
                
                key_points = [0, 5, 9, 13, 17]  # Wrist and base of each finger
                
                for idx in key_points:
                    landmark = hand_landmarks.landmark[idx]
                    palm_x += landmark.x
                    palm_y += landmark.y
                    palm_z += landmark.z
                
                palm_x /= len(key_points)
                palm_y /= len(key_points)
                palm_z /= len(key_points)
                
                # Convert to 3D world coordinates (normalized)
                # Map screen coordinates to simulation space
                world_x = (palm_x - 0.5) * 2.0  # -1 to 1
                world_y = -(palm_y - 0.5) * 2.0  # -1 to 1, inverted
                world_z = palm_z * 2.0  # 0 to 2
                
                position = np.array([world_x, world_y, world_z], dtype=np.float32)
                self.hand_positions.append(position)
                
                # Compute velocity
                if hand_idx < len(self.previous_positions):
                    velocity = position - self.previous_positions[hand_idx]
                else:
                    velocity = np.zeros(3, dtype=np.float32)
                
                self.hand_velocities.append(velocity)
            
            # Update previous positions
            self.previous_positions = self.hand_positions.copy()
            
            # Detect gesture type
            self._detect_gesture(results.multi_hand_landmarks[0])
        
        return self.hand_positions, self.hand_velocities
    
    def _detect_gesture(self, hand_landmarks):
        """Detect specific gesture types"""
        # Get finger tip and base positions
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]
        
        index_base = hand_landmarks.landmark[5]
        middle_base = hand_landmarks.landmark[9]
        ring_base = hand_landmarks.landmark[13]
        pinky_base = hand_landmarks.landmark[17]
        
        # Check if fingers are extended
        index_extended = index_tip.y < index_base.y
        middle_extended = middle_tip.y < middle_base.y
        ring_extended = ring_tip.y < ring_base.y
        pinky_extended = pinky_tip.y < pinky_base.y
        
        # Detect gestures
        if index_extended and middle_extended and not ring_extended and not pinky_extended:
            self.gesture_type = "two_fingers"  # Peace sign - strong push
        elif index_extended and not middle_extended:
            self.gesture_type = "point"  # Point - directional force
        elif all([index_extended, middle_extended, ring_extended, pinky_extended]):
            self.gesture_type = "open_hand"  # Open hand - attraction
        else:
            self.gesture_type = "fist"  # Fist - repulsion
    
    def draw_hand_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """Draw hand landmarks on frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        
        return frame
    
    def get_interaction_forces(self) -> List[Tuple[np.ndarray, np.ndarray, float]]:
        """
        Get interaction forces for fluid simulation
        Returns list of (position, force_vector, radius) tuples
        """
        forces = []
        
        for i, position in enumerate(self.hand_positions):
            velocity = self.hand_velocities[i] if i < len(self.hand_velocities) else np.zeros(3)
            
            # Compute force based on gesture and velocity
            force_magnitude = self.force_multiplier
            
            if self.gesture_type == "two_fingers":
                force_magnitude *= 2.0
            elif self.gesture_type == "open_hand":
                force_magnitude *= -0.5  # Attraction
            elif self.gesture_type == "fist":
                force_magnitude *= 1.5  # Strong repulsion
            
            # Force direction based on velocity (motion) or default push
            if np.linalg.norm(velocity) > 0.01:
                force_direction = velocity / np.linalg.norm(velocity)
            else:
                force_direction = np.array([0.0, 0.0, 1.0])  # Default forward
            
            force_vector = force_direction * force_magnitude
            
            forces.append((position, force_vector, self.interaction_radius))
        
        return forces
    
    def cleanup(self):
        """Release MediaPipe resources"""
        self.hands.close()


class ObjectInteraction:
    """
    Handles interaction with detected objects in the scene
    Can detect and track objects for collision with fluid
    """
    
    def __init__(self):
        self.tracked_objects = []
        
        # Simple object detector using color or contours
        self.detector = cv2.SimpleBlobDetector_create()
    
    def detect_objects(self, frame: np.ndarray) -> List[Tuple[np.ndarray, float]]:
        """
        Detect objects in frame
        Returns list of (position, radius) tuples
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect blobs
        keypoints = self.detector.detect(gray)
        
        objects = []
        for kp in keypoints:
            # Convert to world coordinates
            x = (kp.pt[0] / frame.shape[1] - 0.5) * 2.0
            y = -(kp.pt[1] / frame.shape[0] - 0.5) * 2.0
            z = 0.0
            
            position = np.array([x, y, z], dtype=np.float32)
            radius = kp.size / 100.0
            
            objects.append((position, radius))
        
        self.tracked_objects = objects
        return objects
