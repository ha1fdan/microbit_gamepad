import argparse
import subprocess
import sys
from importlib import resources

from .protocol import parse_line


def run(args: argparse.Namespace) -> int:
    from evdev.uinput import UInputError

    from .gamepad import VirtualGamepad
    from .serial_link import read_lines

    try:
        pad = VirtualGamepad(args.deadzone, args.full, args.invert_x, args.invert_y)
    except (PermissionError, UInputError) as e:
        print(f"can't create the virtual gamepad: {e}", file=sys.stderr)
        print("/dev/uinput needs to be writable by you, see the README "
              "(Linux permissions).", file=sys.stderr)
        return 1

    print("virtual gamepad up, ctrl-c to quit")
    try:
        for line in read_lines(args.port):
            state = parse_line(line)
            if state is not None:
                if args.verbose:
                    print(state)
                pad.update(state)
    except KeyboardInterrupt:
        pass
    finally:
        pad.close()
    return 0


def install(args: argparse.Namespace) -> int:
    """Copy the firmware onto the board as main.py."""
    from .serial_link import find_port

    port = args.port or find_port()
    if port is None:
        print("no micro:bit found, is it plugged in?", file=sys.stderr)
        return 1
    src = resources.files("microbit_gamepad") / "firmware" / "main.py"
    with resources.as_file(src) as path:
        cmd = [sys.executable, "-m", "mpremote", "connect", port,
               "cp", str(path), ":main.py", "+", "reset"]
        return subprocess.call(cmd)


def monitor(args: argparse.Namespace) -> int:
    from .serial_link import read_lines

    try:
        for line in read_lines(args.port):
            print(line, end="")
    except KeyboardInterrupt:
        pass
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="microbit-gamepad", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="create the virtual gamepad")
    r.add_argument("-p", "--port", help="serial port (default: auto-detect)")
    r.add_argument("--deadzone", type=int, default=120, help="mg ignored around flat (default 120)")
    r.add_argument("--full", type=int, default=800, help="mg for full deflection (default 800)")
    r.add_argument("--invert-x", action="store_true")
    r.add_argument("--invert-y", action="store_true")
    r.add_argument("-v", "--verbose", action="store_true", help="print every update")
    r.set_defaults(func=run)

    i = sub.add_parser("install", help="copy the firmware onto the micro:bit")
    i.add_argument("-p", "--port")
    i.set_defaults(func=install)

    m = sub.add_parser("monitor", help="print the raw lines from the board")
    m.add_argument("-p", "--port")
    m.set_defaults(func=monitor)

    args = p.parse_args(argv)
    return args.func(args)
