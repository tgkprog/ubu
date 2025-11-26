# Security

Security commands and file permission management for Ubuntu systems.

## Files

### secure.gh

**File permission commands reference** - chmod and file security operations.

**Common chmod patterns:**
```bash
# Make file executable
chmod +x script.sh

# Set specific permissions (rwxr-xr-x)
chmod 755 file.sh

# Set file read/write for owner only
chmod 600 private.txt

# Recursive permission change
chmod -R 755 /path/to/directory

# Numeric permissions breakdown:
# 7 = rwx (read, write, execute)
# 6 = rw- (read, write)
# 5 = r-x (read, execute)
# 4 = r-- (read only)
# 0 = --- (no permissions)

# Examples:
# 777 = rwxrwxrwx (all permissions for everyone)
# 755 = rwxr-xr-x (owner: all, group/others: read+execute)
# 644 = rw-r--r-- (owner: read+write, group/others: read only)
```

**Ownership commands:**
```bash
# Change file owner
sudo chown user:group file.txt

# Recursive ownership change
sudo chown -R user:group /path/to/directory

# Change only owner
sudo chown user file.txt

# Change only group
sudo chgrp group file.txt
```

**Viewing permissions:**
```bash
# List with permissions
ls -la

# Show permissions in octal
stat -c "%a %n" file.txt
```
