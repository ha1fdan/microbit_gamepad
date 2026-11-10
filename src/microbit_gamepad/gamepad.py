"""Virtual gamepad on top of uinput."""

from evdev import AbsInfo, UInput, ecodes as e

from .protocol import AXIS_MAX, State, tilt_to_axis

BUTTONS = {
    "a": e.BTN_TL2,
    "b": e.BTN_TR2,
    "logo": e.BTN_START,
    "shake": e.BTN_SOUTH,
}

# Never sent, only declared. SDL and friends decide whether a device is a real
# gamepad by looking for the usual button set, so claim all of it.
ADVERTISED = [
    e.BTN_SOUTH, e.BTN_EAST, e.BTN_NORTH, e.BTN_WEST,
    e.BTN_TL, e.BTN_TR, e.BTN_TL2, e.BTN_TR2,
    e.BTN_SELECT, e.BTN_START, e.BTN_MODE,
]


class VirtualGamepad:
    def __init__(self, deadzone: int = 120, full: int = 800,
                 invert_x: bool = False, invert_y: bool = False,
                 name: str = "micro:bit gamepad"):
        self.deadzone, self.full = deadzone, full
        self.invert_x, self.invert_y = invert_x, invert_y
        axis = AbsInfo(value=0, min=-AXIS_MAX, max=AXIS_MAX, fuzz=0, flat=0, resolution=0)
        caps = {
            e.EV_KEY: ADVERTISED,
            e.EV_ABS: [(e.ABS_X, axis), (e.ABS_Y, axis)],
        }
        self.ui = UInput(caps, name=name)
        self._last: dict[int, int] = {}

    def update(self, s: State) -> None:
        for name, code in BUTTONS.items():
            self._send(e.EV_KEY, code, int(getattr(s, name)))
        self._send(e.EV_ABS, e.ABS_X,
                   tilt_to_axis(s.x, self.deadzone, self.full, self.invert_x))
        # tilting the board towards you gives positive y, which is "down" on a stick
        self._send(e.EV_ABS, e.ABS_Y,
                   tilt_to_axis(s.y, self.deadzone, self.full, self.invert_y))
        self.ui.syn()

    def _send(self, etype: int, code: int, value: int) -> None:
        if self._last.get(code) != value:
            self.ui.write(etype, code, value)
            self._last[code] = value

    def close(self) -> None:
        self.ui.close()
