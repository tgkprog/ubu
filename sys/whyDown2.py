#!/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime, timedelta

# Usage: sudo python3 whyDown2.py [minutes]
# Default: 30 minutes

def run(cmd, timeout=10):
    try:
        # journalctl sometimes returns non-zero if no entries found, handle gracefully
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return out.stdout.strip() if out.stdout else ""
    except Exception as e:
        return f"Error running command {' '.join(cmd)}: {e}"

def find_patterns(text, patterns):
    hits = []
    if not text:
        return hits
    for line in text.split("\n"):
        for p in patterns:
            if p.lower() in line.lower():
                hits.append(line.strip())
    return hits

def parse_timestamp(log_line):
    """
    Attempts to parse timestamp from a log line.
    Supports:
    - ISO8601 (e.g. 2026-01-14T01:24:53...)
    - Syslog (e.g. Jan 14 01:24:54) - assumes current year
    """
    try:
        parts = log_line.split()
        if not parts: return None
        
        # Try ISO first (starts with 20YY-)
        # [Source] 2026-01-14T...
        # We need to strip the "[Source]" prefix if present in the finding string, 
        # but here we might receive the raw line or the formatted finding.
        # Let's clean up the line first.
        
        clean_line = log_line
        if log_line.startswith("["):
            # Remove [Source] prefix
            if "]" in log_line:
                clean_line = log_line.split("]", 1)[1].strip()

        parts = clean_line.split()
        if not parts: return None
        first_token = parts[0]

        if "T" in first_token and "-" in first_token:
            # ISO format: 2026-01-14T02:08:49.330790+05:30
            # Simplify by taking first 19 chars: YYYY-MM-DDTHH:MM:SS
            ts_str = first_token[:19]
            return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")

        # Try Syslog: Jan 14 01:24:54
        if len(parts) >= 3:
            month_str = parts[0]
            day_str = parts[1]
            time_str = parts[2]
            current_year = datetime.now().year
            ts_str = f"{current_year} {month_str} {day_str} {time_str}"
            try:
                dt = datetime.strptime(ts_str, "%Y %b %d %H:%M:%S")
                # Handle year rollover if needed (not perfect but decent for recent logs)
                if dt > datetime.now() + timedelta(days=2):
                    dt = dt.replace(year=current_year - 1)
                return dt
            except ValueError:
                pass
                
        return None
    except Exception:
        return None

