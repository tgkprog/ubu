# System Load Management Scripts

This directory contains Python scripts for monitoring and managing system processes to optimize resources for Node.js and Mongosh operations.

## Requirements

```bash
sudo apt-get update
sudo apt-get install python3-psutil
```

## Scripts

### 1. report.py
Analyzes and reports on system processes, identifying which ones can be paused or stopped.

Usage:
```bash
python3 report.py
```

Output:
- Prints summary to console
- Saves detailed report to `system_report.json` (chmod 777)

**Note:** All output files are created with chmod 777 permissions to ensure accessibility when scripts are run with sudo.

### 2. pauseSys.py
Pauses (suspends) non-essential processes to optimize system resources.

Usage:
```bash
sudo python3 pauseSys.py
```

Features:
- Requires sudo privileges
- **Suspends** (pauses) non-essential processes using SIGSTOP
- **Stops** system services using systemctl
- Preserves essential processes (Node.js, Mongosh, terminals, etc.)
- Saves pause state to `paused_state.json` for later resumption
- Logs actions to `pause_actions.log`

Output Files:
- `pause_actions.log` - Detailed log of pause operations (chmod 777)
- `paused_state.json` - State file for restoration (chmod 777)

### 3. restart.py
Restores previously paused processes and services.

Usage:
```bash
sudo python3 restart.py
```

Features:
- Requires sudo privileges
- **Resumes** suspended processes using SIGCONT
- **Restarts** stopped services using systemctl
- Logs actions to `restart_actions.log`
- Cleans up state file after restoration

Output Files:
- `restart_actions.log` - Detailed log of restart operations (chmod 777)

## Essential Processes (Protected)
The following process types are considered essential and won't be paused:
- node, nodejs
- mongosh
- python, python3
- java
- bash, sh
- gnome-terminal
- code (VS Code)
- systemd and core system processes

## How It Works

1. **Processes**: Suspended using SIGSTOP (paused in memory, can be resumed)
2. **Services**: Stopped using systemctl (can be restarted)
3. **Restoration**: Processes resumed with SIGCONT, services restarted with systemctl

## Development Notes
This is the initial basic version. Future iterations may include:
- Process priority management
- More granular service management
- System resource limits
- GUI process whitelist management