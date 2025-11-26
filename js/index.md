# JavaScript / Node.js

Node.js and JavaScript development environment setup for Ubuntu.

## Scripts

### install_nvm.sh

**NVM (Node Version Manager) installation script** - Automated setup for managing multiple Node.js versions.

**Usage:**
```bash
./install_nvm.sh
```

**What it does:**
- Downloads and installs NVM
- Configures shell environment
- Allows easy switching between Node.js versions

## Documentation

### nodeNvm.txt / nodeNvm2.txt

**Node.js and NVM command references**

**Common NVM commands:**
```bash
# Install latest Node.js LTS version
nvm install --lts

# Install specific version
nvm install 18.17.0

# List installed versions
nvm list

# Switch to specific version
nvm use 18.17.0

# Set default version
nvm alias default 18.17.0

# Show current version
node --version
```

**NPM basics:**
```bash
# Initialize new project
npm init

# Install package locally
npm install <package-name>

# Install package globally
npm install -g <package-name>

# Install from package.json
npm install

# Update packages
npm update
```

### How To Install Node.js on Ubuntu 18.04

**DigitalOcean guide** - Comprehensive installation tutorial for Node.js on Ubuntu (saved HTML reference).
