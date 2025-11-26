# Network Configuration Scripts

Network utilities and DNS management scripts for Ubuntu systems.

## Scripts

### dnsMskDomainEdit.py

A Python utility for managing dnsmasq DNS configurations. Allows you to add, comment, or delete domain entries in `/etc/dnsmasq.d/lan.conf`.

**Requirements:**
- Python 3.x
- Sudo access (modifies `/etc/dnsmasq.d/lan.conf`)

**Usage:**
```bash
sudo python3 dnsMskDomainEdit.py <domain> <ip> <action>
```

**Parameters:**
- `<domain>` - DNS domain name (e.g., myapi.lan)
- `<ip>` - IP address (e.g., 192.168.1.5) - used only for add action
- `<action>` - Action to perform:
  - `a` - Add domain if not present
  - `c` - Comment out domain if present
  - `d` - Delete domain if present

**Examples:**
```bash
# Add a new domain entry
sudo python3 dnsMskDomainEdit.py myapi.lan 192.168.1.5 a

# Comment out an existing domain
sudo python3 dnsMskDomainEdit.py myapi.lan 192.168.1.5 c

# Delete a domain entry
sudo python3 dnsMskDomainEdit.py myapi.lan 192.168.1.5 d

# Show help
python3 dnsMskDomainEdit.py --help
```

**Notes:**
- Requires sudo permissions as it modifies system DNS configuration
- After making changes, restart dnsmasq service: `sudo systemctl restart dnsmasq`
- Changes are written with appropriate permissions (chmod 777) for accessibility

## Configuration Files

- `/etc/dnsmasq.d/lan.conf` - Main dnsmasq configuration file (managed by dnsMskDomainEdit.py)

## Dnsmasq Setup

If dnsmasq is not installed:
```bash
sudo apt-get update
sudo apt-get install dnsmasq
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq
```

## Troubleshooting

- Ensure dnsmasq service is running: `sudo systemctl status dnsmasq`
- Check configuration syntax: `sudo dnsmasq --test`
- View dnsmasq logs: `sudo journalctl -u dnsmasq -f`
