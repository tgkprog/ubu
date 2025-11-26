#!/bin/bash
# Run system pause for optimization

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAUSE_SCRIPT="$SCRIPT_DIR/pauseSys.py"
REPORT_FILE="$SCRIPT_DIR/system_report.json"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "⚡ Optimizing System Resources..."
echo "=================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo"
    echo "Command: sudo $0"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$PAUSE_SCRIPT" ]; then
    echo "❌ Error: pauseSys.py not found at $PAUSE_SCRIPT"
    exit 1
fi

# Check if report exists
if [ ! -f "$REPORT_FILE" ]; then
    echo "❌ No system report found. Running report first..."
    "$SCRIPT_DIR/rreport.sh"
fi

# Check if script is executable
if [ ! -x "$PAUSE_SCRIPT" ]; then
    echo "🔧 Making pauseSys.py executable..."
    chmod +x "$PAUSE_SCRIPT"
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Python virtual environment not found. Run setup_env.sh first"
    echo "Command: ./setup_env.sh"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check Python and psutil
echo "🔍 Checking dependencies..."
python -c "import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ psutil not installed. Run setup_env.sh first"
    echo "Command: ./setup_env.sh"
    exit 1
fi

# Warn user
echo "⚠️  WARNING: This will stop non-essential processes"
echo "Essential processes (Node.js, Mongosh, terminals, etc.) will be preserved"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled"
    exit 1
fi

# Run the pause script
echo "🚀 Stopping non-essential processes..."
python "$PAUSE_SCRIPT"

# Deactivate virtual environment
deactivate

# Check if stop report was generated
if [ -f "$SCRIPT_DIR/stop_report.json" ]; then
    echo "=================================================="
    echo "✅ System optimization complete"
    echo "📄 Stop report location: $SCRIPT_DIR/stop_report.json"
else
    echo "❌ Error: System optimization failed"
    exit 1
fi