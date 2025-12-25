"""
Computer Vision Module - Surface Detection and AR Tracking
Implements surface detection, plane tracking, and ArUco marker detection
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
from config import VISION_CONFIG


class SurfaceDetector:
    """
    Detects and tracks surfaces in the environment
    Uses both plane detection and ArUco markers for AR tracking
    """
    
    def __init__(self, config: dict = None):
        self.config = config or VISION_CONFIG
        
        # Camera parameters
        self.camera_id = self.config['camera_id']
        self.resolution = self.config['resolution']
        self.fps = self.config['fps']
        
        # Camera matrix (estimated - should be calibrated for production)
        self.camera_matrix = self._get_default_camera_matrix()
        self.dist_coeffs = np.zeros((4, 1))
        
        # ArUco marker detection
        aruco_dict_name = self.config['aruco_dict']
        aruco_dict_id = getattr(cv2.aruco, aruco_dict_name)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_id)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.marker_size = self.config['marker_size']
        
        # Plane detection parameters
        self.plane_ransac_threshold = 0.01
        self.min_plane_points = 100
        
        # State
        self.detected_plane = None
        self.marker_pose = None
        
    def _get_default_camera_matrix(self) -> np.ndarray:
        """Get default camera matrix based on resolution"""
        width, height = self.resolution
        focal_length = width  # Approximate
        center = (width / 2, height / 2)
        
        return np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float32)
    
    def detect_aruco_markers(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Detect ArUco markers and estimate pose
        Returns: (rotation_vector, translation_vector) or (None, None)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect markers
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )
        
        if ids is not None and len(ids) > 0:
            # Use first detected marker
            rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, self.camera_matrix, self.dist_coeffs
            )
            
            self.marker_pose = (rvec[0], tvec[0])
            return rvec[0], tvec[0]
        
        return None, None
    
    def detect_plane(self, frame: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Detect dominant plane in the image using feature detection
        Returns: (plane_normal, plane_point) or None
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect features
        detector = cv2.ORB_create(nfeatures=500)
        keypoints, descriptors = detector.detectAndCompute(gray, None)
        
        if len(keypoints) < self.min_plane_points:
            return None
        
        # Extract 2D points
        points_2d = np.array([kp.pt for kp in keypoints], dtype=np.float32)
        
        # Simple plane detection: assume ground plane
        # In production, this should use structure from motion or depth sensing
        plane_normal = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        plane_point = np.array([0.0, -1.0, 0.0], dtype=np.float32)
        
        self.detected_plane = (plane_normal, plane_point)
        return plane_normal, plane_point
    
    def draw_aruco_markers(self, frame: np.ndarray) -> np.ndarray:
        """Draw detected ArUco markers on frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.aruco_params
        )
        
        if ids is not None:
            frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            # Draw axis for each marker
            if self.marker_pose is not None:
                rvec, tvec = self.marker_pose
                frame = cv2.drawFrameAxes(
                    frame, self.camera_matrix, self.dist_coeffs,
                    rvec, tvec, self.marker_size * 0.5
                )
        
        return frame
    
    def get_world_transform(self) -> Optional[np.ndarray]:
        """
        Get transformation matrix from camera to world coordinates
        Returns 4x4 transformation matrix or None
        """
        if self.marker_pose is None:
            return None
        
        rvec, tvec = self.marker_pose
        
        # Convert rotation vector to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rvec)
        
        # Create 4x4 transformation matrix
        transform = np.eye(4, dtype=np.float32)
        transform[:3, :3] = rotation_matrix
        transform[:3, 3] = tvec.flatten()
        
        return transform
    
    def project_3d_to_2d(self, points_3d: np.ndarray) -> np.ndarray:
        """
        Project 3D world points to 2D image coordinates
        Args:
            points_3d: Nx3 array of 3D points
        Returns:
            Nx2 array of 2D image coordinates
        """
        if self.marker_pose is None:
            # Default projection without AR tracking
            # Simple perspective projection
            focal_length = self.camera_matrix[0, 0]
            center = (self.camera_matrix[0, 2], self.camera_matrix[1, 2])
            
            points_2d = []
            for point in points_3d:
                if point[2] != 0:
                    x = (point[0] / point[2]) * focal_length + center[0]
                    y = (point[1] / point[2]) * focal_length + center[1]
                else:
                    x, y = center
                points_2d.append([x, y])
            
            return np.array(points_2d, dtype=np.float32)
        
        # Project using marker pose
        rvec, tvec = self.marker_pose
        points_2d, _ = cv2.projectPoints(
            points_3d, rvec, tvec, self.camera_matrix, self.dist_coeffs
        )
        
        return points_2d.reshape(-1, 2)


class CameraCapture:
    """Manages camera capture and frame processing"""
    
    def __init__(self, camera_id: int = 0, resolution: Tuple[int, int] = (1280, 720)):
        self.camera_id = camera_id
        self.resolution = resolution
        self.cap = None
        
    def start(self) -> bool:
        """Start camera capture"""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            return False
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        return True
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the camera"""
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def stop(self):
        """Stop camera capture"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
