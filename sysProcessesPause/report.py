#!/usr/bin/env python3
"""
System Resource Monitor
Reports system processes and identifies which ones can be stopped/paused
to optimize system resources for Node.js and Mongosh operations.
"""

import psutil
import json
from datetime import datetime
import os


def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
        try:
            pinfo = proc.info
            # Get more details about the process
            proc_details = {
                'pid': pinfo['pid'],
                'name': pinfo['name'],
                'username': pinfo['username'],
                'cpu_percent': pinfo['cpu_percent'],
                'memory_percent': pinfo['memory_percent'],
                'status': pinfo['status'],
                'command': ' '.join(proc.cmdline()) if proc.cmdline() else ''
            }
            processes.append(proc_details)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


def categorize_process(proc_name, command):
    """Categorize a process based on its name and command"""
    essential_processes = {
        'node', 'nodejs', 'mongosh', 'python', 'python3', 'java',
        'bash', 'sh', 'gnome-terminal', 'code', 'systemd', 'sshd',
        'gnome-shell', 'Xorg', 'dbus', 'networkmanager', 'systemd-journal'
    }

    pausable_processes = {
        'chrome', 'firefox', 'chromium', 'brave', 'opera',
        'thunderbird', 'slack', 'discord', 'spotify', 'libreoffice',
        'notepad', 'gedit', 'nautilus', 'nemo', 'dolphin'
    }

    # Services that can be safely stopped and restarted
    pausable_services = {
        'cups', 'bluetooth', 'avahi', 'packagekit', 'snapd',
        'tracker-store', 'tracker-miner', 'evolution-calendar',
        'gsd-printer', 'gsd-sharing', 'gsd-wacom'
    }

    proc_lower = proc_name.lower()
    cmd_lower = command.lower()

    if any(name in proc_lower for name in essential_processes):
        return "essential"
    elif any(name in proc_lower for name in pausable_processes):
        return "pausable"
    elif any(name in proc_lower for name in pausable_services):
        return "service"
    elif 'snap' in proc_lower and not any(p in proc_lower for p in essential_processes):
        return "pausable"  # Non-essential snap applications
    elif proc_lower.startswith('gsd-') and 'power' not in proc_lower:
        return "service"  # GNOME system services except power management
    else:
        return "killable"


def analyze_processes(processes):
    analysis = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'total_processes': len(processes)
        },
        'essential_processes': [],
        'pausable_processes': [],
        'pausable_services': [],
        'killable_processes': [],
        'high_resource_processes': [],
        'process_stats': {
            'essential_count': 0,
            'pausable_count': 0,
            'service_count': 0,
            'killable_count': 0
        }
    }

    for proc in processes:
        # Check if process is using significant resources
        if proc['cpu_percent'] > 5 or proc['memory_percent'] > 5:
            analysis['high_resource_processes'].append(proc)

        # Categorize the process
        category = categorize_process(proc['name'], proc['command'])

        # Add to appropriate category list and update counts
        if category == "essential":
            analysis['essential_processes'].append(proc)
            analysis['process_stats']['essential_count'] += 1
        elif category == "pausable":
            analysis['pausable_processes'].append(proc)
            analysis['process_stats']['pausable_count'] += 1
        elif category == "service":
            analysis['pausable_services'].append(proc)
            analysis['process_stats']['service_count'] += 1
        else:  # killable
            analysis['killable_processes'].append(proc)
            analysis['process_stats']['killable_count'] += 1

    return analysis


def save_report(analysis):
    report_path = os.path.join(os.path.dirname(__file__), 'system_report.json')
    with open(report_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    os.chmod(report_path, 0o777)
    print(f"Report saved to {report_path}")


def main():
    print("Gathering system process information...")
    processes = get_process_info()
    print("Analyzing processes...")
    analysis = analyze_processes(processes)

    # Print summary
    print("\n=== System Resource Report ===")
    print(f"Total Processes: {analysis['system_info']['total_processes']}")
    print(f"CPU Usage: {analysis['system_info']['cpu_percent']}%")
    print(f"Memory Usage: {analysis['system_info']['memory_percent']}%")

    # Process categorization summary
    print("\n=== Process Categories ===")
    print(
        f"Essential Processes: {analysis['process_stats']['essential_count']}")
    print(
        f"Pausable Applications: {analysis['process_stats']['pausable_count']}")
    print(f"System Services: {analysis['process_stats']['service_count']}")
    print(f"Other (Killable): {analysis['process_stats']['killable_count']}")

    # High resource usage processes
    if analysis['high_resource_processes']:
        print("\n=== High Resource Usage Processes ===")
        for proc in analysis['high_resource_processes']:
            print(f"{proc['name']} (PID: {proc['pid']}):")
            print(
                f"  CPU: {proc['cpu_percent']}%, Memory: {proc['memory_percent']}%")

    # Save detailed report
    save_report(analysis)
    print("\nDetailed report has been saved to system_report.json")


if __name__ == "__main__":
    main()
