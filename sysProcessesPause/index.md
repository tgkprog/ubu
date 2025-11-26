# System Process Management

Tools and scripts for monitoring, pausing, and managing system processes to optimize resources for development work (Node.js, MongoDB, etc.).

## Overview

This suite of Python scripts helps manage system resources by pausing non-essential processes and services, freeing up CPU and memory for critical development tasks.

## Requirements

```bash
sudo apt-get update
sudo apt-get install python3-psutil
```

## Scripts

### report.py

**System process analyzer** - Identifies which processes can be safely paused or stopped.

```bash
python3 report.py
```

**Output:**
- Console summary of pauseable processes
- Detailed report saved to `system_report.json`

### pauseSys.py

**Process suspension tool** - Pauses non-essential processes to free up resources.

```bash
sudo python3 pauseSys.py
```

**Features:**
- Suspends processes using SIGSTOP (pauses, doesn't kill)
- Stops system services via systemctl
- Protects essential processes (Node.js, Mongosh, terminals, etc.)
- Saves state to `paused_state.json` for restoration
- Logs all actions to `pause_actions.log`

**Requires:** sudo privileges

### restart.py

**Process restoration tool** - Resumes previously paused processes and services.

```bash
sudo python3 restart.py
```

**Features:**
- Reads `paused_state.json` to restore exact previous state
- Resumes suspended processes using SIGCONT
- Restarts stopped services via systemctl
- Logs restoration actions to `restart_actions.log`

## Shell Wrappers

Convenience scripts for easier execution:

- **rpause.sh** - Wrapper for pauseSys.py
- **rrestart.sh** - Wrapper for restart.py  
- **rreport.sh** - Wrapper for report.py
- **setup_env.sh** - Environment setup script
- **step1.sh** - Initial setup step

### sysMon.py

**System monitoring utility** - Real-time process and resource monitoring.

```bash
python3 sysMon.py
```

## Workflow

1. **Analyze:** Run `report.py` to see what processes can be paused
2. **Pause:** Run `sudo pauseSys.py` to free up resources for development
3. **Work:** Do your Node.js/MongoDB development with optimized resources
4. **Restore:** Run `sudo restart.py` to resume all paused processes

## Files Generated

- `system_report.json` - Analysis of system processes (chmod 777)
- `paused_state.json` - State file for restoration (chmod 777)
- `pause_actions.log` - Log of pause operations (chmod 777)
- `restart_actions.log` - Log of restore operations (chmod 777)

See [README.md](README.md) for detailed documentation.

---

[← Back to Home](../)
