# Skill: Line Following

**Difficulty:** Advanced - Vision + Drive Integration
**Type:** Closed-Loop Path Tracking
**Prerequisites:** Mecanum Drive, camera hardware checked in Connect And Test
**Estimated Time:** 25-30 minutes

---

> **Note — Raw API for learning:** The code examples in this guide use the low-level hardware API directly (`board.set_motor_duty()`, etc.) so you can see exactly what's happening inside the robot. Your **starter templates** use the `robot` class which wraps all of this — same concepts, cleaner code.

## Overview

### What This Skill Does

Follow a **lime green tape line** on the floor using camera feedback. The camera sees the line, calculates its position relative to the robot's center, strafes to stay on top of the line, and adds small turn corrections for curves. This is **closed-loop path following** - the same concept self-driving cars use.

**What you'll learn:**
- Line detection using HSV color filtering
- Centroid calculation (where is the line?)
- Proportional strafe and turn control
- Thin camera scan strips for focused detection
- End-of-line detection (when to stop)
- Intersection handling (optional: which way to turn)

### Real-World Applications

- **Warehouse robots:** Follow painted floor lines between stations
- **Factory AGVs:** Automated Guided Vehicles follow magnetic/optical lines
- **Self-driving cars:** Lane detection and keeping
- **Agricultural robots:** Follow crop rows
- **Hospital delivery:** Robots follow floor paths between departments

### How It Works

```
Camera Frame (pointed down)
    |
    v
Sample far, middle, and near scan strips
    |
    v
Convert to HSV
    |
    v
Threshold for lime green (create binary mask)
    |
    v
Find the largest connected line region in each strip
    |
    v
Calculate lateral error and rough line angle
    |
    v
Proportional control (strafe to center, turn for curve)
    |
    v
Mecanum drive (forward + strafe + turn correction)
```

### Why Lime Green?

| Color | HSV Hue | Conflict Risk | Floor Contrast |
|-------|---------|---------------|----------------|
| Red tape | 0-10 | Overlaps red blocks! | Good |
| Orange tape | 5-15 | Overlaps red blocks! | Good |
| Blue tape | 100-130 | Overlaps blue blocks! | Good |
| **Lime green** | **45-65** | **None!** | **Excellent** |

Lime green has maximum HSV separation from all three block colors (red, blue, yellow) AND high contrast against a gray floor.

---

## Quick Start

### Step 1: Test Line Detection

```bash
cd /home/robot/pathfinder/skills/line_following
python3 test_line_detect.py
```

**What happens:**
1. Camera captures frame (pointed down)
2. Detects lime green pixels
3. Calculates line centroid
4. Reports position (left/center/right)
5. Saves annotated image

**Before running:**
- Lay lime green tape on the floor in a line or curve
- Position robot so camera can see the tape
- Arm should be in "camera down" position

### Step 2: Run Line Following Demo

```bash
cd /home/robot/pathfinder/skills/line_following
python3 run_demo.py
```

**What happens:**
1. Camera points down (arm repositioned)
2. Detects lime green line
3. robot drives forward, strafing to stay centered over the line
4. Stops when line ends or timeout

**SAFETY:** robot will drive! Clear the path and be ready with Ctrl+C.

### Step 3: Tuning

If robot oscillates (wobbles back and forth):
- Decrease `K_STRAFE` in `line_follower.py`
- Decrease `K_TURN` in `line_follower.py`

If robot loses the line on curves:
- Increase `K_TURN`
- Decrease `FORWARD_SPEED` (slower = more time to react)

---

## Implementation Guide (For Coders)

### Level 2: Use LineFollower Class

```python
from skills.line_following.line_follower import LineFollower

follower = LineFollower()

# Follow until line ends or timeout
result = follower.follow(timeout=30)

if result['success']:
    print('Reached end of line!')
else:
    print('Stopped: %s' % result['reason'])

follower.cleanup()
```

### Level 3: Understand Line Detection

**Step 1: Capture three scan strips**
```python
ret, frame = camera.read()

# Look far ahead, midway ahead, and close to the robot
far = frame[240:280, :]
mid = frame[340:380, :]
near = frame[420:465, :]
```

**Why use thin strips?**
- Near tape is most important for centering
- Far tape helps estimate the curve direction
- Fewer pixels to process means faster detection
- Reduces false positives from distant objects

**Step 2: HSV threshold for lime green**
```python
hsv = cv2.cvtColor(near, cv2.COLOR_BGR2HSV)

# Lime green tape
lower_green = np.array([35, 50, 50])
upper_green = np.array([85, 255, 255])
mask = cv2.inRange(hsv, lower_green, upper_green)

# Clean up noise
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
```

**Step 3: Find centroid (center of mass)**
```python
# Moments give us the centroid
M = cv2.moments(mask)

if M['m00'] > 0:  # m00 = total white pixel area
    cx = int(M['m10'] / M['m00'])  # X centroid
    cy = int(M['m01'] / M['m00'])  # Y centroid
    line_found = True
else:
    line_found = False  # No green pixels = no line
```

