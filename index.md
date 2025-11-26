# Ubuntu Scripts Collection

A comprehensive collection of utility scripts and configurations to quickly set up and manage Ubuntu systems.

---

## Quick Install Guides

### Installing .deb Packages

```bash
sudo dpkg -i <path-to-file.deb>
sudo apt install -fy
```

### System Updates

```bash
# Get latest OS bug fixes and software updates
sudo apt update

# Update packages and installed software (does not change Ubuntu version)
sudo apt upgrade -y
```

### Working with tar Files

```bash
# Extract tar.gz archive
tar xvf openjdk-13*_bin.tar.gz

# Set JAVA_HOME for extracted Java
export JAVA_HOME=/usr/lib/jvm/jdk-13.0.1
export PATH=$JAVA_HOME/bin:$PATH

# Set as default Java version
sudo apt install oracle-java13-set-default
```

---

## Documentation by Category

### 🌐 [Networking](ntwrkng/)
- [LAN DNS Setup Guide](ntwrkng/lanDns.md) - Complete guide to setting up dnsmasq for local DNS
- [DNS Management Tools](ntwrkng/README.md) - DNS management scripts and utilities
- Network configuration tools

### ⚙️ [System Process Management](sysProcessesPause/)
- [System Load Management](sysProcessesPause/README.md) - Pause/resume processes to optimize resources
- Process monitoring and control scripts
- Resource optimization tools

### 🎬 [Media Processing](media/)
- FFmpeg video/audio processing commands
- Media conversion utilities

### 🐚 [Shell Scripts](shell/)
- Battery monitoring and warnings
- General bash utilities
- File operation helpers

### 📦 [Miscellaneous](misc/)
- Symlink creation
- File search and execution
- General bash scripts

---

## Main Features

✅ **Easy Installation** - Quick setup scripts for common software  
✅ **Network Tools** - DNS management and configuration  
✅ **System Optimization** - Process control and resource management  
✅ **Media Tools** - FFmpeg commands and utilities  
✅ **Shell Utilities** - Helpful bash scripts and automation  

---

## Requirements

- Ubuntu Linux (tested on recent LTS versions)
- Python 3.x for Python scripts
- Bash for shell scripts
- Sudo access for system-level operations

---

## Repository

📂 [View on GitHub](https://github.com/tgkprog/Ubuntu_scripts)
