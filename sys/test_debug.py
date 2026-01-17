#!/usr/bin/env python3
import subprocess
from datetime import datetime

LOG_FILE = "/tmp/temp_debug2.log"

print("Starting test...")

# Get sensors output
print("1. Getting sensors output...")
sensors_output = subprocess.check_output(["sensors"], text=True)
print(f"   Got {len(sensors_output)} bytes")

# Parse sensors output for specific values
print("2. Parsing sensors output...")
lines = sensors_output.splitlines()
print(f"   Got {len(lines)} lines")

i = 0
line_count = 0
while i < len(lines):
    line = lines[i]
    line_count += 1
    if line_count > 100:  # Safety check
        print(f"   ERROR: Processed {line_count} iterations, seems like infinite loop!")
        break
    i += 1

print(f"   Successfully parsed {line_count} lines")

# Try to write to log file
print("3. Writing to log file...")
try:
    with open(LOG_FILE, "w") as f:
        f.write("Test log entry\n")
    print(f"   ✓ Log file written to {LOG_FILE}")
except Exception as e:
    print(f"   ERROR writing log: {e}")

print("Done!")
