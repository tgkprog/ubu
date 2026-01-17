#!/usr/bin/env python3
import sqlite3
import subprocess
import os
import sys
from datetime import datetime, timedelta

# Configuration
DB_PATH = "/home/ubuntu/code/gt/tgk/ubu/sys/mem_stats.db"

def get_db_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def get_last_logout_time():
    user = os.environ.get('SUDO_USER') or os.environ.get('USER')
    if not user:
        print("Error: Could not determine user.")
        sys.exit(1)

    try:
        # last -F returns full date/time. -n 10 to check recent history.
        # Format example:
        # user     pts/0        192.168.1.5      Tue Jan 14 03:52:19 2026 - Tue Jan 14 03:52:25 2026  (00:00)
        output = subprocess.check_output(["last", "-F", "-n", "20", user], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running last: {e}")
        sys.exit(1)

    lines = output.strip().split('\n')
    for line in lines:
        if "still logged in" in line:
            continue
        
        # We need the logout time relative to the line structure.
        # The line format is fixed width usually, but let's parse by " - " separator for the time range.
        if " - " in line:
            parts = line.split(" - ")
            if len(parts) < 2: continue
            
            # The second part starts with the logout timestamp
            # "Tue Jan 14 03:52:25 2026  (00:00)"
            # We want "Tue Jan 14 03:52:25 2026"
            logout_part = parts[1].strip()
            
            # Extract timestamp. It's usually 24 chars: "Tue Jan 14 03:52:25 2026"
            # But let's be safer by splitting by '(' usually present for duration
            time_str = logout_part.split('(')[0].strip()
            
            try:
                # Parse: "Tue Jan 14 03:52:25 2026"
                logout_time = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
                return logout_time
            except ValueError:
                continue

    return None

def get_memory_stats(conn, target_time):
    # Find the closest snapshot to target_time
    # We look for a record with the smallest time difference
    
    target_str = target_time.strftime("%Y-%m-%d %H:%M:%S")
    c = conn.cursor()
    
    # First, find the closest distinct timestamp
    c.execute("""
        SELECT timestamp 
        FROM memory_log 
        ORDER BY ABS(strftime('%s', timestamp) - strftime('%s', ?)) ASC 
        LIMIT 1
    """, (target_str,))
    
    row = c.fetchone()
    if not row:
        return None, []
    
    actual_time_str = row[0]
    
    # Now fetch the top 10 processes for that timestamp
    c.execute("""
        SELECT pid, command, rss_mb, pmem 
        FROM memory_log 
        WHERE timestamp = ? 
        ORDER BY rss_mb DESC 
        LIMIT 10
    """, (actual_time_str,))
    
    data = c.fetchall()
    return datetime.strptime(actual_time_str, "%Y-%m-%d %H:%M:%S"), data

def print_table(title, data, timestamp):
    print(f"\n{title} (Snapshot: {timestamp})")
    print(f"{'PID':<8} {'Name':<25} {'Mem (MB)':<12} {'Mem %':<8}")
    print("-" * 55)
    
    for pid, name, rss, pmem in data:
        # Truncate name if too long
        name_disp = (name[:22] + '..') if len(name) > 22 else name
        print(f"{pid:<8} {name_disp:<25} {rss:<12.2f} {pmem:<8.1f}")

def main():
    print(" Analyzing memory usage around last logout...")
    
    logout_time = get_last_logout_time()
    if not logout_time:
        print("Could not find a valid previous logout time for the current user.")
        sys.exit(0)
        
    print(f" Detected Last Logout: {logout_time}")
    
    conn = get_db_connection()
    
    
    # Time 1: Logout time
    ts1, data1 = get_memory_stats(conn, logout_time)
    
    # Time 2: 40 minutes before logout
    target_time_pre = logout_time - timedelta(minutes=40)
    ts2, data2 = get_memory_stats(conn, target_time_pre)
    
    if ts1:
        delta = abs((ts1 - logout_time).total_seconds()) / 60
        warning = ""
        if delta > 5:
            warning = f" [WARNING: Data is {delta:.1f} mins away from target]"
        print_table(f"TOP 10 APPS AT LOGOUT{warning}", data1, ts1)
    else:
        print(f"\nNo data found near logout time ({logout_time})")
        
    if ts2:
        delta = abs((ts2 - target_time_pre).total_seconds()) / 60
        warning = ""
        if delta > 5:
            warning = f" [WARNING: Data is {delta:.1f} mins away from target]"
        print_table(f"TOP 10 APPS 40 MINS PRIOR{warning}", data2, ts2)
    else:
        print(f"\nNo data found near 40 mins prior ({target_time_pre})")

        
    conn.close()

if __name__ == "__main__":
    main()
