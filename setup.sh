#!/bin/bash
# Primordial Garden - Quick Setup Script

echo "=================================="
echo "Primordial Garden - Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

echo ""
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "To run the simulation:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or use the run.sh script:"
echo "  ./run.sh"
echo ""
echo "Controls:"
echo "  SPACE: Pause/Resume"
echo "  1-5: Speed control"
echo "  S: Toggle stats"
echo "  R: Reset"
echo "  Q: Quit"
echo ""
