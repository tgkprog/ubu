# LAN DNS on Ubuntu 24.04

A simple local DNS setup using **dnsmasq** so your laptop resolves custom LAN‑only domains (e.g. `myapi.lan` → `192.168.1.5`).  
Includes enable/disable instructions and a helper Python script to add/comment/delete domain entries.

---

## 1. Install dnsmasq

```sh
sudo apt update
sudo apt install dnsmasq
```

---

## 2. Main config file

We use:

```
/etc/dnsmasq.d/lan.conf
```

Create or edit it:

```sh
sudo nano /etc/dnsmasq.d/lan.conf
```

Example content:

```
address=/myapi.lan/192.168.1.5
```

---

## 3. Enable DNS service

```sh
sudo systemctl enable dnsmasq
sudo systemctl start dnsmasq
```

Check status:

```sh
systemctl status dnsmasq
```

---

## 4. Disable DNS service

```sh
sudo systemctl stop dnsmasq
sudo systemctl disable dnsmasq
```

---

## 5. Reload after config changes

```sh
sudo systemctl reload dnsmasq
```

---

## 6. Point your phone or other device to use laptop as DNS

Set the DNS server IP to your laptop IP, e.g.:

```
192.168.1.10
```

---

## 7. Python helper script

A CLI script to **add**, **comment**, or **delete** a domain entry.

Save as: `lan_dns_edit.py`

```python
#!/usr/bin/env python3
import sys
import os

CONF = "/etc/dnsmasq.d/lan.conf"

def load_lines():
    if not os.path.exists(CONF):
        return []
    with open(CONF, "r") as f:
        return f.readlines()

def save_lines(lines):
    with open(CONF, "w") as f:
        f.writelines(lines)

def main():
    if len(sys.argv) != 3:
        print("ERROR: usage: lan_dns_edit.py domain action(a/c/d)")
        sys.exit(1)

    domain = sys.argv[1].strip().lower()
    action = sys.argv[2].strip().lower()

    if action not in ("a","c","d"):
        print("ERROR: action must be a/c/d")
        sys.exit(1)

    lines = load_lines()
    target = f"address=/{domain}/"
    found_idx = None

    for i, line in enumerate(lines):
        if target in line:
            found_idx = i
            break

    # --- ADD ---
    if action == "a":
        if found_idx is not None and not lines[found_idx].lstrip().startswith("#"):
            print("OK: already exists")
            return
        ip = input(f"Enter IP for {domain}: ").strip()
        lines.append(f"address=/{domain}/{ip}\n")
        save_lines(lines)
        print("OK: added")
        return

    # --- COMMENT ---
    if action == "c":
        if found_idx is None:
            print("NOT FOUND")
            return
        if lines[found_idx].lstrip().startswith("#"):
            print("OK: already commented")
            return
        lines[found_idx] = "#" + lines[found_idx]
        save_lines(lines)
        print("OK: commented")
        return

    # --- DELETE ---
    if action == "d":
        if found_idx is None:
            print("NOT FOUND")
            return
        del lines[found_idx]
        save_lines(lines)
        print("OK: deleted")
        return

if __name__ == "__main__":
    main()
```

Make executable:

```sh
chmod +x lan_dns_edit.py
```

Run:

```
sudo ./lan_dns_edit.py myapi.lan a
sudo ./lan_dns_edit.py myapi.lan c
sudo ./lan_dns_edit.py myapi.lan d
```

---

## 8. Test DNS resolution

```sh
dig myapi.lan @127.0.0.1
```

Or from another device (phone pointed to laptop DNS).  
Expected answer section should show your IP (e.g. `192.168.1.5`).

---

## 9. Log + Troubleshooting

dnsmasq logs appear in:

```
/var/log/syslog
```

To view live:

```sh
sudo journalctl -u dnsmasq -f
```
