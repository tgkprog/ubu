#!/usr/bin/env python3
"""
System Process Pause Utility
Pauses non-essential processes and services to optimize system resources.
Logs actions for later restoration.
"""

import psutil
import json
import logging
import subprocess
import time
import sys
from datetime import datetime
import os

# Configure logging
log_file = os.path.join(os.path.dirname(__file__), 'pause_actions.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file
)
# Ensure log file has proper permissions
if os.path.exists(log_file):
    os.chmod(log_file, 0o777)


class SystemPauser:
    def __init__(self):
        self.paused_state_file = os.path.join(
            os.path.dirname(__file__), 'paused_state.json')
        self.load_system_report()

    def load_system_report(self):
        """Load the current system report"""
        report_path = os.path.join(
            os.path.dirname(__file__), 'system_report.json')
        try:
            with open(report_path, 'r') as f:
                self.system_report = json.load(f)
        except FileNotFoundError:
            logging.error(
                "System report not found. Please run report.py first.")
            raise SystemExit(1)

    def pause_service(self, service_name):
        """Pause a system service using systemctl"""
        try:
            cmd = ['systemctl', 'stop', service_name]
            subprocess.run(cmd, check=True)
            logging.info(f"Successfully stopped service: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to stop service {service_name}: {str(e)}")
            return False

    def pause_process(self, pid, name):
        """Pause a process using SIGSTOP, with exceptions for kworker"""
        try:
            process = psutil.Process(pid)

            # Skip kworker processes with less than 0.1% CPU usage
            if 'kworker' in name.lower() and process.cpu_percent(interval=0.1) < 0.1:
                logging.info(
                    f"Skipping kworker process: {name} (PID: {pid}) due to low CPU usage")
                return False

            process.suspend()
            logging.info(
                f"Successfully suspended process: {name} (PID: {pid})")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(
                f"Failed to suspend process {name} (PID: {pid}): {str(e)}")
            return False

    def save_paused_state(self, paused_services, paused_processes):
        """Save the state of paused services and processes"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'services': paused_services,
            'processes': paused_processes
        }
        with open(self.paused_state_file, 'w') as f:
            json.dump(state, f, indent=2)
        os.chmod(self.paused_state_file, 0o777)
        logging.info(f"Saved paused state to {self.paused_state_file}")

    def pause_system(self):
        """Pause non-essential services and processes"""
        paused_services = []
        paused_processes = []

        # Pause pausable services first
        for service in self.system_report.get('pausable_services', []):
            # Extract service name from command (e.g., 'cups' from 'cupsd')
            service_name = service['name'].replace('d', '')  # Simple heuristic
            if self.pause_service(service_name):
                paused_services.append({
                    'name': service_name,
                    'pid': service['pid'],
                    'command': service['command']
                })

        # Pause pausable processes
        for process in self.system_report.get('pausable_processes', []):
            # Skip browser processes that are essential
            if 'chrome' in process['name'].lower() and any(
                term in process['command'].lower()
                for term in ['--type=gpu-process', '--type=utility']
            ):
                continue

            if self.pause_process(process['pid'], process['name']):
                paused_processes.append({
                    'name': process['name'],
                    'pid': process['pid'],
                    'command': process['command']
                })

        # Save the state for later restoration
        self.save_paused_state(paused_services, paused_processes)

        # Log summary
        logging.info(
            f"Paused {len(paused_services)} services and {len(paused_processes)} processes")
        print(
            f"Successfully paused {len(paused_services)} services and {len(paused_processes)} processes")
        print("See pause_actions.log for details")


def main():
    try:
        pauser = SystemPauser()
        pauser.pause_system()
    except Exception as e:
        logging.error(f"Error during system pause: {str(e)}")
        raise


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Error: This script must be run as root (with sudo)")
        sys.exit(1)
    main()
