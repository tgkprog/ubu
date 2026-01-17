#!/usr/bin/env bash

# Create log file with header
LOG=/tmp/temperature_log.txt

cat <<EOF > $LOG
========================================
Laptop Temperature Log
Host      : $(hostname)
OS        : Ubuntu 24
Started   : $(date)
Interval  : 10 seconds
Tool      : lm-sensors
========================================

EOF
# Start logging (Ctrl+C to stop)
while true; do
  echo "----- $(date '+%Y-%m-%d %H:%M:%S') -----" >> $LOG
  sensors >> $LOG
  echo >> $LOG
  sleep 10
done
