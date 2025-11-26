#!/usr/bin/env python3
import sys
import os

CONF = "/etc/dnsmasq.d/lan.conf"

HELP_TEXT = """
Usage:
  script.py <domain> <action>

Params:
  <domain>  The DNS domain, e.g. myapi.lan
  <action>  One of:
            a = add if missing
            c = comment if present and not commented
            d = delete if present

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

def main():
    # Help flags
    if len(sys.argv) == 2 and sys.argv[1].lower() in ("-h", "--help", "/?", "h", "-help", "help"):
        print(HELP_TEXT)
        sys.exit(0)

    if len(sys.argv) != 3:
        print("ERROR: usage: script.py <domain> action(a/c/d)")
        sys.exit(1)

    domain = sys.argv[1].strip().lower()
    action = sys.argv[2].strip().lower()

    if action not in ("a", "c", "d"):
        print("ERROR: action must be a/c/d")
        sys.exit(1)

    lines = load_lines()
    target_prefix = f"address=/{domain}/"
    found_idx = None

    for i, line in enumerate(lines):
        if target_prefix in line:
            found_idx = i
            break

    # ADD
    if action == "a":
        if found_idx is not None and not lines[found_idx].lstrip().startswith("#"):
            print("OK: already exists")
            return

        ip = input(f"Enter IP for {domain}: ").strip()
        if not ip:
            print("ERROR: IP empty")
            return

        try:
            lines.append(f"address=/{domain}/{ip}\\n")
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

