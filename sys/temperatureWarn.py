#!/usr/bin/env python3
# sel2in.com tgkprog@gmail.com
import subprocess
import time
import sys
import argparse
import signal
import threading
import os
from datetime import datetime, timedelta
try:
    import tkinter as tk
except ImportError:
    tk = None  # tkinter not available
# command to install tkinter: sudo apt install python3-tk
CRITICAL = 78
THRESHOLD = 73
INTERVAL = 30 # seconds
LOG_FILE = "/tmp/temp.log"  # Default, can be overridden by --log-file argument

def get_detailed_temps():
    """Get detailed temperature readings from sensors output.
    Returns: (first_temp1, edge_temp, second_temp1) or (None, None, None)
    """
    try:
        out = subprocess.check_output(["sensors"], text=True)
        temp1_values = []
        edge_temp = None
        
        for line in out.splitlines():
            # Extract temp1 values
            if "temp1:" in line:
                for token in line.split():
                    if token.startswith("+") and token.endswith("°C"):
                        temp1_values.append(token[1:-2])
                        break
            # Extract edge temperature
            if "edge:" in line:
                for token in line.split():
                    if token.startswith("+") and token.endswith("°C"):
                        edge_temp = token[1:-2]
                        break
        
        first_temp1 = temp1_values[0] if len(temp1_values) > 0 else None
        second_temp1 = temp1_values[1] if len(temp1_values) > 1 else None
        
        return (first_temp1, edge_temp, second_temp1)
    except Exception:
        return (None, None, None)

def get_temp():
    """Get a single temperature value for threshold checking."""
    try:
        out = subprocess.check_output(["sensors"], text=True)
        # Look for k10temp adapter section
        lines = out.splitlines()
        in_k10temp = False
        for line in lines:
            # Detect k10temp adapter section header
            if "k10temp" in line.lower():
                in_k10temp = True
                continue
            # If we're in k10temp section and find temp1, extract it
            if in_k10temp and "temp1:" in line:
                for token in line.split():
                    if token.startswith("+") and token.endswith("°C"):
                        return float(token[1:-2])
            # Exit k10temp section when we hit empty line (new section)
            if in_k10temp and line.strip() == "":
                in_k10temp = False
        # Fallback: look for any line with Tctl or CPU
        for line in lines:
            if "Tctl" in line or "CPU" in line:
                for token in line.split():
                    if token.startswith("+") and token.endswith("°C"):
                        return float(token[1:-2])
    except Exception:
        return None

def clean_old_log_entries():
    """Remove log entries older than 10 minutes."""
    global LOG_FILE
    try:
        cutoff_time = datetime.now() - timedelta(minutes=10)
        
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()
        
        filtered_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Extract time from log format: "HH MM temp1: ..."
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    # Parse HH MM format (space-separated)
                    hour = int(parts[0])
                    minute = int(parts[1])
                    log_datetime = datetime.now().replace(
                        hour=hour, 
                        minute=minute, 
                        second=0, 
                        microsecond=0
                    )
                    
                    # Keep entries within 10 minutes
                    if log_datetime >= cutoff_time:
                        # Keep this entry and all its lines until the next "--"
                        filtered_lines.append(line)
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith("--"):
                            filtered_lines.append(lines[i])
                            i += 1
                        if i < len(lines):  # Add the "--" separator
                            filtered_lines.append(lines[i])
                            i += 1
                        continue
                    else:
                        # Skip this entry - move to next entry (after "--")
                        i += 1
                        while i < len(lines) and not lines[i].strip().startswith("--"):
                            i += 1
                        i += 1  # Skip the "--" line too
                        continue
                except (ValueError, IndexError):
                    # Not a timestamp line, keep it if we're in a valid entry
                    filtered_lines.append(line)
            else:
                # Empty line or separator, keep it
                filtered_lines.append(line)
            i += 1
        
        # Write back filtered lines
        with open(LOG_FILE, "w") as f:
            f.writelines(filtered_lines)
    except FileNotFoundError:
        # Log file doesn't exist yet, nothing to clean
        pass
    except Exception as e:
        print(f"Error cleaning log: {e}", file=sys.stderr)

