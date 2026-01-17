#!/usr/bin/env python3
"""
Test script for temperatureWarn.py
Tests the logging functionality without interfering with the running service
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temperatureWarn import get_detailed_temps, log_temperature, clean_old_log_entries
from datetime import datetime, timedelta

# Use a test log file to avoid conflicts
TEST_LOG = "/tmp/temp_test.log"

def test_get_temperatures():
    """Test reading temperature values from sensors"""
    print("=" * 60)
    print("TEST 1: Get Temperature Readings")
    print("=" * 60)
    temp1_first, edge_temp, temp1_second = get_detailed_temps()
    print(f"First temp1:  {temp1_first}°C")
    print(f"Edge temp:    {edge_temp}°C")
    print(f"Second temp1: {temp1_second}°C")
    return temp1_first, edge_temp, temp1_second

def test_logging(temp1_first, edge_temp, temp1_second):
    """Test logging functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Log Temperature to File")
    print("=" * 60)
    
    # Override LOG_FILE for testing
    import temperatureWarn
    temperatureWarn.LOG_FILE = TEST_LOG
    
    # Clear test log
    if os.path.exists(TEST_LOG):
        os.remove(TEST_LOG)
    
    # Log temperatures
    log_temperature(temp1_first, edge_temp, temp1_second)
    
    print(f"Log file: {TEST_LOG}")
    if os.path.exists(TEST_LOG):
        with open(TEST_LOG, "r") as f:
            content = f.read()
            print(f"Log entry: {content.strip()}")
    else:
        print("ERROR: Log file not created!")

def test_cleanup():
    """Test cleanup of old log entries"""
    print("\n" + "=" * 60)
    print("TEST 3: Cleanup Old Log Entries (>10 minutes)")
    print("=" * 60)
    
    # Override LOG_FILE for testing
    import temperatureWarn
    temperatureWarn.LOG_FILE = TEST_LOG
    
    # Create test entries with different timestamps
    with open(TEST_LOG, "w") as f:
        # Old entry (11 minutes ago - should be removed)
        old_time = datetime.now() - timedelta(minutes=11)
        f.write(f"{old_time.strftime('%H:%M')} temp1 50.0 critical edge : 60.0 2nd temp1 : 65.0\n")
        
        # Recent entry (5 minutes ago - should be kept)
        recent_time = datetime.now() - timedelta(minutes=5)
        f.write(f"{recent_time.strftime('%H:%M')} temp1 48.0 critical edge : 62.0 2nd temp1 : 66.0\n")
        
        # Current entry (should be kept)
        current_time = datetime.now()
        f.write(f"{current_time.strftime('%H:%M')} temp1 46.0 critical edge : 66.0 2nd temp1 : 66.6\n")
    
    print("Before cleanup:")
    with open(TEST_LOG, "r") as f:
        for line in f:
            print(f"  {line.strip()}")
    
    # Run cleanup
    clean_old_log_entries()
    
    print("\nAfter cleanup (entries >10 min removed):")
    with open(TEST_LOG, "r") as f:
        for line in f:
            print(f"  {line.strip()}")

def test_custom_log_file():
    """Test running script with custom log file argument"""
    print("\n" + "=" * 60)
    print("TEST 4: Custom Log File Argument")
    print("=" * 60)
    
    import subprocess
    import time
    
    # Run with --help to show usage
    result = subprocess.run([
        "python3",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "temperatureWarn.py"),
        "--help"
    ], capture_output=True, text=True)
    
    print("Usage:")
    print(result.stdout)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEMPERATURE WARN TEST SUITE")
    print("=" * 60)
    print(f"Test log file: {TEST_LOG}")
    print(f"Service log file: /tmp/temp.log (untouched)")
    print()
    
    # Run tests
    temps = test_get_temperatures()
    test_logging(*temps)
    test_cleanup()
    test_custom_log_file()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    
    # Cleanup test file
    if os.path.exists(TEST_LOG):
        os.remove(TEST_LOG)
        print(f"Cleaned up test log: {TEST_LOG}")
