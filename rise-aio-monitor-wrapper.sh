#!/usr/bin/env bash
set -euo pipefail

exec /usr/bin/python3 -u /usr/local/lib/rise-aio-monitor/rise_aio_usb_settemp.py "$@"
