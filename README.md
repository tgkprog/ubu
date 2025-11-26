# Ubuntu Scripts Collection

A collection of utility scripts and configurations to quickly set up and manage Ubuntu systems.

## Overview

This repository contains various scripts and utilities for:
- System installation and setup
- Network configuration and DNS management
- System process management and resource optimization
- Media processing with ffmpeg
- Shell utilities and automation

## Directory Structure

- **`ntwrkng/`** - Network configuration scripts, including DNS and dnsmasq utilities (see [lanDns.md](ntwrkng/lanDns.md) for LAN DNS setup guide)
- **`sysProcessesPause/`** - System process monitoring and resource management tools
- **`shell/`** - General shell scripts and utilities
- **`media/`** - Media processing scripts and configurations
- **`js/`** - JavaScript/Node.js installation and setup scripts
- **`misc/`** - Miscellaneous utilities and helper scripts
- **`otherSoftware/`** - Installation scripts for various software packages
- **`secure/`** - Security-related scripts and configurations

## Quick Start

1. Clone this repository
2. Review the specific directory README files for detailed usage
3. Run scripts with appropriate permissions (some require sudo)

## Main Scripts

- `aptInstallCmdsAll.txt` - Comprehensive list of apt installation commands
- `dnsMskDomainEdit.py` - DNS domain configuration editor for dnsmasq
- Various `.txt` files containing installation commands and documentation

## Requirements

- Ubuntu Linux (tested on recent LTS versions)
- Python 3.x for Python scripts
- Bash for shell scripts
- Sudo access for system-level operations

## Future Improvements

- Further automation to reduce manual steps
- Variable-based configuration for software versions (Java, Node.js, Eclipse, etc.)
- Enhanced error handling and logging

## License

See LICENSE file for details.
