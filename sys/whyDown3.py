#!/usr/bin/env python3
import sys
import subprocess
import os
import re
from datetime import datetime, timedelta

# Usage: sudo python3 whyDown3.py "Jan 14 01:24:31"

def run(cmd):
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return out.stdout.strip() if out.stdout else ""
    except Exception as e:
        return f"Error: {e}"

def parse_input_time(t_str):
    current_year = datetime.now().year
    formats = [
        "%b %d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(t_str, fmt)
            if fmt == "%b %d %H:%M:%S":
                dt = dt.replace(year=current_year)
                if dt > datetime.now() + timedelta(days=2):
                    dt = dt.replace(year=current_year - 1)
            return dt
        except ValueError:
            continue
    return None

def check_config(file_path, settings_of_interest):
    print(f"\n>> Checking {file_path} for policies...")
    if not os.path.exists(file_path):
        print(f"   (File {file_path} not found, using system defaults)")
        return

    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        found_any = False
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"): continue
            
            # Check if this line sets one of our interesting keys
            for key in settings_of_interest:
                if line.startswith(f"{key}="):
                    print(f"   [POLICY] Found active setting: {line}")
                    found_any = True
        
        if not found_any:
            print("   (No overriding policies found, system defaults apply)")
            
    except Exception as e:
        print(f"   Error reading config: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: whyDown3.py \"<timestamp>\"")
        sys.exit(1)

    t_input = sys.argv[1]
    event_dt = parse_input_time(t_input)
    if not event_dt:
        print(f"Error: Could not parse timestamp '{t_input}'.")
        sys.exit(1)

    print(f"\n=== SYSTEM DIAGNOSIS: {event_dt} ===")
    
    # 1. Policy Check
    # Defaults usually: HandleLidSwitch=suspend, IdleAction=ignore, KillUserProcesses=no (but widely yes on some distros)
    check_config("/etc/systemd/logind.conf", ["HandleLidSwitch", "HandleLidSwitchExternalPower", "IdleAction", "KillUserProcesses", "UserStopDelaySec"])
    check_config("/etc/systemd/system.conf", ["DefaultTimeoutStopSec"])

    # 2. Trigger Hunt
    # Window: +/- 2 minutes
    start_dt = event_dt - timedelta(minutes=2)
    end_dt = event_dt + timedelta(minutes=2)
    s_start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
    s_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n>> Analyzing Triggers in window: {s_start} to {s_end}...")
    
    cmd = ["journalctl", "--since", s_start, "--until", s_end]
    logs = run(cmd)
    
    triggers = {
        "LID_CLOSE": ["Lid closed", "Lid switch"],
        "POWER_BUTTON": ["Power key pressed", "Power button"],
        "SUSPEND": ["Suspending system", "Reached target Sleep", "systemd-suspend"],
        "IDLE": ["System is idle", "IdleAction"],
        "BATTERY": ["critical battery", "battery is low"],
        "CRON": [f"CRON[{event_dt.minute}"], # Heuristic: Cron runs at top of minute?
        "SYSTEM_STATE": ["Reached target Power-Off", "Stopped target Graphical Interface", "Stopping User Manager"]
    }
    
    matches = []
    
    if logs:
        # Check for Clustered Cron jobs (cron usually logs as CRON[pid]: ...)
        # We look for CRON lines that happen exactly at the minute of the event if event is near XX:XX:00
        # or just any cron in the window.
        
        for line in logs.splitlines():
            l_lower = line.lower()
            for t_name, keywords in triggers.items():
                for k in keywords:
                    if k.lower() in l_lower:
                        matches.append((t_name, line))
                        
            # Detect implicit Cron at the specific minute of death
            # e.g. if death is 01:24:31, look for Cron at 01:24:00+
            # CRON logs look like: Jan 14 01:25:01 ... CRON ...
            if "CRON" in line and f"{event_dt.hour:02}:{event_dt.minute:02}" in line:
                 matches.append(("CRON_EXACT_MINUTE", line))

    # Dedupe
    matches = sorted(list(set(matches)))
    
    if not matches:
        print("   No obvious physical or scheduled triggers found in logs.")
    else:
        print(f"   Found {len(matches)} potential trigger events:")
        for t_name, line in matches:
            print(f"   [{t_name}] {line}")

    print("\n=== INTERPRETATION ===")
    if any(m[0] == "LID_CLOSE" for m in matches):
        print("- Lid Close detected. If HandleLidSwitch=suspend/poweroff, this caused the stop.")
    if any(m[0] == "IDLE" for m in matches):
        print("- System Idle detected. IdleAction might be set to suspend or lock.")
    if any(m[0] == "CRON_EXACT_MINUTE" for m in matches):
        print("- Cron jobs ran at this minute. Check if any maintenance scripts kill users or restart services.")
    if any(m[0] == "SYSTEM_STATE" for m in matches):
        print("- System target changed (e.g. stopped Graphical Interface). This implies a high-level command (systemctl isolate/poweroff) or a critical failure propagation.")

    print("\n---------------------------------------------------------------")

if __name__ == "__main__":
    main()
