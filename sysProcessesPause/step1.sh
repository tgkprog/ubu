#!/bin/bash

# Wrapper script to run report.py and pauseSys.py sequentially
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Ensure virtual environment exists and is activated
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Please run setup_env.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

# Run the report script
python "$SCRIPT_DIR/report.py"
if [ $? -ne 0 ]; then
    echo "Error occurred while generating the system report. Exiting."
    exit 1
fi

# Run the pause script
python "$SCRIPT_DIR/pauseSys.py"
if [ $? -ne 0 ]; then
    echo "Error occurred while pausing system processes. Exiting."
    exit 1
fi

echo "System report generated and non-essential processes paused successfully."