**Step 4: Calculate centering and heading error**
```python
frame_center = 320  # 640 / 2

if line_found:
    error = cx - frame_center  # Positive = line is right
    # error = -200 -> line far left, strafe left
    # error = 0    -> line centered, go straight
    # error = +200 -> line far right, strafe right
```

**Step 5: Proportional control**
```python
K_STRAFE = 0.22  # Sideways correction gain
K_TURN = 0.08    # Heading correction gain
forward_speed = 38  # Base forward speed

if abs(error) > 10:
    strafe = error * K_STRAFE
    if abs(strafe) < 18:
        strafe = 18 if strafe > 0 else -18
else:
    strafe = 0
turn = heading_error * K_TURN

# Mecanum: forward + sideways correction + small turn correction
fl = int(forward_speed + strafe + turn)
fr = int(forward_speed - strafe - turn)
rl = int(forward_speed - strafe + turn)
rr = int(forward_speed + strafe - turn)

board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])
```

### Level 3: End-of-Line Detection

**How to know when the line ends:**
```python
contours = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
line_found = any(cv2.contourArea(c) >= 25 for c in contours)

if not line_found:
    consecutive_lost += 1
    stop()  # Do not continue driving while the line is missing
    if consecutive_lost >= 3:
        stop()
        return 'line_ended'
else:
    consecutive_lost = 0
```

### Level 4: Advanced Line Following

**Multiple scan lines (better for curves):**
```python
# Instead of one centroid, scan at three tested heights
far_row = frame[240:280, :]
mid_row = frame[340:380, :]
near_row = frame[420:465, :]

# Calculate centroid for each strip
near_cx = find_centroid(near_row, mask)
mid_cx = find_centroid(mid_row, mask)
far_cx = find_centroid(far_row, mask)

# Center from the closest visible strip; use far for curve direction
error = near_cx - frame_center
heading_error = far_cx - near_cx
```

**Intersection detection:**
```python
# If green area suddenly doubles, might be an intersection
if green_ratio > INTERSECTION_THRESHOLD:
    # Multiple line segments detected
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        print('Intersection detected!')
        # Decision: go left, right, or straight
```

---

## Engineering Deep Dive (Advanced)

### Proportional Control

**Centering correction:**
```
strafe = K_STRAFE * error

Positive error means the line is right of center, so the robot strafes right.
```

**Heading correction:**
```
turn = K_TURN * heading_error

Positive heading error means the line trends right ahead, so the robot turns right a little.
```

This keeps the robot physically over the tape instead of swinging wide around it.

### Scan Line Analysis

**Why bottom of frame is most important:**
```
Frame top:     Far away    -> Curve information
Frame middle:  Medium      -> Where robot will be soon
Frame bottom:  Close       -> Where robot IS right now

For centering: React to what's close (bottom)
For planning: Look ahead (top) to anticipate curves
```

**Scan-strip jobs:**
- Near: Immediate lateral centering
- Mid: Backup center when the near strip cannot see the line
- Far: Initial line acquisition and curve anticipation

### Lighting Robustness

**Problem:** Indoor lighting varies (fluorescent flicker, shadows, windows)

**HSV advantage:** Hue channel is relatively stable under lighting changes

**Additional robustness:**
```python
# Adaptive thresholding: adjust V range based on frame brightness
avg_brightness = np.mean(frame[:,:,2])  # V channel average

if avg_brightness < 80:  # Dark
    v_min = 60
elif avg_brightness > 200:  # Very bright
    v_min = 150
else:
    v_min = 100  # Normal
```

### Tape vs Painted Lines

**Tape:**
- Consistent color (manufactured)
- Raised surface (shadows at edges)
- Can peel (temporary)
- Easy to reposition

**Paint:**
- May vary in thickness/color
- Flat (no shadow edges)
- Permanent
- Cheaper for large areas

**For workshops: Tape is ideal** (reusable, repositionable, consistent color)

### Speed vs Accuracy Tradeoff

```
Slow (speed=15):
  + Smooth following
  + Handles tight curves
  + More time to process
  - Boring to watch
  - Slow challenge time

Fast (speed=40):
  + Exciting to watch
  + Fast challenge time
  - Overshoots curves
  - May lose line
  - Needs higher turn gain

Sweet spot: speed=38, strafe gain=0.22, turn gain=0.08, minimum strafe=18 (tune from here)
```

---

## Configuration

The current code does not load `config.yaml`. Tune the named constants in `line_follower.py`.

---

## Files

```
line_following/
  SKILL.md              # This file
  run_demo.py           # Follow the line (with safety)
  test_line_detect.py   # Test detection only (no driving)
  line_follower.py      # LineFollower class
  config.yaml           # Reference values; not loaded by the current code
  README.md             # Quick reference
```

---

*Follow the line, stay on track!*
