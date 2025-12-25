"""
AR Renderer Module - Real-time Augmented Reality Visualization
Renders fluid particles overlaid on camera feed with OpenGL acceleration
"""

import cv2
import numpy as np
from typing import Optional, Tuple
from config import RENDER_CONFIG


class ARFluidRenderer:
    """
    Renders fluid particles in augmented reality
    Overlays particles on camera feed with realistic effects
    """
    
    def __init__(self, config: dict = None):
        self.config = config or RENDER_CONFIG
        
        self.particle_size = self.config['particle_size']
        self.particle_color = self.config['particle_color']
        self.enable_glow = self.config['enable_glow']
        self.enable_motion_blur = self.config['enable_motion_blur']
        
        # Overlay canvas
        self.overlay = None
        
    def render_particles_2d(
        self,
        frame: np.ndarray,
        particle_positions_2d: np.ndarray,
        velocities: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Render particles on frame using 2D projections
        
        Args:
            frame: Camera frame (BGR)
            particle_positions_2d: Nx2 array of 2D screen coordinates
            velocities: Nx3 array of particle velocities (optional)
        
        Returns:
            Rendered frame with particles
        """
        height, width = frame.shape[:2]
        
        # Create overlay
        overlay = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Convert particle color to BGR
        b = int(self.particle_color[2] * 255)
        g = int(self.particle_color[1] * 255)
        r = int(self.particle_color[0] * 255)
        alpha = int(self.particle_color[3] * 255)
        
        for i, pos in enumerate(particle_positions_2d):
            x, y = int(pos[0]), int(pos[1])
            
            # Skip if outside frame
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            
            # Compute particle size based on depth (if available)
            size = self.particle_size
            if velocities is not None:
                speed = np.linalg.norm(velocities[i])
                size = self.particle_size * (1.0 + speed * 0.5)
            
            size = int(min(size, 50))  # Limit maximum size
            
            # Draw particle with glow effect
            if self.enable_glow:
                self._draw_glowing_particle(overlay, (x, y), size, (b, g, r, alpha))
            else:
                cv2.circle(overlay, (x, y), size, (b, g, r, alpha), -1)
            
            # Draw motion blur trail
            if self.enable_motion_blur and velocities is not None:
                velocity = velocities[i]
                speed = np.linalg.norm(velocity)
                if speed > 0.1:
                    # Draw trail in direction opposite to velocity
                    trail_length = int(speed * 20)
                    vel_2d = velocity[:2] / speed  # Normalize 2D component
                    
                    end_x = int(x - vel_2d[0] * trail_length)
                    end_y = int(y - vel_2d[1] * trail_length)
                    
                    # Draw line with decreasing alpha
                    for j in range(5):
                        alpha_trail = int(alpha * (1.0 - j / 5.0) * 0.5)
                        cv2.line(
                            overlay,
                            (x, y),
                            (end_x, end_y),
                            (b, g, r, alpha_trail),
                            max(1, size // 2)
                        )
        
        # Blend overlay with frame
        result = self._blend_overlay(frame, overlay)
        
        return result
    
    def _draw_glowing_particle(
        self,
        overlay: np.ndarray,
        center: Tuple[int, int],
        size: int,
        color: Tuple[int, int, int, int]
    ):
        """Draw particle with glow effect using multiple layers"""
        b, g, r, alpha = color
        
        # Draw outer glow (larger, more transparent)
        glow_size = int(size * 2.0)
        glow_alpha = int(alpha * 0.3)
        cv2.circle(overlay, center, glow_size, (b, g, r, glow_alpha), -1)
        
        # Draw middle layer
        mid_size = int(size * 1.5)
        mid_alpha = int(alpha * 0.6)
        cv2.circle(overlay, center, mid_size, (b, g, r, mid_alpha), -1)
        
        # Draw core (brightest)
        cv2.circle(overlay, center, size, (b, g, r, alpha), -1)
    
    def _blend_overlay(self, frame: np.ndarray, overlay: np.ndarray) -> np.ndarray:
        """Blend overlay with frame using alpha channel"""
        # Convert frame to float for blending
        frame_float = frame.astype(np.float32)
        
        # Extract alpha channel
        alpha = overlay[:, :, 3:4].astype(np.float32) / 255.0
        
        # Extract color channels
        overlay_bgr = overlay[:, :, :3].astype(np.float32)
        
        # Blend
        blended = frame_float * (1.0 - alpha) + overlay_bgr * alpha
        
        return blended.astype(np.uint8)
    
    def draw_boundaries(self, frame: np.ndarray, surface_detector) -> np.ndarray:
        """Draw visualization of simulation boundaries"""
        # This would project boundary box using surface detector
        # For now, draw a simple frame overlay
        height, width = frame.shape[:2]
        
        margin = 50
        color = (0, 255, 255)  # Yellow
        thickness = 2
        
        cv2.rectangle(
            frame,
            (margin, margin),
            (width - margin, height - margin),
            color,
            thickness
        )
        
        return frame
    
    def add_hud(
        self,
        frame: np.ndarray,
        fps: float,
        particle_count: int,
        debug_info: dict = None
    ) -> np.ndarray:
        """Add heads-up display with information"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (0, 255, 0)
        thickness = 2
        
        y_offset = 30
        
        # FPS
        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (10, y_offset),
            font,
            font_scale,
            color,
            thickness
        )
        y_offset += 30
        
        # Particle count
        cv2.putText(
            frame,
            f"Particles: {particle_count}",
            (10, y_offset),
            font,
            font_scale,
            color,
            thickness
        )
        y_offset += 30
        
        # Debug info
        if debug_info:
            for key, value in debug_info.items():
                text = f"{key}: {value}"
                cv2.putText(
                    frame,
                    text,
                    (10, y_offset),
                    font,
                    font_scale,
                    color,
                    thickness
                )
                y_offset += 30
        
        return frame


class SimpleRenderer:
    """
    Fallback simple renderer without OpenGL
    For systems where OpenGL is not available
    """
    
    def __init__(self):
        self.particle_color = (255, 100, 50)  # BGR
        self.particle_radius = 5
    
    def render(self, frame: np.ndarray, positions: np.ndarray) -> np.ndarray:
        """Simple particle rendering"""
        for pos in positions:
            # Simple perspective projection
            if len(pos) == 3:
                # Project 3D to 2D
                scale = 500.0 / (pos[2] + 2.0)  # Simple depth scaling
                x = int(frame.shape[1] / 2 + pos[0] * scale)
                y = int(frame.shape[0] / 2 - pos[1] * scale)
            else:
                x, y = int(pos[0]), int(pos[1])
            
            if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:
                cv2.circle(frame, (x, y), self.particle_radius, self.particle_color, -1)
        
        return frame
