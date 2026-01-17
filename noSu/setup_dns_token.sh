#!/bin/bash
set -e

SCRIPT_PATH="/home/ubuntu/b/dns"
SUDOERS_FILE="/etc/sudoers.d/reachme-dns-bypass"

# 1. Verify script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script $SCRIPT_PATH not found!"
    exit 1
fi

# 2. Configure sudoers to allow passwordless execution
# Check if we already have permissions or need to ask for password (this script requires sudo to run)
echo "Setting up passwordless sudo execution for $SCRIPT_PATH..."
echo "You may be asked for your sudo password to apply this configuration."

# Write the sudoers file
# using tee to write as root
echo "ubuntu ALL=(ALL) NOPASSWD: $SCRIPT_PATH" | sudo tee $SUDOERS_FILE > /dev/null

# Set correct permissions (must be 0440)
sudo chmod 0440 $SUDOERS_FILE

echo "Successfully created $SUDOERS_FILE"

# 3. Add to login script (.profile)
LOGIN_SCRIPT="/home/ubuntu/.profile"

if grep -q "$SCRIPT_PATH" "$LOGIN_SCRIPT"; then
    echo "Entry already exists in $LOGIN_SCRIPT"
else
    echo "Adding execution entry to $LOGIN_SCRIPT..."
    echo "" >> "$LOGIN_SCRIPT"
    echo "# Run DNS setup automatically on login with sudo" >> "$LOGIN_SCRIPT"
    echo "sudo $SCRIPT_PATH" >> "$LOGIN_SCRIPT"
    echo "Added to $LOGIN_SCRIPT"
fi

echo "Setup complete!"
echo "The script will now run automatically on login."
echo "You can also run it manually without a password using: sudo $SCRIPT_PATH"
