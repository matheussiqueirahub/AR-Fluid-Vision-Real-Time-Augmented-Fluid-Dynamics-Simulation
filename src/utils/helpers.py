"""
Utility Module - Helper functions and performance monitoring
"""

import time
import numpy as np


class FPSCounter:
    """Calculate and track FPS"""
    
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.frame_times = []
        self.last_time = time.time()
    
    def update(self) -> float:
        """Update FPS counter and return current FPS"""
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        self.frame_times.append(delta_time)
        if len(self.frame_times) > self.window_size:
            self.frame_times.pop(0)
        
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
        
        return 0.0
    
    def get_frame_time(self) -> float:
        """Get last frame time in seconds"""
        if len(self.frame_times) > 0:
            return self.frame_times[-1]
        return 0.0


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.timers = {}
        self.counters = {}
    
    def start_timer(self, name: str):
        """Start a named timer"""
        self.timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End a named timer and return elapsed time"""
        if name in self.timers:
            elapsed = time.time() - self.timers[name]
            return elapsed
        return 0.0
    
    def increment_counter(self, name: str, amount: int = 1):
        """Increment a named counter"""
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += amount
    
    def get_stats(self) -> dict:
        """Get all statistics"""
        return {
            'timers': self.timers.copy(),
            'counters': self.counters.copy()
        }
    
    def reset(self):
        """Reset all statistics"""
        self.timers.clear()
        self.counters.clear()


class SpatialHashGrid:
    """
    Spatial hash grid for efficient neighbor finding in SPH
    Optimizes particle-particle interaction calculations
    """
    
    def __init__(self, cell_size: float):
        self.cell_size = cell_size
        self.grid = {}
    
    def clear(self):
        """Clear the grid"""
        self.grid.clear()
    
    def _hash_position(self, position: np.ndarray) -> tuple:
        """Hash a position to grid coordinates"""
        return (
            int(position[0] / self.cell_size),
            int(position[1] / self.cell_size),
            int(position[2] / self.cell_size)
        )
    
    def insert(self, particle_id: int, position: np.ndarray):
        """Insert a particle into the grid"""
        cell = self._hash_position(position)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(particle_id)
    
    def query_neighbors(self, position: np.ndarray, radius: float) -> list:
        """Query all particles within radius of position"""
        neighbors = []
        
        # Calculate cell range to check
        cell_radius = int(np.ceil(radius / self.cell_size))
        center_cell = self._hash_position(position)
        
        # Check neighboring cells
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                for dz in range(-cell_radius, cell_radius + 1):
                    cell = (
                        center_cell[0] + dx,
                        center_cell[1] + dy,
                        center_cell[2] + dz
                    )
                    
                    if cell in self.grid:
                        neighbors.extend(self.grid[cell])
        
        return neighbors


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normalize a vector"""
    norm = np.linalg.norm(v)
    if norm < 1e-6:
        return np.zeros_like(v)
    return v / norm


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation"""
    return a + (b - a) * t


def smooth_step(edge0: float, edge1: float, x: float) -> float:
    """Smooth step function"""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)
