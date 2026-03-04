# System Scripts Backup (sys/b)

**Last Updated:** 2026-03-04

This directory contains a backup of system utility scripts from `/b`, limited to files smaller than 1MB and up to 2 directory levels deep.

## Purpose

This backup is created by the `../saveGit` script to preserve essential system utilities in the git repository while excluding large files.

## Scripts Overview

### CPU Management
- `cpu100set` - Set CPU to 100% performance mode
- `cpu80set` - Set CPU to 80% mode
- `cpuget` - Get current CPU settings
- `cpulow` - Set CPU to low power mode
- `cpumax` - Set CPU to maximum performance
- `cpunorm` - Set CPU to normal mode
- `cpuset` - General CPU configuration script

### System Monitoring
- `temp` - Check system temperature
- `tempb` - Temperature monitoring (brief)
- `wtemp` - Watch temperature continuously
- `memtrack` - Memory tracking utility
- `topm` - Top memory consumers
- `sysinfo2` - System information display
- `whyd`, `whyd2`, `whyd3` - System downtime/crash investigation tools

### Process Management
- `killp` - Kill processes utility
- `killantig` - Kill antivirus processes
- `clranti` - Clear antivirus processes

### Notifications & UI
- `winMsg`, `winMsg.py`, `winMsg2.py` - Window message display utilities
- `winMsg.ini` - Configuration for window messages
- `winMsg.md` - Documentation for window messaging
- `showWin`, `showWin.py` - Show window utilities
- `donePersistentNotify.py` - Persistent notification system
- `happyBeeps`, `happyBeeps.ps1` - Audio notification scripts
- `sweetSound` - Sound notification utility

### Network & Connectivity
- `dns` - DNS management
- `vps1` - VPS connection script

### Editors & Terminals
- `gedit1` - Launch gedit
- `ter` - Terminal launcher
- `gt1` - Git terminal
- `co1` - Console utility
- `t7co` - Terminal 7 console

### System Operations
- `shut` - Shutdown utility
- `updt` - Update system
- `checkt` - System check
- `aptdot` - APT operations
- `path` - Path management
- `toRepo` - Navigate to repository

### Resources
- `rme.odt` - Documentation file
- `res/` - Resources directory
- `done/` - Completed tasks
- `e/` - Additional scripts directory
- `b/` - Nested backup directory
- `b2/` - Secondary backup directory

## Usage

These scripts are backed up copies. To use them:
1. Ensure they have execute permissions: `chmod +x scriptname`
2. Run directly: `./scriptname`
3. Or copy to a location in your PATH

## Updating This Backup

Run the parent saveGit script:
```bash
cd /data/code/gt/tgk/ubu/sys
./saveGit
```

This will copy all files < 1MB from `/b` to this directory, showing:
- Files being copied with sizes
- Files skipped due to size
- Folders skipped at level 3+

## Notes

- Only files smaller than 1MB are included
- Maximum directory depth: 2 levels
- Level 3+ directories are excluded to keep backup manageable
- Original location: `/b`
