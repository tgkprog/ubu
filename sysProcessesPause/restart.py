#!/usr/bin/env python3
"""
System Process Restart Utility
Restores previously paused processes and services.
"""

import psutil
import json
import logging
import subprocess
import time
from datetime import datetime
import os

# Configure logging
log_file = os.path.join(os.path.dirname(__file__), 'restart_actions.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file
)
# Ensure log file has proper permissions
if os.path.exists(log_file):
    os.chmod(log_file, 0o777)

class SystemRestarter:
    def __init__(self):
        self.paused_state_file = os.path.join(os.path.dirname(__file__), 'paused_state.json')

    def load_paused_state(self):
        """Load the state of paused services and processes"""
        try:
            with open(self.paused_state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error("No paused state file found. Nothing to restore.")
            return None

    def restart_service(self, service_name):
        """Restart a system service using systemctl"""
        try:
            cmd = ['systemctl', 'start', service_name]
            subprocess.run(cmd, check=True)
            logging.info(f"Successfully started service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to start service {service_name}: {str(e)}")
            return False

    def resume_process(self, pid, name):
        """Resume a process using SIGCONT"""
        try:
            process = psutil.Process(pid)
            process.resume()
            logging.info(f"Successfully resumed process: {name} (PID: {pid})")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Failed to resume process {name} (PID: {pid}): {str(e)}")
            # If process doesn't exist, try to restart it using the command
            return False

    def restart_process(self, command):
        """Restart a process using its original command"""
        try:
            subprocess.Popen(command.split())
            logging.info(f"Successfully restarted process with command: {command}")
            return True
        except subprocess.SubprocessError as e:
            logging.error(f"Failed to restart process with command {command}: {str(e)}")
            return False

    def restore_system(self):
        """Restore previously paused services and processes"""
        state = self.load_paused_state()
        if not state:
            return

        restored_services = 0
        restored_processes = 0

        # Restore services first
        for service in state.get('services', []):
            if self.restart_service(service['name']):
                restored_services += 1

        # Restore processes
        for process in state.get('processes', []):
            if not self.resume_process(process['pid'], process['name']):
                # If resume fails, try to restart the process
                if self.restart_process(process['command']):
                    restored_processes += 1

        # Log summary
        logging.info(f"Restored {restored_services} services and {restored_processes} processes")
        print(f"Successfully restored {restored_services} services and {restored_processes} processes")
        print("See restart_actions.log for details")

        # Clean up the state file
        try:
            os.remove(self.paused_state_file)
            logging.info("Cleaned up paused state file")
        except FileNotFoundError:
            pass

def main():
    try:
        restarter = SystemRestarter()
        restarter.restore_system()
    except Exception as e:
        logging.error(f"Error during system restore: {str(e)}")
        raise

if __name__ == "__main__":
    main()