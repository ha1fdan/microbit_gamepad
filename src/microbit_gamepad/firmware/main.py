# Runs on the micro:bit (V2). Streams input over USB serial, one line per update:
#   G <a> <b> <logo> <shake> <x> <y>
# the first four are 0/1, x and y are accelerometer readings in milli-g.
# On the PC: A is L2, B is R2, logo is Start, shake is South.
from microbit import *
import music

PERIOD = 15       # ms between samples
HEARTBEAT = 100   # resend at least this often so the host knows we're alive
SHAKE_HOLD = 150  # ms to keep "shake" pressed, the gesture itself is momentary
NBUTTONS = 4

# frequency in Hz for a, b, logo, shake. None mutes that input
SOUNDS = (440, 660, 880, 550)

last = None
since = 0
shake_left = 0

music.play(["c4:2", "e4:2", "g4:2", "c5:4"], wait=False)

while True:
    if accelerometer.is_gesture("shake"):
        shake_left = SHAKE_HOLD
    elif shake_left > 0:
        shake_left -= PERIOD

    state = (
        int(button_a.is_pressed()),
        int(button_b.is_pressed()),
        int(pin_logo.is_touched()),
        int(shake_left > 0),
        accelerometer.get_x(),
        accelerometer.get_y(),
    )
    # accel jitters by a few mg, only send real changes
    changed = last is None or state[:NBUTTONS] != last[:NBUTTONS] or \
        abs(state[4] - last[4]) > 8 or abs(state[5] - last[5]) > 8
    if last is not None:
        for i in range(NBUTTONS):
            # beep on press only, not release
            if state[i] and not last[i] and SOUNDS[i]:
                music.pitch(SOUNDS[i], 80, wait=False)
    if changed or since >= HEARTBEAT:
        print("G %d %d %d %d %d %d" % state)
        last = state
        since = 0

        # little dot that follows the tilt
        display.clear()
        px = max(0, min(4, 2 + state[4] // 400))
        py = max(0, min(4, 2 + state[5] // 400))
        display.set_pixel(px, py, 9)
        if state[0]:
            display.set_pixel(0, 0, 5)
        if state[1]:
            display.set_pixel(4, 0, 5)
        if state[3]:
            display.set_pixel(2, 4, 5)
    sleep(PERIOD)
    since += PERIOD
