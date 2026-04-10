#!/usr/bin/env python3
import argparse
import json
import subprocess
import time

import usb.core
import usb.util


VID = 0xAA88
PID = 0x8666
CPU_SYSFS_CANDIDATES = (
    "/sys/class/hwmon/hwmon4/temp1_input",
    "/sys/devices/platform/asus-ec-sensors/hwmon/hwmon4/temp1_input",
)


def find_device():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        raise SystemExit("device aa88:8666 not found")
    return dev


def prepare_device(dev, do_reset=False):
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    if do_reset:
        dev.reset()
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]
    ep = next(
        (e for e in intf if usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT),
        None,
    )
    if ep is None:
        raise SystemExit("USB OUT endpoint not found")
    return ep


def payload_bmortella(temp: int):
    return [temp, 0x1C, 0x00, 0x00, 0x1C, 0x00, 0x00, 0x00]


def payload_ronaldo(temp: int):
    second = 0x0C if temp < 16 else 0x1C
    return [temp, second, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00]


def get_cpu_temp_c_sysfs():
    for path in CPU_SYSFS_CANDIDATES:
        try:
            with open(path, "r", encoding="ascii") as fh:
                raw = fh.read().strip()
            return int(round(int(raw) / 1000))
        except (FileNotFoundError, ValueError, OSError):
            continue
    return None


def get_cpu_temp_c():
    temp = get_cpu_temp_c_sysfs()
    if temp is not None:
        return temp

    out = subprocess.check_output(["sensors", "-j"], text=True)
    data = json.loads(out)

    asusec = data.get("asusec-isa-000a", {})
    cpu = asusec.get("CPU", {}).get("temp1_input")
    if cpu is not None:
        return int(round(cpu))

    k10 = data.get("k10temp-pci-00c3", {})
    tctl = k10.get("Tctl", {}).get("temp1_input")
    if tctl is not None:
        return int(round(tctl))

    for chip in data.values():
        if isinstance(chip, dict):
            for sensor in chip.values():
                if isinstance(sensor, dict):
                    for key, val in sensor.items():
                        if key.endswith("_input") and isinstance(val, (int, float)):
                            return int(round(val))
    raise RuntimeError("no temperature sensor found from `sensors -j`")


def send_payload(ep, payload, repeat=1, interval=0.05):
    for _ in range(repeat):
        ep.write(payload)
        time.sleep(interval)


def cmd_info(_args):
    dev = find_device()
    ep = prepare_device(dev, do_reset=False)
    print(f"device={hex(VID)}:{hex(PID)}")
    print(f"out_endpoint=0x{ep.bEndpointAddress:02x}")
    print(f"max_packet_size={ep.wMaxPacketSize}")
    usb.util.dispose_resources(dev)
    return 0


def cmd_set(args):
    temp = max(0, min(99, args.temp))
    dev = find_device()
    ep = prepare_device(dev, do_reset=args.reset)
    payload = payload_bmortella(temp) if args.mode == "bmortella" else payload_ronaldo(temp)
    print(f"mode={args.mode} temp={temp} payload={' '.join(f'{b:02x}' for b in payload)}")
    send_payload(ep, payload, repeat=args.repeat, interval=args.interval)
    usb.util.dispose_resources(dev)
    return 0


def cmd_watch(args):
    dev = find_device()
    ep = prepare_device(dev, do_reset=args.reset)
    try:
        while True:
            temp = max(0, min(99, get_cpu_temp_c()))
            payload = payload_bmortella(temp) if args.mode == "bmortella" else payload_ronaldo(temp)
            print(f"mode={args.mode} temp={temp} payload={' '.join(f'{b:02x}' for b in payload)}")
            send_payload(ep, payload, repeat=args.repeat, interval=args.interval)
            time.sleep(args.period)
    finally:
        usb.util.dispose_resources(dev)


def build_parser():
    parser = argparse.ArgumentParser(description="Send temperatures to Rise Mode Aura Ice over PyUSB.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_info = sub.add_parser("info", help="Show endpoint info")
    p_info.set_defaults(func=cmd_info)

    p_set = sub.add_parser("set", help="Set a fixed temperature")
    p_set.add_argument("temp", type=int)
    p_set.add_argument("--mode", choices=("bmortella", "ronaldo"), default="bmortella")
    p_set.add_argument("--repeat", type=int, default=5)
    p_set.add_argument("--interval", type=float, default=0.05)
    p_set.add_argument("--reset", action="store_true")
    p_set.set_defaults(func=cmd_set)

    p_watch = sub.add_parser("watch", help="Continuously update from system sensors")
    p_watch.add_argument("--mode", choices=("bmortella", "ronaldo"), default="bmortella")
    p_watch.add_argument("--repeat", type=int, default=5)
    p_watch.add_argument("--interval", type=float, default=0.05)
    p_watch.add_argument("--period", type=float, default=1.0)
    p_watch.add_argument("--reset", action="store_true")
    p_watch.set_defaults(func=cmd_watch)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
