#!/usr/bin/env python3
import subprocess
import sys
import os
from datetime import datetime, timedelta

# Usage: sudo python3 whyDown.py [minutes]
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

def get_uptime_seconds():
    try:
        with open("/proc/uptime", "r") as f:
            return float(f.read().split()[0])
    except:
        return -1

def main():
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    since_time = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n=== SYSTEM HEALTH CHECK (Last {minutes} mins) ===")
    print(f"Time Now: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # --- Check 1: Recent Restart/Crash (Uptime) ---
    uptime_seconds = get_uptime_seconds()
    restarted_recently = False
    
    print("\n[1] RESTART/CRASH CHECK")
    if uptime_seconds >= 0:
        if uptime_seconds < (minutes * 60):
            restarted_recently = True
            print(f"YES. System uptime is {uptime_seconds:.1f} seconds (< {minutes} minutes).")
            print("The system has likely restarted or crashed recently.")
        else:
            print(f"NO. System uptime is {uptime_seconds:.1f} seconds (> {minutes} minutes).")
            print("The system has NOT restarted in the checked window.")
    else:
        print("UNKNOWN. Could not read /proc/uptime.")

    # --- Check 2: Log Scanning (Current & Previous Boot if applicable) ---
    
    # Expanded Pattern List
    crash_patterns = {
        "OOM": [
            "Out of memory", "Killed process", "Memory cgroup out of memory", 
            "invoked oom-killer", "oom-kill", "System OOM", "kernel:.*Killed"
        ],
        "PANIC/OOPS": [
            "Kernel panic", "BUG:", "Oops:", "Call Trace:", "RIP:", 
            "unable to handle kernel paging request"
        ],
        "THERMAL/HARDWARE": [
            "thermal", "critical temperature", "Machine Check Exception", "MCE", "Hardware Error"
        ],
        "SEGFAULT": [
            "segfault", "Segmentation fault"
        ],
        "SHUTDOWN/REBOOT": [
            "reboot: Restarting system", "Power key pressed", "systemd-shutdownd", 
            "Deactivated slice", "Reached target Power-Off"
        ]
    }

    all_findings = []

    def scan_log_source(source_name, log_text):
        found_issues = False
        for category, patterns in crash_patterns.items():
            hits = find_patterns(log_text, patterns)
            if hits:
                found_issues = True
                for h in hits[:5]: # Limit per category
                    all_findings.append(f"[{source_name}] [{category}] {h[:120]}")
        return found_issues

    print("\n[2] LOG ANALYSIS")
    
    # 2a. Current Boot Logs
    print(">> Scanning CURRENT boot logs...")
    
    # Journalctl current
    j_current = run(["journalctl", "--since", since_time, "-xe"])
    scan_log_source("Current Journal", j_current)
    
    # Dmesg (often cleared on reboot, but check anyway)
    dmesg_logs = run(["dmesg"]) 
    # Use tail if dmesg is huge
    if len(dmesg_logs) > 500000:
         dmesg_logs = dmesg_logs[-50000:]
    scan_log_source("Dmesg", dmesg_logs)

    # 2b. Previous Boot Logs (Critical if restarted)
    if restarted_recently:
        print("\n>> Scanning PREVIOUS boot logs (journalctl -b -1)...")
        # Check the LAST 500 lines of previous boot to see why it died
        j_prev = run(["journalctl", "-b", "-1", "-n", "1000"])
        
        if "No journal files were found" in j_prev or not j_prev:
             print("   (No persistent journal found or no previous boot record accessible)")
        else:
             found_prev = scan_log_source("PrevBoot Journal", j_prev)
             
             # Also just show the very last few messages as they often hold the clue (non-error finalizer)
             lines = j_prev.strip().split("\n")
             if lines:
                 last_lines = lines[-3:]
                 print("   Last 3 lines of previous boot:")
                 for l in last_lines:
                     print(f"     {l}")

    # 2c. Persistent Files (/var/log/syslog, /var/crash)
    print("\n>> Scanning persistent logs...")
    
    # Syslog
    if os.path.exists("/var/log/syslog"):
        # Scan last 2000 lines approx to handle rotation
        try:
             # tail is efficient
             syslog_tail = run(["tail", "-n", "2000", "/var/log/syslog"])
             scan_log_source("Syslog", syslog_tail)
        except: pass

    # Kern.log
    if os.path.exists("/var/log/kern.log"):
        try:
             kern_tail = run(["tail", "-n", "1000", "/var/log/kern.log"])
             scan_log_source("KernLog", kern_tail)
        except: pass

    # Crash Dumps
    crash_dirs = ["/var/crash"]
    for d in crash_dirs:
        if os.path.exists(d):
            try:
                files = os.listdir(d)
                for f in files:
                    if f.endswith(".crash") or f.endswith(".log"):
                         fpath = os.path.join(d, f)
                         mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                         if mtime > (datetime.now() - timedelta(minutes=minutes)):
                             all_findings.append(f"[CrashDump] Found recent crash report: {fpath} ({mtime})")
            except: pass

    # Report
    print("\n=== FINDINGS SUMMARY ===")
    
    # Deduplicate findings somewhat
    unique_findings = sorted(list(set(all_findings)))
    
    if not unique_findings:
        print("No crash signatures (OOM, Panic, Segfault) found in logs.")
        if restarted_recently:
             print("System restarted, but no clear error log found. Possible causes: Power loss, Hard reset, Clean reboot without error.")
    else:
        print(f"Found {len(unique_findings)} relevant log entries:")
        for f in unique_findings:
            print(f" {f}")

    print("\n=== CONCLUSION ===")
    final_reasons = []
    if restarted_recently: final_reasons.append("System RESTARTED.")
    
    # Classify findings
    cats_found = set()
    for f in unique_findings:
        for cat in crash_patterns.keys():
            if f"[{cat}]" in f: cats_found.add(cat)
        if "[CrashDump]" in f: cats_found.add("CRASH_DUMP")

    if cats_found:
        final_reasons.append(f"Logs indicate: {', '.join(cats_found)}")
    
    if not final_reasons:
        print("System seems stable.")
    else:
        print(" / ".join(final_reasons))

if __name__ == "__main__":
    main()
