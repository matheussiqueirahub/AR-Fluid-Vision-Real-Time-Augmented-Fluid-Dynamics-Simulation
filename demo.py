"""
Demo: Fluid Simulation with Simulated Interaction
Demonstrates the system without requiring a camera
Creates a window showing fluid simulation with simulated hand interaction
"""

import cv2
import numpy as np
import sys
sys.path.append('.')

from src.fluid_physics import SPHFluidSimulator
from src.ar_renderer import ARFluidRenderer
from src.utils import FPSCounter


class DemoApp:
    """Demo application without camera"""
    
    def __init__(self):
        print("Initializing demo...")
        
        # Create components
        self.simulator = SPHFluidSimulator()
        self.renderer = ARFluidRenderer()
        self.fps_counter = FPSCounter()
        
        # Window settings
        self.width = 1280
        self.height = 720
        
        # Interaction state
        self.interaction_pos = np.array([0.0, 0.5, 0.0])
        self.interaction_active = False
        self.auto_move = True
        self.time = 0.0
        
        print("Demo initialized!")
    
    def create_background_frame(self):
        """Create a nice gradient background"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Create gradient
        for y in range(self.height):
            color_value = int(20 + (y / self.height) * 40)
            frame[y, :] = [color_value, color_value // 2, color_value // 4]
        
        # Add grid pattern
        for i in range(0, self.width, 100):
            cv2.line(frame, (i, 0), (i, self.height), (30, 30, 30), 1)
        for i in range(0, self.height, 100):
            cv2.line(frame, (0, i), (self.width, i), (30, 30, 30), 1)
        
        return frame
    
    def project_3d_to_2d(self, positions_3d):
        """Simple projection from 3D simulation space to 2D screen"""
        positions_2d = []
        
        for pos in positions_3d:
            # Scale and center
            scale = 300.0
            x = int(self.width / 2 + pos[0] * scale)
            y = int(self.height / 2 - pos[1] * scale)
            
            positions_2d.append([x, y])
        
        return np.array(positions_2d, dtype=np.float32)
    
    def update_interaction(self):
        """Update simulated interaction position"""
        if self.auto_move:
            # Move in a circular pattern
            radius = 0.6
            self.interaction_pos[0] = np.sin(self.time) * radius
            self.interaction_pos[1] = 0.2 + np.cos(self.time * 0.7) * 0.3
            self.interaction_pos[2] = np.cos(self.time) * radius * 0.5
            
            # Apply force
            force = np.array([
                np.cos(self.time) * 30.0,
                np.sin(self.time * 2.0) * 10.0,
                np.sin(self.time) * 30.0
            ])
            
            self.simulator.add_external_force(
                self.interaction_pos,
                0.3,
                force
            )
    
    def draw_interaction_point(self, frame):
        """Draw the interaction point on screen"""
        # Project interaction position
        pos_2d = self.project_3d_to_2d(np.array([self.interaction_pos]))[0]
        x, y = int(pos_2d[0]), int(pos_2d[1])
        
        # Draw circles for interaction zone
        if 0 <= x < self.width and 0 <= y < self.height:
            cv2.circle(frame, (x, y), 60, (0, 255, 255), 2)
            cv2.circle(frame, (x, y), 8, (0, 255, 255), -1)
    
    def run(self):
        """Run demo loop"""
        print("\nDemo Controls:")
        print("  SPACE - Pause/Resume")
        print("  A - Toggle auto-move interaction")
        print("  R - Reset simulation")
        print("  Q/ESC - Quit")
        print("\nStarting demo...\n")
        
        paused = False
        
        while True:
            # Create frame
            frame = self.create_background_frame()
            
            # Update simulation
            if not paused:
                self.update_interaction()
                self.simulator.update()
                self.time += 0.016
            
            # Get particle data
            positions_3d = self.simulator.get_particle_positions()
            velocities = self.simulator.get_particle_velocities()
            
            # Project to 2D
            positions_2d = self.project_3d_to_2d(positions_3d)
            
            # Render particles
            frame = self.renderer.render_particles_2d(frame, positions_2d, velocities)
            
            # Draw interaction point
            if self.auto_move:
                self.draw_interaction_point(frame)
            
            # Add info text
            fps = self.fps_counter.update()
            
            info_text = [
                f"FPS: {fps:.1f}",
                f"Particles: {len(self.simulator.particles)}",
                f"Auto-move: {'ON' if self.auto_move else 'OFF'}",
                "" if not paused else "PAUSED"
            ]
            
            y_offset = 30
            for text in info_text:
                if text:
                    cv2.putText(
                        frame, text, (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 0), 2
                    )
                    y_offset += 35
            
            # Add title
            title = "AR Fluid Vision - Demo Mode (No Camera)"
            cv2.putText(
                frame, title, (10, self.height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (100, 200, 255), 2
            )
            
            # Display
            cv2.imshow('AR Fluid Vision Demo', frame)
            
            # Process input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord(' '):  # Space
                paused = not paused
                print(f"{'Paused' if paused else 'Resumed'}")
            elif key == ord('a'):  # A
                self.auto_move = not self.auto_move
                print(f"Auto-move: {'ON' if self.auto_move else 'OFF'}")
            elif key == ord('r'):  # R
                self.simulator.reset()
                self.time = 0.0
                print("Reset simulation")
        
        cv2.destroyAllWindows()
        print("\nDemo closed")


def main():
    """Main entry point"""
    print("=" * 60)
    print("AR Fluid Vision - Demo Mode")
    print("=" * 60)
    print()
    
    app = DemoApp()
    app.run()


if __name__ == "__main__":
    main()
