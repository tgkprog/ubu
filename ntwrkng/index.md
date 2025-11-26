# Networking

Ubuntu networking commands, configurations, and troubleshooting guides.

## Documentation

- [LAN DNS Setup Guide](lanDns.md) - Complete guide to setting up dnsmasq for local DNS resolution
- [DNS Management Tools](README.md) - Documentation for DNS management scripts and utilities

## Scripts

### dnsMskDomainEdit.py

A Python utility for managing dnsmasq DNS configurations. Allows you to add, comment, delete, or list domain entries in `/etc/dnsmasq.d/lan.conf`.

**Usage:**
```bash
# Add a new domain entry
sudo python3 dnsMskDomainEdit.py myapi.lan 192.168.1.5 a

# Comment out an existing domain
sudo python3 dnsMskDomainEdit.py myapi.lan 192.168.1.5 c

# Delete a domain entry
sudo python3 dnsMskDomainEdit.py myapi.lan 192.168.1.5 d

# List all configured domains
python3 dnsMskDomainEdit.py l

# Show help
python3 dnsMskDomainEdit.py --help
```

**Actions:**
- `a` - Add domain if not present
- `c` - Comment out domain if present
- `d` - Delete domain if present
- `l` or `L` - List all configured domains (active and commented)

See [README.md](README.md) for detailed documentation and setup instructions.
