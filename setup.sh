#!/bin/bash

echo "========================================"
echo "Webcam Attendance System Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
echo "This may take several minutes..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating data directories..."
mkdir -p data/database
mkdir -p data/face_images
mkdir -p reports

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python main.py"
echo ""
echo "Note: On first run, you'll need to add people to the database"
echo "      before you can start attendance monitoring."
echo ""
