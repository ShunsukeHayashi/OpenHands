#!/bin/bash
# Setup script for DevinAgent environment

# Create a virtual environment
echo "Creating virtual environment..."
python -m venv devin_env

# Activate the virtual environment
echo "Activating virtual environment..."
source devin_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the OpenHands package in development mode
echo "Installing OpenHands in development mode..."
cd ../../../../
pip install -e .

echo "Setup complete!"
