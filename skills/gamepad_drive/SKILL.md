# Skill: Gamepad Remote Control (E2)

**Difficulty:** Beginner - Plug and Play
**Type:** Manual Control
**Prerequisites:** C2 (Connected to robot)
**Estimated Time:** 10 minutes

---

> **Note - Raw API for learning:** The code examples in this guide use the low-level hardware API directly (`board.set_motor_duty()`, etc.) so you can see exactly what's happening inside the robot. Your **starter templates** use the `robot` class which wraps all of this - same concepts, cleaner code.

## Overview

Drive your robot with a Logitech F710 wireless gamepad. Tank-style stick control with mecanum strafing, trigger-based speed control, bumper turns, and D-pad arm actions.

The gamepad plugs into the **robot Pi** (not the Pi 500). You control from the couch, the robot drives on the field.

### Why Gamepad?

- Fastest way to drive the robot manually
- No coding required
- Great for scouting the field before writing autonomous code
- Fun for demonstrations and practice

---

## Quick Start

### Step 1: Hardware Setup

1. Plug the **F710 USB wireless receiver** into the **robot Pi** (any USB port)
2. Turn on the gamepad (center button)
3. Set the **back switch to X** (XInput mode, not D/DirectInput)
4. Check the green LED is on (connected)

### Step 2: Confirm Dependencies

The Pathfinder2026 robot image should already include `python3-pygame` and `joystick`. For an older image only, install missing packages from the robot:

```bash
ssh robot@<ROBOT_IP>
sudo apt install -y python3-pygame joystick
```

Verify the gamepad is detected:
```bash
lsusb | grep -i logitech
# Should show: Logitech, Inc. F710 Wireless Gamepad
```

### Step 3: Run Gamepad Drive

```bash
cd /home/robot/pathfinder
python3 skills/gamepad_drive/gamepad_drive.py
```

You should see:
```
Initializing robot hardware...
Initializing gamepad...
Gamepad: Logitech Gamepad F710
Ready - drive with sticks, triggers, bumpers!
```

If "No gamepad detected" appears, the robot beeps and keeps checking. Connect the USB receiver or turn on the gamepad, or press Ctrl+C to quit.

---

## Controls

### Sticks - Driving

| Control | Action |
|---------|--------|
| **Left stick Y** | Forward / backward (tank left side) |
| **Right stick Y** | Forward / backward (tank right side) |
| **Either stick X** | Strafe left / right using all wheels |

Push both sticks forward = drive forward.
Push sticks in opposite directions = spin in place.
Push either stick sideways = strafe.

### Triggers - Precision Speed

| Control | Action |
|---------|--------|
| **Right trigger** | Drive forward (analog - more pull = faster) |
| **Left trigger** | Drive backward (analog) |

Triggers override sticks when pressed. Great for smooth, controlled approach.

### Bumpers - Quick Turns

| Control | Action |
|---------|--------|
| **Right bumper** | Turn right in place |
| **Left bumper** | Turn left in place |

### D-Pad - Arm Sequences (One-Press Macros)

| Control | Action |
|---------|--------|
| **D-pad Up** | **Front pickup** - reach down, grab block, lift |
| **D-pad Down** | **Backward drop** - fold arm back, release into rear bin |
| **D-pad Left** | **Left side pickup** - rotate arm left, grab, lift |
| **D-pad Right** | **Right side pickup** - rotate arm right, grab, lift |

Warning: These are full sequences (2-4 seconds each). Motors stop automatically during arm movement. Keep people clear of the arm.

**Workshop challenge workflow:**
1. Drive to block, then press **D-pad Up** to grab it.
2. With block in gripper, press **D-pad Down** to drop into rear bin.
3. Repeat until bin is full
4. Drive to basket, then dump bin manually or push blocks in.

**Side pickups** let you grab blocks that aren't directly in front - useful when you cannot line up perfectly.

### Face Buttons - Arm Expressions

| Button | Action |
|--------|--------|
| **A** | Look forward (reset arm to default pose) |
| **B** | Look sad (arm droops for demos) |
| **Y** | Nod yes (arm bobs up/down) |
| **X** | Shake no (arm swings side to side) |

### Safety

| Button | Action |
|--------|--------|
| **Back** | EMERGENCY STOP (all motors off) |
| **Start** | Quit program |

**Always keep a thumb near the Back button!**

---

## Implementation Guide

### How It Works

```python
# Main loop (simplified):
while running:
    # Read gamepad state
    left_y = gamepad.get_axis(1)   # Left stick Y
    right_y = gamepad.get_axis(4)  # Right stick Y
    left_x = gamepad.get_axis(0)   # Left stick X
    right_x = gamepad.get_axis(3)  # Right stick X

    # Apply deadzone (ignore tiny stick drift)
    if abs(left_y) < 0.15: left_y = 0

    # Y sticks control left/right sides; either X stick strafes all wheels.
    if left_x and right_x:
        strafe = (left_x + right_x) / 2
    else:
        strafe = left_x or right_x

    fl = -left_y + strafe     # Front left
    rl = -left_y - strafe     # Rear left
    fr = -right_y - strafe    # Front right
    rr = -right_y + strafe    # Rear right

    # Scale to motor range and send
    board.set_motor_duty([(1, fl*50), (2, fr*50), (3, rl*50), (4, rr*50)])
```

### Tuning

At the top of `gamepad_drive.py`:
```python
MAX_SPEED = 50        # Maximum motor duty cycle (0-100)
TURN_SPEED = 40       # In-place turn speed
DEADZONE = 0.15       # Ignore stick values below this
```

- **Reduce MAX_SPEED** for beginners (30 = gentle, 80 = fast)
- **Increase DEADZONE** if robot creeps when sticks are centered
- **Reduce TURN_SPEED** if spins are too aggressive

---

## Configuration

```yaml
gamepad:
  max_speed: 50        # Motor duty cycle limit
  turn_speed: 40       # In-place turn speed
  deadzone: 0.15       # Stick deadzone
  mode: "xinput"       # X mode on back of controller
```

---

## Troubleshooting

**"No gamepad detected":**
- USB receiver plugged into robot Pi (not Pi 500)?
- Gamepad powered on (green LED)?
- Back switch set to **X** (not D)?
- Try: `lsusb | grep -i logitech`
- Try: `ls /dev/input/js*` (should show js0)
- The script will beep and retry until the gamepad is detected.

**robot drives wrong direction:**
- Sticks inverted? Adjust axis mapping in code
- Motors wired backward? Swap motor plugs or invert in code

**robot creeps when sticks centered:**
- Increase DEADZONE (0.15 to 0.20)
- Recalibrate: `sudo jscal /dev/input/js0`

**Laggy response:**
- WiFi interference? Move closer to router
- CPU overloaded? Close other programs on robot

---

## Files

- `SKILL.md` - this file
- `gamepad_drive.py` - main gamepad control script
- `config.yaml` - tuning parameters
- `README.md` - quick reference

---

*Grab the controller and drive!*