def log_temperature(temp1_first, edge_temp, temp1_second):
    """Log temperature readings to log file in custom parsed format.
    Format matches temp_sample.log with full sensors output parsing.
    """
    global LOG_FILE
    try:
        now = datetime.now()
        time_str = now.strftime("%H %M")  # HH MM format
        
        # Clean old entries before adding new one
        clean_old_log_entries()
        
        # Get full sensors output for detailed parsing
        sensors_output = subprocess.check_output(["sensors"], text=True)
        
        # Parse sensors output for specific values
        lines = sensors_output.splitlines()
        
        # Extract key information
        temp1_iwlwifi = None
        temp1_k10temp = None
        temp1_k10temp_high = None
        temp1_k10temp_crit = None
        temp1_k10temp_hyst = None
        battery_voltage = None
        vddgfx = None
        vddnb = None
        edge = None
        cpu_fan = None
        gpu_fan = None
        power1 = None
        power1_avg = None
        power1_crit = None
        temp1_acpitz = None
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # iwlwifi temp1
            if "iwlwifi" in line.lower():
                if i + 2 < len(lines) and "temp1:" in lines[i + 2]:
                    parts = lines[i + 2].split()
                    for j, p in enumerate(parts):
                        if p.startswith("+") and "°C" in p:
                            temp1_iwlwifi = p
                            break
            
            # k10temp-pci temp1 with high/crit/hyst
            if "k10temp" in line.lower():
                if i + 2 < len(lines) and "temp1:" in lines[i + 2]:
                    parts = lines[i + 2].split()
                    for j, p in enumerate(parts):
                        if p.startswith("+") and "°C" in p:
                            temp1_k10temp = p
                            # Look for high/crit/hyst on same or next line
                            combined = lines[i + 2]
                            if i + 3 < len(lines):
                                combined += " " + lines[i + 3]
                            if "high" in combined:
                                high_match = combined.split("high")[1].split(")")[0]
                                for token in high_match.split():
                                    if "°C" in token:
                                        temp1_k10temp_high = token
                                        break
                            if "crit" in combined:
                                crit_match = combined.split("crit")[1].split(",")[0]
                                for token in crit_match.split():
                                    if "°C" in token:
                                        temp1_k10temp_crit = token
                                        break
                            if "hyst" in combined:
                                hyst_match = combined.split("hyst")[1].split(")")[0]
                                for token in hyst_match.split():
                                    if "°C" in token:
                                        temp1_k10temp_hyst = token
                                        break
                            break
            
            # Battery voltage
            if "BAT0" in line or "in0:" in line:
                if "in0:" in line:
                    parts = line.split()
                    for j, p in enumerate(parts):
                        if "V" in p:
                            battery_voltage = " ".join(parts[1:3])
                            break
            
            # GPU voltages
            if "vddgfx:" in line:
                parts = line.split()
                vddgfx = " ".join(parts[1:3])
            if "vddnb:" in line:
                parts = line.split()
                vddnb = " ".join(parts[1:3])
            
            # Edge temperature
            if "edge:" in line:
                parts = line.split()
                for p in parts:
                    if p.startswith("+") and "°C" in p:
                        edge = p
                        break
            
            # Fan speeds
            if "cpu_fan:" in line:
                parts = line.split()
                cpu_fan = " ".join(parts[1:3])
            if "gpu_fan:" in line:
                parts = line.split()
                gpu_fan = " ".join(parts[1:3])
            
            # Power
            if "power1:" in line and "mW" in line:
                parts = line.split()
                power1 = " ".join(parts[1:3])
                if "avg" in line:
                    avg_start = line.index("avg")
                    avg_section = line[avg_start:]
                    avg_parts = avg_section.split()
                    if len(avg_parts) >= 3:
                        power1_avg = " ".join(avg_parts[2:4])
                if i + 1 < len(lines) and "crit" in lines[i + 1]:
                    crit_line = lines[i + 1]
                    crit_parts = crit_line.split()
                    for j, p in enumerate(crit_parts):
                        if "W" in p and j > 0:
                            power1_crit = " ".join(crit_parts[j-1:j+1])
                            break
            
            # acpitz temp1
            if "acpitz" in line.lower():
                if i + 2 < len(lines) and "temp1:" in lines[i + 2]:
                    parts = lines[i + 2].split()
                    for p in parts:
                        if p.startswith("+") and "°C" in p:
                            temp1_acpitz = p
                            break
            
            i += 1
        
        # Build log entry in the sample format
        log_entry = f"{time_str} temp1: {temp1_iwlwifi or 'N/A'}   PCI adapter {temp1_k10temp or 'N/A'}  (high = {temp1_k10temp_high or 'N/A'})   (crit = {temp1_k10temp_crit or 'N/A'}, hyst = {temp1_k10temp_hyst or 'N/A'})\n"
        log_entry += "\n"
        log_entry += f"BAT0-acpi-0   {battery_voltage or 'N/A'}\n"
        log_entry += "\n"
        log_entry += f"vddgfx:      {vddgfx or 'N/A'}\n"
        log_entry += f"vddnb:       {vddnb or 'N/A'}\n"
        log_entry += f"edge:        {edge or 'N/A'}\n"
        log_entry += "asus-isa-0000\n"
        log_entry += "Adapter: ISA adapter\n"
        log_entry += f"cpu_fan:      {cpu_fan or 'N/A'}\n"
        log_entry += f"gpu_fan:      {gpu_fan or 'N/A'}\n"
        log_entry += "\n"
        log_entry += f"power1:       {power1 or 'N/A'} (avg =  {power1_avg or 'N/A'}, interval =   0.01 s)\n"
        log_entry += f"                       (crit =  {power1_crit or 'N/A'})\n"
        log_entry += f"temp1:        {temp1_acpitz or 'N/A'}\n"
        log_entry += "--\n"
        
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error logging temperature: {e}", file=sys.stderr)

