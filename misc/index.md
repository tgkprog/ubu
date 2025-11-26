# Miscellaneous

Various Ubuntu commands, scripts, and utilities that don't fit other categories.

## Documentation

### Create Symlink in Linux ln -s.txt

**Symbolic link creation guide**

**Basic syntax:**
```bash
ln -s /path/to/original /path/to/link
```

**Examples:**
```bash
# Create symlink to file
ln -s /usr/bin/python3 /usr/local/bin/python

# Create symlink to directory
ln -s /var/www/html /home/user/www

# Verify symlink
ls -la /path/to/link
```

### find_exec.txt

**Find and execute command patterns** - Using find with -exec to batch process files.

**Common patterns:**
```bash
# Find and execute command on files
find /path -name "*.log" -exec rm {} \;

# Find and process with confirmation
find /path -name "*.txt" -exec chmod 644 {} \;

# Find and execute complex commands
find . -type f -name "*.sh" -exec bash -c 'echo "Processing: $1"' _ {} \;
```

## Scripts

### mkFiles.sh

**Batch file creation script** - Utility for creating multiple files or directories at once.

**Usage:**
```bash
./mkFiles.sh
```

## Additional Resources

- **docs/** - Additional documentation and guides
- **generalBashScripts/** - Collection of general-purpose bash utilities
