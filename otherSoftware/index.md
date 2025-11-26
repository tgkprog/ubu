# Other Software

Installation and configuration guides for various third-party software on Ubuntu.

## Documentation

### splunk.txt

**Splunk installation and setup guide** - Instructions for installing and configuring Splunk on Ubuntu.

**Splunk** is a platform for searching, monitoring, and analyzing machine-generated data.

**Typical installation steps:**
```bash
# Download Splunk package (from splunk.com)
wget -O splunk.deb 'https://www.splunk.com/...'

# Install the .deb package
sudo dpkg -i splunk.deb

# Install dependencies if needed
sudo apt install -fy

# Start Splunk
sudo /opt/splunk/bin/splunk start --accept-license

# Enable boot-start
sudo /opt/splunk/bin/splunk enable boot-start
```

**Access Splunk:**
- Default URL: http://localhost:8000
- Default credentials: admin / changeme (change on first login)

**Common operations:**
```bash
# Start Splunk
sudo /opt/splunk/bin/splunk start

# Stop Splunk
sudo /opt/splunk/bin/splunk stop

# Restart Splunk
sudo /opt/splunk/bin/splunk restart

# Check status
sudo /opt/splunk/bin/splunk status
```

See [splunk.txt](splunk.txt) for detailed configuration and usage instructions.
