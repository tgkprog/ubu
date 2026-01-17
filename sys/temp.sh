#!/bin/bash
# Script to kill stuck temperatureWarn.py and restart the service

echo "================================================"
echo "Temperature Warn Service Restart Script"
echo "================================================"
echo ""

# 1. Kill any stuck temperatureWarn.py processes
echo "Step 1: Killing any stuck temperatureWarn.py processes..."
pkill -9 -f temperatureWarn.py
sleep 1

# Verify processes are killed
REMAINING=$(ps aux | grep temperatureWarn.py | grep -v grep | wc -l)
if [ $REMAINING -eq 0 ]; then
    echo "  ✓ All temperatureWarn.py processes killed"
else
    echo "  ⚠ Warning: $REMAINING processes still running"
    ps aux | grep temperatureWarn.py | grep -v grep
fi
echo ""

# 2. Clear old log file
echo "Step 2: Clearing old log file..."
if [ -f /tmp/temp.log ]; then
    echo "  Old log content:"
    cat /tmp/temp.log | head -5
    rm -f /tmp/temp.log
    echo "  ✓ Log file cleared"
else
    echo "  ℹ No log file to clear"
fi
echo ""

# 3. Reload systemd daemon
echo "Step 3: Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "  ✓ Daemon reloaded"
echo ""

# 4. Restart the service
echo "Step 4: Restarting temperature-warn service..."
sudo systemctl restart temperature-warn
sleep 2
echo "  ✓ Service restart command issued"
echo ""

# 5. Check service status
echo "Step 5: Checking service status..."
sudo systemctl status temperature-warn --no-pager -l
echo ""

# 6. Check for running processes
echo "Step 6: Checking for new temperatureWarn.py process..."
ps aux | grep temperatureWarn.py | grep -v grep
echo ""

# 7. Wait and check log file
echo "Step 7: Waiting 5 seconds for log file to be created..."
sleep 5
if [ -f /tmp/temp.log ]; then
    echo "  ✓ Log file exists!"
    echo "  Latest log entries:"
    tail -20 /tmp/temp.log
else
    echo "  ✗ Log file NOT created - service may have issues!"
fi
echo ""

echo "================================================"
echo "Restart Complete!"
echo "================================================"
echo ""
echo "To monitor logs in real-time, run:"
echo "  tail -f /tmp/temp.log"
echo ""
echo "To check service logs:"
echo "  sudo journalctl -u temperature-warn -f"
