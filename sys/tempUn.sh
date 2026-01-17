#!/bin/bash

# Stop the service
sudo systemctl stop temperature-warn.service

# Disable the service (prevent it from starting on boot)
sudo systemctl disable temperature-warn.service

# Remove the service file
sudo rm /etc/systemd/system/temperature-warn.service

# Reload systemd daemon to recognize the removal
sudo systemctl daemon-reload

# Reset any failed state
sudo systemctl reset-failed

echo "Service stopped, disabled, and removed successfully"
