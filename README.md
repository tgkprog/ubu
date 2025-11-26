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
- [dnsMskDomainEdit.py](ntwrkng/dnsMskDomainEdit.py) - Add, comment, delete, or list DNS domains

### ⚙️ [System Process Management](sysProcessesPause/)
- [System Load Management](sysProcessesPause/README.md) - Pause/resume processes to optimize resources
- Process monitoring and control scripts (pauseSys.py, restart.py, report.py)
- Shell wrappers for easier execution
- Resource optimization for Node.js/MongoDB development

### 🎬 [Media Processing](media/)
- FFmpeg video/audio trim and concatenation commands
- Video compression with H.265
- Media conversion utilities

### 🐚 [Shell Scripts](shell/)
- Battery monitoring with audio/visual warnings
- File management utilities
- Autostart configuration examples

### 💻 [JavaScript / Node.js](js/)
- NVM (Node Version Manager) installation script
- Node.js setup and command references
- NPM usage guides

### 🔒 [Security](secure/)
- File permission commands (chmod, chown)
- Security best practices

### 📦 [Miscellaneous](misc/)
- Symbolic link creation
- Find and execute commands
- General bash utilities

### 📥 [Other Software](otherSoftware/)
- Splunk installation and setup
- Third-party software guides

---

## Main Features

✅ **Easy Installation** - Quick setup scripts for common software  
✅ **Network Tools** - DNS management and dnsmasq configuration  
✅ **System Optimization** - Pause/resume processes to free resources  
✅ **Media Tools** - FFmpeg commands for video/audio processing  
✅ **Shell Utilities** - Battery monitoring, file operations, automation  
✅ **Development Setup** - Node.js, NVM, and development tools

---

## Directory Structure

- **`ntwrkng/`** - Network configuration scripts, DNS and dnsmasq utilities
- **`sysProcessesPause/`** - System process monitoring and resource management
- **`shell/`** - General shell scripts and utilities
- **`media/`** - Media processing scripts and FFmpeg commands
- **`js/`** - JavaScript/Node.js installation and setup scripts
- **`misc/`** - Miscellaneous utilities and helper scripts
- **`otherSoftware/`** - Installation scripts for various software packages
- **`secure/`** - Security-related scripts and configurations

## Requirements

- Ubuntu Linux (tested on recent LTS versions)
- Python 3.x for Python scripts
- Bash for shell scripts
- Sudo access for system-level operations

## Quick Start

1. Clone this repository
2. Review the specific directory index.md files for detailed usage
3. Run scripts with appropriate permissions (some require sudo)

## Main Files

- `aptInstallCmdsAll.txt` - Comprehensive list of apt installation commands
- `apt_install.txt` - APT package installation reference
- `video_audio_ffmpeg.txt` - FFmpeg command examples
- Various `.txt` files containing installation commands and documentation

---

## Repository

📂 [View on GitHub](https://github.com/tgkprog/ubu)  
📖 [View Documentation Site](https://tgkprog.github.io/ubu/)