def analyze_pre_logout(logout_time):
    start_time = logout_time - timedelta(minutes=10)
    end_time = logout_time
    
    s_start = start_time.strftime("%Y-%m-%d %H:%M:%S")
    s_end = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n=== PRE-LOGOUT CONTEXT (Errors 10 mins before last logout) ===")
    print(f"Window: {s_start} to {s_end}")
    
    # Check for logs with Priority <= 3 (Error)
    # Using json output for reliable parsing? No, standard text is consistent enough here with run()
    cmd = ["journalctl", "--since", s_start, "--until", s_end, "-p", "3"]
    errors = run(cmd)
    
    if not errors or "No entries" in errors:
        print("No system errors (priority <= 3) found in journal.")
    else:
        print(f"Found Critical/Error logs:")
        lines = errors.splitlines()
        for l in lines:
            print(f"  {l}") 


    # Also search for 'killer', 'segfault' in standard range (priority 3 misses some things)
    print("\nScanning for deeper failure patterns (segfault, kill, etc) in that window...")
    
    # Expanded suspicious patterns
    suspicious_patterns = [
        "segfault", "killed process", "oom-killer", "call trace", "stack trace", "hardware error",
        "gnome-shell", "gnome-session", "Wayland", "Xorg", # Desktop environment crashes
        "systemd-sleep", "suspend", "hibernate", "lid closed", # Power events
        "killed by", "signal 15", "signal 9", "oom_reaper", "Out of memory", # Kill signals
        "systemd-oomd" # User-space OOM killer
    ]
    
    # We grab all logs for that window
    full_logs_cmd = ["journalctl", "--since", s_start, "--until", s_end]
    full_logs = run(full_logs_cmd)
    
    found_suspicious = False
    if full_logs:
        # We want to be a bit smarter than just "is str in line" for some of these common words
        # e.g. "Wayland" might appear in normal logs. 
        # But for now, we'll list them and let the user judge or refine
        hits = []
        for line in full_logs.split("\n"):
            line_lower = line.lower()
            for p in suspicious_patterns:
                if p.lower() in line_lower:
                    # Filter out some common noise if needed, but for "Why Down" usually verbosity is okay
                    # if it's in the 10 mins before death.
                    hits.append(line.strip())
                    break
        
        if hits:
            found_suspicious = True
            print(f"Found {len(hits)} suspicious or relevant event logs:")
            # Show last 20 if too many
            show_hits = hits[-20:] if len(hits) > 20 else hits
            for h in show_hits:
                print(f"  [LOG] {h}")
            if len(hits) > 20:
                print(f"  ... (and {len(hits)-20} more)")
    
    if not found_suspicious and (not errors or "No entries" in errors):
        print("No obvious error patterns found preceding the logout.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
        print("Usage: whyDown2.py [minutes]")
        print("Scans system logs for logout events in the last N minutes.")
        print("Default: 30 minutes.")
        print("Parameter 'minutes': The time window in minutes to look back for events.")
        sys.exit(0)

    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    since_time = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n=== LOGOUT CHECK (Last {minutes} mins) ===")
    print(f"Time Now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Searching for logout events since {since_time}...")
    print(f"(Parameter '{minutes}' means we are checking the last {minutes} minutes)\n")
    
    # Logout Patterns
    logout_patterns = {
        "SESSION_CLOSED": [
            "session closed for user",
            "Removed session",
            "pam_unix(sshd:session): session closed",
            "logged out",
            "systemd-logind: removed session"
        ]
    }

    all_findings = []

    def scan_log_source(source_name, log_text):
        found_issues = False
        for category, patterns in logout_patterns.items():
            hits = find_patterns(log_text, patterns)
            if hits:
                for h in hits: 
                    # Filter out noise: Cron jobs and Sudo commands create sessions that "close" frequently
                    if "cron:session" in h or "sudo:session" in h:
                        continue
                    found_issues = True
                    all_findings.append(f"[{source_name}] {h}")
        return found_issues

    print("\n[LOG ANALYSIS]")
    
    # Journalctl current
    # We use 'journalctl' without -xe to catch info logs which logouts usually are
    print(">> Scanning system journal...")
    j_current = run(["journalctl", "--since", since_time])
    scan_log_source("Journal", j_current)
    
    # /var/log/auth.log check if exists
    if os.path.exists("/var/log/auth.log"):
        print(">> Scanning /var/log/auth.log...")
        try:
             # We tail 5000 lines to ensure coverage, but filter by simple string matching
             # Ideally we should parse timestamps but for this tool simple grep is acceptable overlap
             auth_tail = run(["tail", "-n", "5000", "/var/log/auth.log"])
             scan_log_source("AuthLog", auth_tail)
        except: pass

    # Report
    print("\n=== FINDINGS SUMMARY ===")
    
    unique_findings = sorted(list(set(all_findings)))
    last_logout_dt = None
    
    if not unique_findings:
        print(f"No logout events found in the last {minutes} minutes.")
    else:
        print(f"Found {len(unique_findings)} logout-related entries:")
        for f in unique_findings:
            print(f" {f}")
            
        # Determine the most relevant logout time to analyze
        # Priority:
        # 1. Last logout of the specific user (if we can detect who ran sudo)
        # 2. Last logout of any normal user (exclude gdm, root if possible)
        # 3. Last logout overall
        
        target_user = os.environ.get('SUDO_USER') or os.environ.get('USER')
        
        # Filter for specific user if possible
        user_specific_findings = []
        if target_user and target_user not in ['root', 'gdm']:
             print(f"\nFocusing on logout events for user: '{target_user}'...")
             user_specific_findings = [f for f in unique_findings if f"for user {target_user}" in f]
        
        findings_to_check = user_specific_findings if user_specific_findings else unique_findings
        
        if user_specific_findings:
             print(f"Found {len(user_specific_findings)} events for {target_user}.")
        elif target_user:
             print(f"No specific events for {target_user}, falling back to latest system logout event.")

        # Find max timestamp in the selected subset
        for f in findings_to_check:
            dt = parse_timestamp(f)
            if dt:
                if last_logout_dt is None or dt > last_logout_dt:
                    last_logout_dt = dt

    if last_logout_dt:
        print(f"\nAnalyzing errors 10 minutes prior to event at: {last_logout_dt}")
        analyze_pre_logout(last_logout_dt)

    print("\n=== CONCLUSION ===")
    if unique_findings:
        print("Logouts detected.")
    else:
        print("No logouts detected in this window.")

if __name__ == "__main__":
    main()
