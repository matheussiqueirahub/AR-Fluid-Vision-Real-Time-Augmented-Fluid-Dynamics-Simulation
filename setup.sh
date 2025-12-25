#!/bin/bash

# Setup script for AR Fluid Vision
# This script helps set up the development environment

echo "=========================================="
echo "AR Fluid Vision - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi
echo "✓ Python version is compatible"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Run system test
echo "Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Run the demo (no camera required):"
    echo "   python demo.py"
    echo ""
    echo "3. Run the full AR application (requires camera):"
    echo "   python main.py"
    echo ""
    echo "4. Run examples:"
    echo "   python examples/basic_simulation.py"
    echo "   python examples/test_gesture_recognition.py"
    echo "   python examples/test_aruco_detection.py"
    echo ""
else
    echo ""
    echo "Setup completed with errors. Please check the output above."
    exit 1
fi
