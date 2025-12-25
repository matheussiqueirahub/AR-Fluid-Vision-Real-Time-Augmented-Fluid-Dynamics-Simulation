"""
Main Application - AR Fluid Vision Simulator
Integrates all components: physics, vision, rendering, and interaction
"""

import cv2
import numpy as np
import sys
import time

from src.fluid_physics import SPHFluidSimulator
from src.computer_vision import SurfaceDetector, CameraCapture
from src.ar_renderer import ARFluidRenderer
from src.interaction import GestureRecognizer, ObjectInteraction
from src.utils import FPSCounter, PerformanceMonitor

from config import (
    FLUID_CONFIG,
    VISION_CONFIG,
    RENDER_CONFIG,
    GESTURE_CONFIG,
    DEBUG_CONFIG
)


class ARFluidVisionApp:
    """
    Main application class for AR Fluid Vision
    Coordinates all subsystems and manages the main loop
    """
    
    def __init__(self):
        print("Initializing AR Fluid Vision...")
        
        # Initialize subsystems
        self.fluid_simulator = SPHFluidSimulator(FLUID_CONFIG)
        self.surface_detector = SurfaceDetector(VISION_CONFIG)
        self.renderer = ARFluidRenderer(RENDER_CONFIG)
        self.gesture_recognizer = GestureRecognizer(GESTURE_CONFIG)
        self.object_interaction = ObjectInteraction()
        
        # Camera capture
        self.camera = CameraCapture(
            camera_id=VISION_CONFIG['camera_id'],
            resolution=VISION_CONFIG['resolution']
        )
        
        # Performance monitoring
        self.fps_counter = FPSCounter()
        self.performance_monitor = PerformanceMonitor()
        
        # State
        self.running = False
        self.paused = False
        self.debug_mode = DEBUG_CONFIG['show_fps']
        
        print("Initialization complete!")
    
    def start(self) -> bool:
        """Start the application"""
        # Start camera
        if not self.camera.start():
            print("Error: Could not start camera")
            return False
        
        print("Camera started successfully")
        print("\nControls:")
        print("  SPACE - Pause/Resume")
        print("  R - Reset simulation")
        print("  D - Toggle debug info")
        print("  Q/ESC - Quit")
        print("\nStarting main loop...")
        
        self.running = True
        return True
    
    def stop(self):
        """Stop the application"""
        self.running = False
        self.camera.stop()
        self.gesture_recognizer.cleanup()
        cv2.destroyAllWindows()
        print("\nApplication stopped")
    
    def process_input(self, key: int):
        """Process keyboard input"""
        if key == ord('q') or key == 27:  # Q or ESC
            self.running = False
        elif key == ord(' '):  # Space
            self.paused = not self.paused
            print(f"Simulation {'paused' if self.paused else 'resumed'}")
        elif key == ord('r'):  # R
            self.fluid_simulator.reset()
            print("Simulation reset")
        elif key == ord('d'):  # D
            self.debug_mode = not self.debug_mode
            print(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")
    
    def update(self):
        """Update simulation and interactions"""
        if self.paused:
            return
        
        # Update fluid simulation
        self.performance_monitor.start_timer('physics')
        self.fluid_simulator.update()
        physics_time = self.performance_monitor.end_timer('physics')
        
        return physics_time
    
    def render(self, frame: np.ndarray) -> np.ndarray:
        """Render the current frame"""
        self.performance_monitor.start_timer('render')
        
        # Detect ArUco markers for AR tracking
        self.surface_detector.detect_aruco_markers(frame)
        
        # Get particle positions
        particle_positions_3d = self.fluid_simulator.get_particle_positions()
        particle_velocities = self.fluid_simulator.get_particle_velocities()
        
        # Project 3D positions to 2D screen coordinates
        particle_positions_2d = self.surface_detector.project_3d_to_2d(particle_positions_3d)
        
        # Render particles on frame
        frame = self.renderer.render_particles_2d(
            frame,
            particle_positions_2d,
            particle_velocities
        )
        
        # Draw ArUco markers if detected
        if DEBUG_CONFIG['show_boundaries']:
            frame = self.surface_detector.draw_aruco_markers(frame)
        
        # Draw hand landmarks
        if DEBUG_CONFIG['show_hand_landmarks']:
            frame = self.gesture_recognizer.draw_hand_landmarks(frame)
        
        render_time = self.performance_monitor.end_timer('render')
        
        return frame, render_time
    
    def process_interactions(self, frame: np.ndarray):
        """Process user interactions"""
        self.performance_monitor.start_timer('interaction')
        
        # Process hand gestures
        hand_positions, hand_velocities = self.gesture_recognizer.process_frame(frame)
        
        # Apply interaction forces to fluid
        interaction_forces = self.gesture_recognizer.get_interaction_forces()
        for position, force, radius in interaction_forces:
            self.fluid_simulator.add_external_force(position, radius, force)
        
        # Detect and interact with objects
        objects = self.object_interaction.detect_objects(frame)
        
        interaction_time = self.performance_monitor.end_timer('interaction')
        
        return interaction_time
    
    def run(self):
        """Main application loop"""
        if not self.start():
            return
        
        try:
            while self.running:
                # Read frame from camera
                frame = self.camera.read_frame()
                
                if frame is None:
                    print("Warning: Could not read frame")
                    continue
                
                # Process interactions
                interaction_time = self.process_interactions(frame)
                
                # Update simulation
                physics_time = self.update()
                
                # Render frame
                rendered_frame, render_time = self.render(frame)
                
                # Add HUD with debug information
                if self.debug_mode:
                    fps = self.fps_counter.update()
                    debug_info = {}
                    
                    if DEBUG_CONFIG['verbose']:
                        debug_info['Physics'] = f"{physics_time*1000:.1f}ms"
                        debug_info['Render'] = f"{render_time*1000:.1f}ms"
                        debug_info['Interaction'] = f"{interaction_time*1000:.1f}ms"
                    
                    rendered_frame = self.renderer.add_hud(
                        rendered_frame,
                        fps,
                        len(self.fluid_simulator.particles),
                        debug_info
                    )
                
                # Display frame
                cv2.imshow('AR Fluid Vision', rendered_frame)
                
                # Process input
                key = cv2.waitKey(1) & 0xFF
                if key != 255:
                    self.process_input(key)
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()


def main():
    """Main entry point"""
    print("=" * 60)
    print("AR Fluid Vision - Real-Time Augmented Fluid Dynamics")
    print("=" * 60)
    print()
    
    app = ARFluidVisionApp()
    app.run()


if __name__ == "__main__":
    main()
