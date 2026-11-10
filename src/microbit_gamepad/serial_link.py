"""Finding the micro:bit and reading lines from it."""

import time
from collections.abc import Iterator

import serial
from serial.tools import list_ports

# DAPLink on the micro:bit
VID, PID = 0x0D28, 0x0204
BAUD = 115200


def find_port() -> str | None:
    for p in list_ports.comports():
        if p.vid == VID and p.pid == PID:
            return p.device
    return None


def read_lines(port: str | None = None, retry: float = 1.0) -> Iterator[str]:
    """Yield lines forever, reconnecting if the board gets unplugged."""
    waiting_said = False
    while True:
        dev = port or find_port()
        if dev is None:
            if not waiting_said:
                print("waiting for a micro:bit...")
                waiting_said = True
            time.sleep(retry)
            continue
        try:
            with serial.Serial(dev, BAUD, timeout=1) as ser:
                print(f"connected on {dev}")
                waiting_said = False
                while True:
                    raw = ser.readline()
                    if raw:
                        yield raw.decode("ascii", errors="ignore")
        except serial.SerialException as e:
            print(f"lost connection: {e}")
            time.sleep(retry)
