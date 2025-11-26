#!/bin/bash
# Run system resource report

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_SCRIPT="$SCRIPT_DIR/report.py"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "📊 Running System Resource Report..."
echo "=================================================="

# Check if Python script exists
if [ ! -f "$REPORT_SCRIPT" ]; then
    echo "❌ Error: report.py not found at $REPORT_SCRIPT"
    exit 1
fi

# Check if script is executable
if [ ! -x "$REPORT_SCRIPT" ]; then
    echo "🔧 Making report.py executable..."
    chmod +x "$REPORT_SCRIPT"
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

# Run the report
echo "🚀 Generating system resource report..."
python "$REPORT_SCRIPT"

# Deactivate virtual environment
deactivate

# Check if report was generated
if [ -f "$SCRIPT_DIR/system_report.json" ]; then
    echo "=================================================="
    echo "✅ Report generated successfully"
    echo "📄 Report location: $SCRIPT_DIR/system_report.json"
else
    echo "❌ Error: Report generation failed"
    exit 1
fi