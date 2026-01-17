#!/usr/bin/env python3
"""
Test the enhanced notify function with GUI window and process killing
"""
import sys
sys.path.insert(0, '/home/ubuntu/code/gt/tgk/ubu/sys')

from temperatureWarn import notify, THRESHOLD, CRITICAL

print("=" * 60)
print("TESTING ENHANCED NOTIFY FUNCTION")
print("=" * 60)
print(f"THRESHOLD: {THRESHOLD}°C")
print(f"CRITICAL:  {CRITICAL}°C")
print()

# Test with temperature just above threshold but below critical
print("Test 1: Temperature above THRESHOLD but below CRITICAL")
print(f"Testing with {THRESHOLD + 1}°C...")
print("Should show orange window and notification, but NOT kill processes")
print()

# Uncomment to test the window (will show for 5 seconds)
# notify(THRESHOLD + 1)
# import time
# time.sleep(6)

# Test with critical temperature
print("Test 2: Temperature above CRITICAL")
print(f"Testing with {CRITICAL + 1}°C...")
print("Should show RED window, notification, AND kill processes")
print()

# Uncomment to test critical behavior (WARNING: will kill processes!)
# notify(CRITICAL + 1)
# import time
# time.sleep(6)

print("Tests defined but not executed (uncomment to run)")
print("To restart service after changes: sudo systemctl restart temperature-warn")
