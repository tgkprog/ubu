#!/usr/bin/env python3
import sys
import os

CONF = "/etc/dnsmasq.d/lan.conf"

HELP_TEXT = """ 
Usage:
  dnsMskDomainEdit.py <domain> <ip> <action>
  dnsMskDomainEdit.py l|L  (list all domains)

Params:
  <domain>  DNS domain, e.g. myapi.lan
  <ip>      IP address, e.g. 192.168.1.5 (used only for add)
  <action>  a = add if missing
            c = comment if present
            d = delete if present
            l/L = list all configured domains

All operations print clear errors and short success messages:
  - OK: added
  - OK: commented
  - OK: deleted
  - NOT FOUND
  - OK: already exists
  - OK: already commented
"""

def load_lines():
    if not os.path.exists(CONF):
        return []
    try:
        with open(CONF, "r") as f:
            return f.readlines()
    except Exception as e:
        print(f"ERROR: failed to read {CONF} -> {e}")
        sys.exit(1)

def save_lines(lines):
    try:
        with open(CONF, "w") as f:
            f.writelines(lines)
        os.chmod(CONF, 0o777)
    except Exception as e:
        print(f"ERROR: failed to write {CONF} -> {e}")
        sys.exit(1)

def list_domains():
    lines = load_lines()
    if not lines:
        print("No domains configured.")
        return
    
    print("\nConfigured DNS Domains:")
    print("-" * 60)
    active = []
    commented = []
    
    for line in lines:
        line = line.strip()
        if not line or not "address=/" in line:
            continue
        
        is_commented = line.startswith("#")
        if is_commented:
            line = line.lstrip("#").strip()
        
        # Parse: address=/domain/ip
        if line.startswith("address=/"):
            parts = line.split("/")
            if len(parts) >= 3:
                domain = parts[1]
                ip = parts[2]
                if is_commented:
                    commented.append((domain, ip))
                else:
                    active.append((domain, ip))
    
    if active:
        print("\nActive Domains:")
        for domain, ip in active:
            print(f"  ✓ {domain:<30} -> {ip}")
    
    if commented:
        print("\nCommented Domains:")
        for domain, ip in commented:
            print(f"  # {domain:<30} -> {ip}")
    
    if not active and not commented:
        print("No domains found.")
    
    print("-" * 60)

def main():

    # help
    if len(sys.argv) == 2 and sys.argv[1].lower() in ("-h","--help","/?","h","-help","help"):
        print(HELP_TEXT)
        sys.exit(0)

    # list domains
    if len(sys.argv) == 2 and sys.argv[1].lower() == "l":
        list_domains()
        sys.exit(0)

    if len(sys.argv) != 4:
        print("ERROR: usage: dnsMskDomainEdit.py <domain> <ip> <action(a/c/d)> OR dnsMskDomainEdit.py l")
        sys.exit(1)

    domain = sys.argv[1].strip().lower()
    ip = sys.argv[2].strip()
    action = sys.argv[3].strip().lower()

    if action not in ("a","c","d"):
        print("ERROR: action must be a/c/d")
        sys.exit(1)

    lines = load_lines()
    prefix = f"address=/{domain}/"

    found_idx = None
    for i, line in enumerate(lines):
        if prefix in line:
            found_idx = i
            break

    # ADD
    if action == "a":
        if found_idx is not None and not lines[found_idx].lstrip().startswith("#"):
            print("OK: already exists")
            return
        try:
            lines.append(f"address=/{domain}/{ip}\n")
            save_lines(lines)
            print("OK: added")
        except Exception as e:
            print(f"ERROR: add failed -> {e}")
        return

    # COMMENT
    if action == "c":
        if found_idx is None:
            print("NOT FOUND")
            return
        if lines[found_idx].lstrip().startswith("#"):
            print("OK: already commented")
            return
        try:
            lines[found_idx] = "#" + lines[found_idx]
            save_lines(lines)
            print("OK: commented")
        except Exception as e:
            print(f"ERROR: comment failed -> {e}")
        return

    # DELETE
    if action == "d":
        if found_idx is None:
            print("NOT FOUND")
            return
        try:
            del lines[found_idx]
            save_lines(lines)
            print("OK: deleted")
        except Exception as e:
            print(f"ERROR: delete failed -> {e}")
        return

if __name__ == "__main__":
    main()