def show_temp_warning_window(temp, is_critical):
    """Show a lightweight warning window using tkinter."""
    if tk is None:
        print("Warning: tkinter not available, skipping GUI window", file=sys.stderr)
        return
    
    def create_window():
        try:
            root = tk.Tk()
            root.title("temp high")
            root.configure(bg='red' if is_critical else 'orange')
            root.geometry("400x200")
            root.attributes('-topmost', True)
            
            # Display temperature
            label = tk.Label(
                root, 
                text=f"CPU Temperature: {temp}°C\n{'CRITICAL!' if is_critical else 'High'}",
                font=('Arial', 16, 'bold'),
                bg='red' if is_critical else 'orange',
                fg='white'
            )
            label.pack(expand=True)
            
            # Auto-close after 5 seconds
            root.after(5000, root.destroy)
            root.mainloop()
        except Exception as e:
            print(f"Error showing window: {e}", file=sys.stderr)
    
    # Run window in separate thread so it doesn't block
    thread = threading.Thread(target=create_window, daemon=True)
    thread.start()

def _run_command_silent(cmd):
    """Run command suppressing stdio; return True on success."""
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def lock_and_turn_off_display():
    """Attempt to lock the session (Win+L equivalent) and power off monitors."""
    session_id = os.environ.get("XDG_SESSION_ID")
    uid = str(os.getuid())
    lock_commands = [["xdotool", "key", "Super_L+l"]]
    if session_id:
        lock_commands.append(["loginctl", "lock-session", session_id])
    lock_commands.extend([
        ["loginctl", "lock-session"],
        ["loginctl", "lock-user", uid],
        ["xdg-screensaver", "lock"],
        ["gnome-screensaver-command", "-l"],
        [
            "dbus-send",
            "--type=method_call",
            "--dest=org.freedesktop.ScreenSaver",
            "/org/freedesktop/ScreenSaver",
            "org.freedesktop.ScreenSaver.Lock",
        ],
    ])

    locked = False
    for cmd in lock_commands:
        if _run_command_silent(cmd):
            locked = True
            break

    display = os.environ.get("DISPLAY")
    if display:
        display_commands = [
            ["xset", "-display", display, "dpms", "force", "off"],
            ["xset", "-display", display, "dpms", "force", "standby"],
        ]
        for cmd in display_commands:
            if _run_command_silent(cmd):
                print("Display powered down to aid cooling", file=sys.stderr)
                break

    if locked:
        print("Session locked due to critical temperature", file=sys.stderr)

def kill_heavy_processes():
    """Kill processes containing node, java, chrome, and antigravity."""
    try:
        # Get all processes
        result = subprocess.run(['ps', '-aux'], capture_output=True, text=True)
        processes = result.stdout.splitlines()
        
        # Targets to kill
        targets = ['node', 'java', 'chrome', 'antigravity', 'python']
        killed = []
        
        for line in processes[1:]:  # Skip header
            parts = line.split()
            if len(parts) < 11:
                continue
            
            pid = parts[1]
            command = ' '.join(parts[10:])
            
            # Check if process matches any target
            for target in targets:
                if target in command.lower():
                    try:
                        # Send SIGTERM (graceful termination)
                        subprocess.run(['kill', '-TERM', pid], check=False)
                        killed.append(f"{target} (PID {pid})")
                        print(f"Killed {target} process (PID {pid}): {command[:50]}...", file=sys.stderr)
                    except Exception as e:
                        print(f"Error killing PID {pid}: {e}", file=sys.stderr)
                    break
        
        if killed:
            print(f"CRITICAL TEMP: Killed processes: {', '.join(killed)}", file=sys.stderr)
        else:
            print("CRITICAL TEMP: No matching processes to kill", file=sys.stderr)
            
    except Exception as e:
        print(f"Error killing processes: {e}", file=sys.stderr)


