#!/bin/bash

# Wrapper script to run the restart functionality
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Ensure virtual environment exists and is activated
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Please run setup_env.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Run the restart script
python "$SCRIPT_DIR/restart.py"

# Check exit status
if [ $? -eq 0 ]; then
    echo "System processes restored successfully"
else
    echo "Error occurred while restoring system processes"
    exit 1
fi