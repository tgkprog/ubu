#!/usr/bin/env python3
import sqlite3
import subprocess
import datetime
import os
import sys

# Configuration
DB_PATH = "/home/ubuntu/code/gt/tgk/ubu/sys/mem_stats.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            pid INTEGER,
            user TEXT,
            command TEXT,
            rss_mb REAL,
            pmem REAL
        )
    ''')
    conn.commit()
    return conn

def get_top_memory_processes(limit=10):
    # ps -eo pid,user,rss,%mem,comm --sort=-rss
    cmd = ["ps", "-eo", "pid,user,rss,%mem,comm", "--sort=-rss"]
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True).stdout
    except Exception as e:
        print(f"Error running ps: {e}")
        return []

    processes = []
    lines = out.strip().split("\n")[1:] # Skip header
    
    for line in lines[:limit]:
        parts = line.split(maxsplit=4)
        if len(parts) < 5: continue
        
        try:
            pid = int(parts[0])
            user = parts[1]
            rss_kb = float(parts[2])
            pmem = float(parts[3])
            comm = parts[4]
            
            rss_mb = rss_kb / 1024.0
            processes.append((pid, user, comm, rss_mb, pmem))
        except ValueError:
            continue
            
    return processes

def log_to_db(conn, processes):
    c = conn.cursor()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for p in processes:
        pid, user, comm, rss_mb, pmem = p
        c.execute('''
            INSERT INTO memory_log (timestamp, pid, user, command, rss_mb, pmem)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ts, pid, user, comm, rss_mb, pmem))
    
    conn.commit()
    print(f"Logged {len(processes)} processes at {ts}")

def main():
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = init_db()
    top_procs = get_top_memory_processes(10)
    log_to_db(conn, top_procs)
    conn.close()

if __name__ == "__main__":
    main()
