#!/usr/bin/env python3
import sqlite3
import os
import sys

# Path to database - adjusting relative to this script location or absolute
# Assuming script is in .../memtrack/ and db is in .../sys/
DB_PATH = "/home/ubuntu/code/gt/tgk/ubu/sys/mem_stats.db"

def get_db_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def main():
    target_time_str = "2026-01-16 18:54:02"
    print(f"Searching for snapshot before or at: {target_time_str}")

    conn = get_db_connection()
    c = conn.cursor()

    # Find the latest timestamp <= target_time
    c.execute("""
        SELECT timestamp 
        FROM memory_log 
        WHERE timestamp <= ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (target_time_str,))
    
    row = c.fetchone()
    
    if not row:
        print("No records found before the specified time.")
        conn.close()
        return

    found_time = row[0]
    print(f"Found snapshot at: {found_time}")
    print("-" * 60)
    print(f"{'PID':<8} {'User':<10} {'Command':<20} {'RSS (MB)':<10} {'%MEM':<8}")
    print("-" * 60)

    # Get top 10 for that timestamp
    c.execute("""
        SELECT pid, user, command, rss_mb, pmem 
        FROM memory_log 
        WHERE timestamp = ? 
        ORDER BY rss_mb DESC 
        LIMIT 10
    """, (found_time,))

    data = c.fetchall()
    
    for row in data:
        pid, user, command, rss_mb, pmem = row
        # Command might be long, truncate for display
        cmd_display = (command[:17] + '..') if len(command) > 17 else command
        print(f"{pid:<8} {user:<10} {cmd_display:<20} {rss_mb:<10.2f} {pmem:<8}")

    conn.close()

if __name__ == "__main__":
    main()
