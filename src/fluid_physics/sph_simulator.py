"""
Fluid Physics Module - Smoothed Particle Hydrodynamics (SPH) Implementation
Implements Navier-Stokes equations for real-time fluid simulation
"""

import numpy as np
from typing import List, Tuple
from config import FLUID_CONFIG, BOUNDARY_CONFIG


class Particle:
    """Represents a single fluid particle"""
    
    def __init__(self, position: np.ndarray):
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.zeros(3, dtype=np.float32)
        self.force = np.zeros(3, dtype=np.float32)
        self.density = 0.0
        self.pressure = 0.0
        self.mass = FLUID_CONFIG['particle_mass']
        

class SPHFluidSimulator:
    """
    Smoothed Particle Hydrodynamics (SPH) fluid simulator
    Implements real-time fluid dynamics using particle-based methods
    """
    
    def __init__(self, config: dict = None):
        self.config = config or FLUID_CONFIG
        self.boundary_config = BOUNDARY_CONFIG
        
        self.particles: List[Particle] = []
        self.num_particles = self.config['num_particles']
        self.rest_density = self.config['rest_density']
        self.gas_constant = self.config['gas_constant']
        self.viscosity = self.config['viscosity']
        self.gravity = np.array(self.config['gravity'], dtype=np.float32)
        self.smoothing_radius = self.config['smoothing_radius']
        self.h = self.smoothing_radius
        self.h2 = self.h * self.h
        self.dt = self.config['time_step']
        self.damping = self.config['damping']
        
        # Pre-compute SPH kernel constants
        self.poly6_constant = 315.0 / (64.0 * np.pi * self.h ** 9)
        self.spiky_constant = -45.0 / (np.pi * self.h ** 6)
        self.viscosity_constant = 45.0 / (np.pi * self.h ** 6)
        
        self._initialize_particles()
    
    def _initialize_particles(self):
        """Initialize particles in a grid formation"""
        self.particles = []
        
        # Calculate grid dimensions
        particles_per_dim = int(np.ceil(self.num_particles ** (1/3)))
        spacing = self.smoothing_radius * 0.8
        
        # Create particles in a cube
        count = 0
        for i in range(particles_per_dim):
            for j in range(particles_per_dim):
                for k in range(particles_per_dim):
                    if count >= self.num_particles:
                        break
                    
                    x = (i - particles_per_dim / 2) * spacing
                    y = (j - particles_per_dim / 2) * spacing + 0.5
                    z = (k - particles_per_dim / 2) * spacing
                    
                    self.particles.append(Particle([x, y, z]))
                    count += 1
                    
                if count >= self.num_particles:
                    break
            if count >= self.num_particles:
                break
    
    def _poly6_kernel(self, r2: float) -> float:
        """Poly6 kernel for density computation"""
        if r2 >= self.h2:
            return 0.0
        diff = self.h2 - r2
        return self.poly6_constant * diff * diff * diff
    
    def _spiky_gradient(self, r_vec: np.ndarray, r: float) -> np.ndarray:
        """Spiky kernel gradient for pressure forces"""
        if r >= self.h or r < 1e-6:
            return np.zeros(3, dtype=np.float32)
        diff = self.h - r
        return self.spiky_constant * diff * diff * (r_vec / r)
    
    def _viscosity_laplacian(self, r: float) -> float:
        """Viscosity kernel Laplacian for viscosity forces"""
        if r >= self.h:
            return 0.0
        return self.viscosity_constant * (self.h - r)
    
    def _compute_density_pressure(self):
        """Compute density and pressure for all particles"""
        for particle in self.particles:
            particle.density = 0.0
            
            # Sum contributions from all neighbors
            for neighbor in self.particles:
                r_vec = particle.position - neighbor.position
                r2 = np.dot(r_vec, r_vec)
                
                if r2 < self.h2:
                    particle.density += particle.mass * self._poly6_kernel(r2)
            
            # Compute pressure using equation of state
            particle.pressure = self.gas_constant * (particle.density - self.rest_density)
    
    def _compute_forces(self):
        """Compute pressure and viscosity forces"""
        for particle in self.particles:
            pressure_force = np.zeros(3, dtype=np.float32)
            viscosity_force = np.zeros(3, dtype=np.float32)
            
            for neighbor in self.particles:
                if particle is neighbor:
                    continue
                
                r_vec = particle.position - neighbor.position
                r = np.linalg.norm(r_vec)
                
                if r < self.h:
                    # Pressure force (symmetric)
                    pressure_term = (particle.pressure + neighbor.pressure) / (2.0 * neighbor.density)
                    pressure_force += particle.mass * pressure_term * self._spiky_gradient(r_vec, r)
                    
                    # Viscosity force
                    velocity_diff = neighbor.velocity - particle.velocity
                    viscosity_force += self.viscosity * particle.mass * (velocity_diff / neighbor.density) * self._viscosity_laplacian(r)
            
            # Total force
            particle.force = pressure_force + viscosity_force + (self.gravity * particle.density)
    
    def _integrate(self):
        """Integrate particle positions using semi-implicit Euler"""
        for particle in self.particles:
            # Update velocity
            acceleration = particle.force / particle.density
            particle.velocity += acceleration * self.dt
            
            # Apply damping
            particle.velocity *= self.damping
            
            # Update position
            particle.position += particle.velocity * self.dt
            
            # Handle boundary collisions
            self._handle_boundaries(particle)
    
    def _handle_boundaries(self, particle: Particle):
        """Handle collisions with boundaries"""
        min_bounds = np.array(self.boundary_config['min_bounds'])
        max_bounds = np.array(self.boundary_config['max_bounds'])
        restitution = self.boundary_config['restitution']
        
        for i in range(3):
            if particle.position[i] < min_bounds[i]:
                particle.position[i] = min_bounds[i]
                particle.velocity[i] *= -restitution
            elif particle.position[i] > max_bounds[i]:
                particle.position[i] = max_bounds[i]
                particle.velocity[i] *= -restitution
    
    def add_external_force(self, position: np.ndarray, radius: float, force: np.ndarray):
        """Apply external force to particles within a radius"""
        for particle in self.particles:
            r_vec = particle.position - position
            distance = np.linalg.norm(r_vec)
            
            if distance < radius:
                # Apply force with falloff
                falloff = 1.0 - (distance / radius)
                particle.velocity += force * falloff * self.dt
    
    def update(self, dt: float = None):
        """Update simulation by one time step"""
        if dt is not None:
            self.dt = dt
        
        self._compute_density_pressure()
        self._compute_forces()
        self._integrate()
    
    def get_particle_positions(self) -> np.ndarray:
        """Get all particle positions as numpy array"""
        return np.array([p.position for p in self.particles], dtype=np.float32)
    
    def get_particle_velocities(self) -> np.ndarray:
        """Get all particle velocities as numpy array"""
        return np.array([p.velocity for p in self.particles], dtype=np.float32)
    
    def reset(self):
        """Reset simulation to initial state"""
        self._initialize_particles()