def kill_antigravity_processes():
    """Forcefully terminate all running antigravity processes using sudo."""
    try:
        result = subprocess.run(['ps', '-eo', 'pid=', 'command='], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        antigravity_procs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                continue
            pid, command = parts
            if 'antigravity' in command.lower():
                antigravity_procs.append((pid, command))
        if not antigravity_procs:
            print("No antigravity processes found to terminate", file=sys.stderr)
            return
        for pid, command in antigravity_procs:
            try:
                subprocess.run(['sudo', 'kill', pid], check=False)
                print(f"Sent sudo kill to antigravity PID {pid}: {command[:50]}...", file=sys.stderr)
            except Exception as e:
                print(f"Failed to send sudo kill to PID {pid}: {e}", file=sys.stderr)
        time.sleep(1)
        for pid, _ in antigravity_procs:
            try:
                subprocess.run(['sudo', 'kill', '-9', pid], check=False)
                print(f"Sent sudo kill -9 to antigravity PID {pid}", file=sys.stderr)
            except Exception as e:
                print(f"Failed to send sudo kill -9 to PID {pid}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error locating antigravity processes: {e}", file=sys.stderr)

def notify(temp):
    """Send desktop notification using notify-send.
    notify-send is a Linux command-line utility that displays popup notifications
    on the desktop. The -u flag sets urgency level (critical = highest priority).
    
    If temp ≥ CRITICAL, also kills heavy processes to reduce CPU load.
    """
    is_critical = temp >= CRITICAL
    
    # Get detailed temperatures for logging
    temp1_first, edge_temp, temp1_second = get_detailed_temps()
    
    # Log to file
    log_temperature(temp1_first, edge_temp, temp1_second)
    
    # Show GUI warning window
    show_temp_warning_window(temp, is_critical)
    
    # Send desktop notification
    subprocess.run([
        "notify-send",
        "-u", "critical",
        "CPU OVERHEATING" if is_critical else "CPU Temperature High",
        f"Temperature {temp}°C ≥ {THRESHOLD}°C\n{'KILLING PROCESSES!' if is_critical else 'Save work NOW'}"
    ])
    
    # If critical, kill heavy processes and lock system
    if is_critical:
        print(f"CRITICAL TEMPERATURE {temp}°C ≥ {CRITICAL}°C - Killing heavy processes", file=sys.stderr)
        kill_heavy_processes()
        if temp > CRITICAL:
            kill_antigravity_processes()
        lock_and_turn_off_display()

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Monitor CPU temperature and send alerts")
    parser.add_argument(
        "--log-file",
        default="/tmp/temp.log",
        help="Path to log file (default: /tmp/temp.log)"
    )
    parser.add_argument(
        "--warn",
        type=float,
        default=THRESHOLD,
        help=f"Temperature threshold for warnings (default: {THRESHOLD}°C)"
    )
    parser.add_argument(
        "--critical",
        type=float,
        default=CRITICAL,
        help=f"Temperature threshold for killing/locking (default: {CRITICAL}°C)"
    )
    args = parser.parse_args()
    
    if args.critical <= args.warn:
        parser.error("--critical must be greater than --warn")
    
    # Override LOG_FILE with command-line argument
    LOG_FILE = args.log_file
    THRESHOLD = args.warn
    CRITICAL = args.critical
    
    print(
        f"Starting temperature monitor (warn: {THRESHOLD}°C, critical: {CRITICAL}°C, interval: {INTERVAL}s)",
        file=sys.stderr,
    )
    print(f"Logging to: {LOG_FILE}", file=sys.stderr)
    
    while True:
        temp = get_temp()
        if temp:
            # Get detailed temps for logging
            temp1_first, edge_temp, temp1_second = get_detailed_temps()
            
            # Always log temperature (every interval)
            log_temperature(temp1_first, edge_temp, temp1_second)
            
            # Only show notification/window if temp >= THRESHOLD
            if temp >= THRESHOLD:
                print(f"WARNING: CPU {temp}°C", file=sys.stderr)
                
                # Show GUI warning and desktop notification
                is_critical = temp >= CRITICAL
                show_temp_warning_window(temp, is_critical)
                
                subprocess.run([
                    "notify-send",
                    "-u", "critical",
                    "CPU OVERHEATING" if is_critical else "CPU Temperature High",
                    f"Temperature {temp}°C ≥ {THRESHOLD}°C\n{'KILLING PROCESSES!' if is_critical else 'Save work NOW'}"
                ])
                
                # Only kill processes if temp >= CRITICAL
                if is_critical:
                    print(f"CRITICAL TEMPERATURE {temp}°C ≥ {CRITICAL}°C - Killing heavy processes", file=sys.stderr)
                    kill_heavy_processes()
                    if temp > CRITICAL:
                        kill_antigravity_processes()
                    lock_and_turn_off_display()
        
        time.sleep(INTERVAL)


# Service commands (after editing this file, you MUST restart the service):
# sudo systemctl daemon-reload
# sudo systemctl restart temperature-warn
# 
# To check service status:
# sudo systemctl status temperature-warn
#
# To test without conflicting with running service:
# python3 temperatureWarn.py --log-file /tmp/temp_test.log