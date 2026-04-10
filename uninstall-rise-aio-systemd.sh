#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "rode com sudo: sudo $0"
  exit 1
fi

systemctl disable --now rise-aio-monitor.service 2>/dev/null || true
rm -f /etc/systemd/system/rise-aio-monitor.service
rm -f /usr/local/bin/rise-aio-monitor
rm -f /usr/local/lib/rise-aio-monitor/rise_aio_usb_settemp.py
rmdir /usr/local/lib/rise-aio-monitor 2>/dev/null || true
systemctl daemon-reload

echo "rise-aio-monitor removido"
