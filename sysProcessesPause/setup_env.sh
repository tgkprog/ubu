#!/bin/bash
# Install dependencies for system load management scripts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "🔧 Setting up Python environment for system load management..."
echo "=================================================="

# Check Python3 installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3 first."
    exit 1
fi

# Install required system packages
echo "📦 Installing required system packages..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-full

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies in virtual environment..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install psutil

# Verify installations
echo "✅ Verifying installations..."
python -c "import psutil" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ psutil installed successfully"
else
    echo "❌ Error: psutil installation failed"
    exit 1
fi

# Create wrapper scripts that use the virtual environment
echo "🔧 Creating wrapper scripts..."

echo "=================================================="
echo "✅ All dependencies installed successfully"
echo "You can now comment out the installation commands in this script"