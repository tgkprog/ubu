#!/usr/bin/env python3
import subprocess
from datetime import datetime

LOG_FILE = "/tmp/temp_debug3.log"

print("Testing detailed parsing (matching temperatureWarn.py)...")

# Get sensors output
sensors_output = subprocess.check_output(["sensors"], text=True)
lines = sensors_output.splitlines()

# Extract key information (matching the script)
temp1_iwlwifi = None
temp1_k10temp = None
edge = None
cpu_fan = None
gpu_fan = None
power1 = None
power1_avg = None
power1_crit = None

i = 0
iteration_count = 0
MAX_ITERATIONS = 1000

print(f"Total lines to parse: {len(lines)}")

while i < len(lines):
    iteration_count += 1
    if iteration_count > MAX_ITERATIONS:
        print(f"ERROR: Hit max iterations ({MAX_ITERATIONS})! Infinite loop detected!")
        print(f"  Current i={i}, len(lines)={len(lines)}")
        print(f"  Current line: {lines[i] if i < len(lines) else 'OUT OF BOUNDS'}")
        break
    
    line = lines[i]
    
    # Power - THIS IS THE SUSPECT
    if "power1:" in line and "mW" in line:
        print(f"Line {i}: Found power1 line: {line}")
        parts = line.split()
        power1 = " ".join(parts[1:3])
        print(f"  power1 = {power1}")
        
        if "avg" in line:
            print(f"  Found 'avg' in line")
            avg_start = line.index("avg")
            avg_section = line[avg_start:]
            avg_parts = avg_section.split()
            if len(avg_parts) >= 3:
                power1_avg = " ".join(avg_parts[2:4])
                print(f"  power1_avg = {power1_avg}")
        
        if i + 1 < len(lines) and "crit" in lines[i + 1]:
            print(f"  Checking next line for crit: {lines[i + 1]}")
            crit_line = lines[i + 1]
            crit_parts = crit_line.split()
            for j, p in enumerate(crit_parts):
                if "W" in p and j > 0:
                    power1_crit = " ".join(crit_parts[j-1:j+1])
                    print(f"  power1_crit = {power1_crit}")
                    break
    
    i += 1

print(f"\n✓ Successfully completed after {iteration_count} iterations")
print(f"  power1: {power1}")
print(f"  power1_avg: {power1_avg}")
print(f"  power1_crit: {power1_crit}")
