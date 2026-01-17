#!/usr/bin/env python3
import sys
import signal
sys.path.insert(0, '/home/ubuntu/code/gt/tgk/ubu/sys')

# Set a timeout
def timeout_handler(signum, frame):
    print("TIMEOUT! log_temperature() is hanging!")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)  # 10 second timeout

from temperatureWarn import get_detailed_temps, log_temperature
import temperatureWarn

temperatureWarn.LOG_FILE = '/tmp/temp_final_test.log'

print("Getting temps...")
temp1, edge, temp2 = get_detailed_temps()
print(f'Got temps: temp1={temp1}, edge={edge}, temp2={temp2}')

print('Calling log_temperature()...')
log_temperature(temp1, edge, temp2)
print('✓ log_temperature() completed!')

signal.alarm(0)  # Cancel alarm

import os
if os.path.exists('/tmp/temp_final_test.log'):
    print(f'✓ Log file created!')
    with open('/tmp/temp_final_test.log') as f:
        content = f.read()
        print(f'Log contains {len(content)} bytes, {len(content.splitlines())} lines')
        print('First 200 chars:')
        print(content[:200])
else:
    print('✗ Log file NOT created')
