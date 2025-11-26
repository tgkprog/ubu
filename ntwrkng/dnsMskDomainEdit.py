#!/usr/bin/env python3
import sys
import os

CONF = "/etc/dnsmasq.d/lan.conf"

HELP_TEXT = """ 
Usage:
  b.py <domain> <ip> <action>

Params:
  <domain>  DNS domain, e.g. myapi.lan
  <ip>      IP address, e.g. 192.168.1.5 (used only for add)
  <action>  a = add if missing
            c = comment if present
            d = delete if present
"""

def load_lines():
    if not os.path.exists(CONF):
        return []
    with open(CONF, "r") as f:
        return f.readlines()

def save_lines(lines):
    with open(CONF, "w") as f:
        f.writelines(lines)
    os.chmod(CONF, 0o777)

def main():

    # help
    if len(sys.argv) == 2 and sys.argv[1].lower() in ("-h","--help","/?","h","help"):
        print(HELP_TEXT)
        sys.exit(0)

    if len(sys.argv) != 4:
        print("ERROR: usage: b.py <domain> <ip> <action(a/c/d)>")
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
        lines.append(f"address=/{domain}/{ip}\n")
        save_lines(lines)
        print("OK: added")
        return

    # COMMENT
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

    # DELETE
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
