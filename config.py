"""
Configuration file for AR Fluid Vision Simulator
Contains all system parameters and settings
"""

# Fluid Simulation Parameters
FLUID_CONFIG = {
    'num_particles': 500,
    'particle_mass': 0.02,
    'rest_density': 1000.0,
    'gas_constant': 2000.0,
    'viscosity': 0.5,
    'gravity': [0.0, -9.8, 0.0],
    'smoothing_radius': 0.05,
    'time_step': 0.016,  # ~60 FPS
    'damping': 0.95,
}

# Boundary Conditions
BOUNDARY_CONFIG = {
    'min_bounds': [-1.0, -1.0, -1.0],
    'max_bounds': [1.0, 1.0, 1.0],
    'restitution': 0.3,  # Coefficient of restitution for collisions
}

# Computer Vision Parameters
VISION_CONFIG = {
    'camera_id': 0,
    'resolution': (1280, 720),
    'fps': 30,
    'marker_size': 0.15,  # meters
    'aruco_dict': 'DICT_6X6_250',
}

# AR Rendering Parameters
RENDER_CONFIG = {
    'particle_size': 10.0,
    'particle_color': [0.2, 0.5, 1.0, 0.8],  # RGBA
    'background_alpha': 0.0,
    'enable_glow': True,
    'enable_motion_blur': True,
}

# Gesture Recognition Parameters
GESTURE_CONFIG = {
    'enable_hand_tracking': True,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'interaction_radius': 0.15,
    'force_multiplier': 50.0,
}

# Performance Parameters
PERFORMANCE_CONFIG = {
    'enable_multiprocessing': False,
    'max_fps': 60,
    'enable_profiling': False,
    'spatial_hash_grid_size': 0.1,
}

# Debug Parameters
DEBUG_CONFIG = {
    'show_fps': True,
    'show_particle_count': True,
    'show_boundaries': True,
    'show_hand_landmarks': True,
    'verbose': False,
}
