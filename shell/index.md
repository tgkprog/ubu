# Shell Scripts

Bash scripts and shell utilities for Ubuntu system management.

## Scripts

### batteryWatchCheckWarn.sh

**Battery monitoring and warning system** - Monitors laptop battery status and provides audio/visual alerts.

**Features:**
- Monitors battery charge level continuously
- Audio alerts when battery is discharging
- Desktop notifications via notify-send and zenity
- Auto-starts on system boot via .desktop file

**Setup for autostart:**
```bash
# Create autostart file at: ~/.config/autostart/batteryMonitor.desktop
[Desktop Entry]
Type=Application
Exec=/path/to/batteryWatchCheckWarn.sh
Hidden=false
NoDisplay=false
Name=Battery Monitor Script
```

**Requirements:**
- ffplay (for audio alerts)
- notify-send
- zenity
- Battery device at /sys/class/power_supply/BAT1

**Usage:**
```bash
./batteryWatchCheckWarn.sh
```

### fileCmds.sh / fileCmds.txt

**File management command references** - Common file operations and utilities for Ubuntu.

**Contents:**
- File manipulation commands
- Search and find operations
- Permission management
- Directory operations
