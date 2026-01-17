#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="temperature-warn.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"
WARN_THRESHOLD="${1:-73}"
CRITICAL_THRESHOLD="${2:-78}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/temperatureWarn.py"
SERVICE_USER="${SUDO_USER:-$USER}"
SERVICE_UID="$(id -u "${SERVICE_USER}")"

if [[ ! -f "${PYTHON_SCRIPT}" ]]; then
  echo "Temperature monitor script not found at ${PYTHON_SCRIPT}" >&2
  exit 1
fi

cat <<EOF | sudo tee "${SERVICE_FILE}" > /dev/null
[Unit]
Description=Temperature monitor (warn >= ${WARN_THRESHOLD}°C, critical >= ${CRITICAL_THRESHOLD}°C)
After=multi-user.target

[Service]
Type=simple
User=${SERVICE_USER}
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/${SERVICE_USER}/.Xauthority
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/${SERVICE_UID}/bus
ExecStart=/usr/bin/env python3 "${PYTHON_SCRIPT}" --warn ${WARN_THRESHOLD} --critical ${CRITICAL_THRESHOLD}
Restart=always
RestartSec=10
WorkingDirectory=${SCRIPT_DIR}

[Install]
WantedBy=multi-user.target
EOF

sudo chmod 644 "${SERVICE_FILE}"
sudo systemctl daemon-reload
sudo systemctl enable --now "${SERVICE_NAME}"

echo "Service ${SERVICE_NAME} installed and started. Check status via:"
echo "  sudo systemctl status ${SERVICE_NAME}"
