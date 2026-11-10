"""Parsing for the lines the firmware sends, and tilt -> axis maths."""

from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    a: bool
    b: bool
    logo: bool
    shake: bool
    x: int  # milli-g
    y: int  # milli-g


def parse_line(line: str) -> State | None:
    """Turn 'G 1 0 0 1 -120 340' into a State. Returns None for anything else.

    The REPL banner and half-written lines show up on the port now and then,
    so bad input is ignored instead of raising.
    """
    parts = line.strip().split()
    if len(parts) != 7 or parts[0] != "G":
        return None
    try:
        a, b, logo, shake, x, y = (int(p) for p in parts[1:])
    except ValueError:
        return None
    return State(bool(a), bool(b), bool(logo), bool(shake), x, y)


AXIS_MAX = 32767


def tilt_to_axis(mg: int, deadzone: int = 120, full: int = 800, invert: bool = False) -> int:
    """Map a tilt reading (milli-g) to a signed 16 bit stick value.

    Anything inside the deadzone is 0, `full` mg or more is full deflection.
    """
    if full <= deadzone:
        raise ValueError("full must be larger than deadzone")
    mag = abs(mg)
    if mag <= deadzone:
        return 0
    scaled = min(1.0, (mag - deadzone) / (full - deadzone))
    value = round(scaled * AXIS_MAX)
    if (mg < 0) != invert:
        value = -value
    return value
