#!/usr/bin/env python3
import sys
import subprocess
from datetime import datetime, timedelta

# Usage: sudo python3 checkTime.py "Jan 14 01:24:31" [minutes_before] [minutes_after]

def run(cmd):
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return out.stdout.strip() if out.stdout else ""
    except Exception as e:
        return f"Error: {e}"

def parse_input_time(t_str):
    # Try multiple formats
    # 1. Syslog style: Jan 14 01:24:31 (assumes current year)
    current_year = datetime.now().year
    formats = [
        "%b %d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(t_str, fmt)
            # If format excludes year, add it
            if fmt == "%b %d %H:%M:%S":
                dt = dt.replace(year=current_year)
                # Handle future/past rollover if needed (simple heuristic: if > 2 days in future, it's last year)
                if dt > datetime.now() + timedelta(days=2):
                    dt = dt.replace(year=current_year - 1)
            return dt
        except ValueError:
            continue
            
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: checkTime.py \"<timestamp>\" [minutes_before] [minutes_after]")
        print("Example: checkTime.py \"Jan 14 01:24:31\"")
        sys.exit(1)

    t_input = sys.argv[1]
    
    # Optional ranges
    mins_before = 5
    mins_after = 1
    if len(sys.argv) > 2: mins_before = int(sys.argv[2])
    if len(sys.argv) > 3: mins_after = int(sys.argv[3])

    target_dt = parse_input_time(t_input)
    if not target_dt:
        print(f"Error: Could not parse timestamp '{t_input}'. Try 'MMM DD HH:MM:SS' or 'YYYY-MM-DD HH:MM:SS'.")
        sys.exit(1)

    start_dt = target_dt - timedelta(minutes=mins_before)
    end_dt = target_dt + timedelta(minutes=mins_after)

    s_start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    s_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n=== POINT-IN-TIME ANALYSIS ===")
    print(f"Target Event: {target_dt}")
    print(f"Scanning Logs: {s_start} -> {s_end}")
    print("---------------------------------------------------------------")

    cmd = ["journalctl", "--since", s_start, "--until", s_end]
    logs = run(cmd)
    
    if not logs:
        print("No logs found in this window.")
    else:
        # Simple highlighting
        for line in logs.splitlines():
            l_lower = line.lower()
            prefix = "  "
            
            # Highlight interesting things
            if any(x in l_lower for x in ["error", "fail", "kill", "segfault", "warn", "critical"]):
                prefix = ">>"
            if "systemd" in l_lower and ("stopping" in l_lower or "stopped" in l_lower):
                prefix = "**"
                
            print(f"{prefix} {line}")

    print("---------------------------------------------------------------")

if __name__ == "__main__":
    main()
