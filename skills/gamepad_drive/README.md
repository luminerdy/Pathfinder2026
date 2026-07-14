# Gamepad Remote Control - Quick Reference

**Drive with Logitech F710 wireless gamepad**

## Setup
1. Plug F710 USB receiver into **robot Pi**
2. Gamepad on, back switch to **X**
3. Confirm the robot image includes `python3-pygame` and `joystick`
4. `python3 skills/gamepad_drive/gamepad_drive.py`

For an older image only, install missing packages with:

```bash
sudo apt install -y python3-pygame joystick
```

## Controls

| Control | Action |
|---------|--------|
| Left stick Y | Left wheels forward/backward |
| Right stick Y | Right wheels forward/backward |
| Either stick X | Strafe all wheels (mecanum) |
| Right trigger | Forward (analog) |
| Left trigger | Backward (analog) |
| Right bumper | Turn right |
| Left bumper | Turn left |
| A | Camera forward |
| B | Open claw |
| Y | Nod yes |
| X | Shake no |
| D-pad Up | Front pickup |
| D-pad Down | Drop into rear bin |
| D-pad Left | AprilTag navigation automation |
| D-pad Right | Line following automation |
| **Back** | **EMERGENCY STOP** |
| **Start** | **Quit** |

## Automation Shortcuts

- `D-pad Left` moves the arm/camera to look forward, runs AprilTag navigation, then returns to gamepad control.
- `D-pad Right` runs line following, then returns to gamepad control.
- Press `Back` or `Start` while an automation is running to cancel it and return to gamepad control.

---
If no gamepad is detected when the script starts, the robot beeps and keeps checking until the gamepad is connected.
