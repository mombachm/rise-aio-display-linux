#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

SERVICE_SRC="$SCRIPT_DIR/rise-aio-monitor.service"
SERVICE_DST="/etc/systemd/system/rise-aio-monitor.service"
SCRIPT_SRC="$SCRIPT_DIR/rise_aio_usb_settemp.py"
SCRIPT_DST="/usr/local/lib/rise-aio-monitor/rise_aio_usb_settemp.py"
WRAPPER_SRC="$SCRIPT_DIR/rise-aio-monitor-wrapper.sh"
WRAPPER_DST="/usr/local/bin/rise-aio-monitor"

if [[ $EUID -ne 0 ]]; then
  echo "run with sudo: sudo $0"
  exit 1
fi

for path in "$SERVICE_SRC" "$SCRIPT_SRC" "$WRAPPER_SRC"; do
  if [[ ! -f "$path" ]]; then
    echo "file not found: $path"
    exit 1
  fi
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found"
  exit 1
fi

if ! python3 -c 'import usb.core, usb.util' >/dev/null 2>&1; then
  echo "PyUSB not found. Install it with:"
  echo "  sudo pacman -S python-pyusb"
  echo "or:"
  echo "  python3 -m pip install -r \"$SCRIPT_DIR/requirements.txt\""
  exit 1
fi

if ! command -v sensors >/dev/null 2>&1; then
  echo "sensors not found. Install it with:"
  echo "  sudo pacman -S lm_sensors"
  exit 1
fi

install -d /usr/local/lib/rise-aio-monitor
install -m 0755 "$SCRIPT_SRC" "$SCRIPT_DST"
install -m 0755 "$WRAPPER_SRC" "$WRAPPER_DST"
install -m 0644 "$SERVICE_SRC" "$SERVICE_DST"

systemctl daemon-reload
systemctl enable rise-aio-monitor.service
systemctl restart rise-aio-monitor.service
systemctl status --no-pager --full rise-aio-monitor.service
