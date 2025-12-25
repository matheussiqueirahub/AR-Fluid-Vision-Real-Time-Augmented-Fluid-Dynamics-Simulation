"""
Simple test script to verify the AR Fluid Vision system works
Tests without requiring camera or display
"""

import numpy as np
import sys

def test_config():
    """Test configuration import"""
    print("Testing configuration...")
    import config
    assert hasattr(config, 'FLUID_CONFIG')
    assert hasattr(config, 'VISION_CONFIG')
    assert hasattr(config, 'RENDER_CONFIG')
    print("✓ Configuration loaded successfully")


def test_fluid_physics():
    """Test fluid physics simulation"""
    print("\nTesting fluid physics...")
    from src.fluid_physics import SPHFluidSimulator, Particle
    
    # Create simulator
    sim = SPHFluidSimulator()
    assert len(sim.particles) > 0
    print(f"✓ Created simulator with {len(sim.particles)} particles")
    
    # Get initial state
    initial_pos = sim.get_particle_positions()
    assert initial_pos.shape == (len(sim.particles), 3)
    
    # Update simulation
    for i in range(5):
        sim.update()
    
    # Check particles moved
    final_pos = sim.get_particle_positions()
    distance_moved = np.linalg.norm(final_pos - initial_pos, axis=1).mean()
    assert distance_moved > 0, "Particles should have moved"
    print(f"✓ Particles moved {distance_moved:.4f} units in 5 steps")
    
    # Test external force
    sim.add_external_force(
        position=np.array([0.0, 0.0, 0.0]),
        radius=0.3,
        force=np.array([10.0, 0.0, 0.0])
    )
    sim.update()
    print("✓ External force applied successfully")
    
    # Test reset
    sim.reset()
    assert len(sim.particles) == len(initial_pos)
    print("✓ Simulation reset successfully")


def test_utils():
    """Test utility functions"""
    print("\nTesting utilities...")
    from src.utils import FPSCounter, PerformanceMonitor, normalize_vector
    
    # Test FPS counter
    fps_counter = FPSCounter()
    for i in range(5):
        import time
        time.sleep(0.01)
        fps = fps_counter.update()
    assert fps > 0
    print(f"✓ FPS Counter working: {fps:.1f} FPS")
    
    # Test performance monitor
    monitor = PerformanceMonitor()
    monitor.start_timer('test')
    import time
    time.sleep(0.01)
    elapsed = monitor.end_timer('test')
    assert elapsed > 0
    print(f"✓ Performance Monitor working: {elapsed*1000:.2f}ms")
    
    # Test normalize_vector
    vec = np.array([3.0, 4.0, 0.0])
    normalized = normalize_vector(vec)
    assert abs(np.linalg.norm(normalized) - 1.0) < 1e-6
    print("✓ Vector normalization working")


def test_ar_renderer():
    """Test AR renderer (without display)"""
    print("\nTesting AR renderer...")
    from src.ar_renderer import ARFluidRenderer, SimpleRenderer
    
    # Create renderer
    renderer = ARFluidRenderer()
    print("✓ AR Renderer created")
    
    # Create dummy frame and positions
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    positions_2d = np.array([
        [100, 100],
        [200, 200],
        [300, 300]
    ], dtype=np.float32)
    
    # Render (should not crash)
    rendered = renderer.render_particles_2d(frame, positions_2d)
    assert rendered.shape == frame.shape
    print("✓ Particle rendering working")
    
    # Test HUD
    rendered_with_hud = renderer.add_hud(rendered, fps=60.0, particle_count=100)
    assert rendered_with_hud.shape == frame.shape
    print("✓ HUD rendering working")


def test_integration():
    """Test basic integration of components"""
    print("\nTesting component integration...")
    from src.fluid_physics import SPHFluidSimulator
    from src.ar_renderer import SimpleRenderer
    
    # Create components
    simulator = SPHFluidSimulator()
    renderer = SimpleRenderer()
    
    # Simulate and render
    simulator.update()
    positions = simulator.get_particle_positions()
    
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    rendered = renderer.render(frame, positions)
    
    assert rendered.shape == frame.shape
    print("✓ Simulator + Renderer integration working")


def main():
    """Run all tests"""
    print("=" * 60)
    print("AR Fluid Vision - System Test")
    print("=" * 60)
    
    try:
        test_config()
        test_fluid_physics()
        test_utils()
        test_ar_renderer()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)
        print("\nThe system is working correctly.")
        print("Run 'python main.py' to start the full AR application.")
        print("Note: Camera and MediaPipe are required for full AR features.")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
