#!/usr/bin/env bash
set -euo pipefail

sudo systemctl status --no-pager --full rise-aio-monitor.service
