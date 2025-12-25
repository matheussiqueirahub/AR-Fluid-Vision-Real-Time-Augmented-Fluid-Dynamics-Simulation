"""
Example: Basic Fluid Simulation without AR
Demonstrates the fluid physics engine without camera/AR components
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
sys.path.append('..')

from src.fluid_physics import SPHFluidSimulator
from config import FLUID_CONFIG


def main():
    """Run basic fluid simulation visualization"""
    print("Starting basic fluid simulation...")
    
    # Create simulator
    simulator = SPHFluidSimulator(FLUID_CONFIG)
    
    # Setup matplotlib
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Initialize scatter plot
    positions = simulator.get_particle_positions()
    scatter = ax.scatter(
        positions[:, 0],
        positions[:, 1],
        positions[:, 2],
        c='blue',
        s=50,
        alpha=0.6
    )
    
    # Set axis limits
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('SPH Fluid Simulation')
    
    frame_count = [0]
    
    def update(frame):
        """Update function for animation"""
        # Update simulation
        simulator.update()
        
        # Get new positions
        positions = simulator.get_particle_positions()
        
        # Update scatter plot
        scatter._offsets3d = (
            positions[:, 0],
            positions[:, 1],
            positions[:, 2]
        )
        
        frame_count[0] += 1
        if frame_count[0] % 30 == 0:
            print(f"Frame {frame_count[0]}")
        
        return scatter,
    
    # Create animation
    anim = FuncAnimation(
        fig,
        update,
        frames=300,
        interval=16,  # ~60 FPS
        blit=False
    )
    
    plt.show()


if __name__ == "__main__":
    main()
