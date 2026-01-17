#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime, timedelta

# Usage: sudo python3 check_oom.py [minutes]
# Default: 30 minutes

def run(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return out.strip()
    except Exception as e:
        return ""

def find_patterns(text, patterns):
    hits = []
    for line in text.split("\n"):
        for p in patterns:
            if p.lower() in line.lower():
                hits.append(line)
    return hits

def main():
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    since_time = (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")

    # Common OOM patterns
    oom_keys = [
        "Out of memory",
        "Killed process",
        "Memory cgroup out of memory",
        "invoked oom-killer",
        "oom-kill",
        "System OOM",
        "kernel:.*Killed"
    ]

    # 1. Journald
    journal_cmd = ["journalctl", "--since", since_time, "-xe"]
    journal_logs = run(journal_cmd)
    journal_hits = find_patterns(journal_logs, oom_keys)

    # 2. Kernel log
    dmesg_logs = run(["dmesg", "--ctime"])
    dmesg_hits = []
    if dmesg_logs:
        # Filter only recent by minutes
        for line in dmesg_logs.split("\n"):
            dmesg_hits.extend(find_patterns(line, oom_keys)) if any(k in line for k in oom_keys) else None

    # 3. /var/log/syslog (Ubuntu)
    try:
        syslog_logs = run(["grep", "-i", "-E", "|".join(oom_keys), "/var/log/syslog"])
    except:
        syslog_logs = ""
    syslog_hits = syslog_logs.split("\n") if syslog_logs else []

    # 4. Crash logs (Apport or kernel)
    crash_hits = []
    crash_dirs = [
        "/var/crash",
    ]
    for d in crash_dirs:
        ls = run(["ls", "-1", d])
        for f in ls.split("\n"):
            if f.endswith(".crash") or f.endswith(".log"):
                crash_hits.append(f"Crash file: {d}/{f}")

    # Final decision
    all_hits = journal_hits + dmesg_hits + syslog_hits
    oom_likely = any(all_hits)

    print("\n=== OOM CHECK REPORT ===")
    print(f"Looked back: {minutes} minutes")
    print("\n-- Journald hits --")
    print("\n".join(journal_hits) if journal_hits else "None")

    print("\n-- dmesg hits --")
    print("\n".join(dmesg_hits) if dmesg_hits else "None")

    print("\n-- syslog hits --")
    print("\n".join(syslog_hits) if syslog_hits else "None")

    print("\n-- Crash files --")
    print("\n".join(crash_hits) if crash_hits else "None")

    print("\n=== RESULT ===")
    if oom_likely:
        print("YES: Likely an OOM event.")
    else:
        print("NO: No strong evidence of OOM in logs.")

if __name__ == "__main__":
    main()

