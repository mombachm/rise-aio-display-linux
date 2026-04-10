# Rise AIO Monitor

Linux temperature monitor for the Rise Aura Ice water cooler display (`VID:PID aa88:8666`).

The service reads the `CPU` temperature from the `asusec` sensor when available, falls back to other sensors when needed, and sends the temperature to the display via `PyUSB`.

## Structure

- `rise_aio_usb_settemp.py`: main script
- `rise-aio-monitor-wrapper.sh`: wrapper installed to `/usr/local/bin/rise-aio-monitor`
- `rise-aio-monitor.service`: `systemd` unit
- `install-rise-aio-systemd.sh`: installs the service
- `uninstall-rise-aio-systemd.sh`: removes the service
- `rise-aio-monitor-status.sh`: shows service status/logs
- `requirements.txt`: Python dependencies for `pip`, if preferred

## Dependencies

### Arch Linux

```bash
sudo pacman -S python python-pyusb lm_sensors
```

### Alternative with pip

```bash
python3 -m pip install -r requirements.txt
```

## Installation

From the project directory:

```bash
sudo ./install-rise-aio-systemd.sh
```

The installer:

- copies the script to `/usr/local/lib/rise-aio-monitor/rise_aio_usb_settemp.py`
- installs the wrapper to `/usr/local/bin/rise-aio-monitor`
- installs the unit to `/etc/systemd/system/rise-aio-monitor.service`
- enables and restarts the service

## Usage

Show status:

```bash
./rise-aio-monitor-status.sh
```

Show logs:

```bash
sudo journalctl -u rise-aio-monitor.service -f
```

Restart:

```bash
sudo systemctl restart rise-aio-monitor.service
```

## Removal

```bash
sudo ./uninstall-rise-aio-systemd.sh
```

## License

This project is licensed under the GNU GPL v3.0.

See the [LICENSE](LICENSE) file for the full license text.

## Credits

This project includes protocol and implementation work derived from or inspired by:

- https://github.com/bmortella/wc-aura-ice-linux

The USB payload format used by this project was validated against public Linux implementations for the same `aa88:8666` Rise Aura Ice display device.
