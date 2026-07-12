# Skill: Robotic Arm Control

**Difficulty:** Intermediate - Hardware Manipulation
**Type:** Servo Control & Manipulation
**Prerequisites:** D1 (Mecanum Drive recommended)
**Estimated Time:** 25-30 minutes

---

> **Note - Raw API for learning:** The code examples in this guide use the low-level hardware API directly (`get_board()`, `board.set_servo_position()`, etc.) so you can see exactly what's happening inside the robot. Your **starter templates** use the `robot` class which wraps all of this - same concepts, cleaner code.

##  Overview

### What This Skill Does

Learn to control a **5-servo robotic arm** to position, grab, and manipulate objects. Progress from visual sliders to programming pick-and-place sequences.

**What you'll learn:**
- Servo control (PWM pulse width, 500-2500 range)
- Degrees of freedom (DOF) - what each joint does
- Pre-recorded sequences (action groups like "macros")
- Named positions (quick positioning)
- Inverse kinematics basics (XYZ coordinates to joint angles)
- Pick-and-place programming

### Real-World Applications

**In Industry:**
- **Assembly lines:** Pick parts, insert into products
- **Warehouses:** Box sorting, palletizing
- **Food service:** Robotic kitchens, burger flippers
- **Surgery:** Da Vinci surgical robots (teleoperated arms)
- **Manufacturing:** Welding, painting, material handling

**In Research:**
- Prosthetic arms (human-robot interfaces)
- Space robotics (ISS Canadarm, Mars rovers)
- Bomb disposal (EOD robots)
- Underwater exploration (ROV manipulators)

### Why Robotic Arms?

**Advantages:**
- Precise positioning (mm accuracy)
- Repeatable (exact same motion every time)
- Tireless (24/7 operation, no fatigue)
- Flexible (reprogram for different tasks)

**Limitations:**
- Reachability (limited workspace, can't reach everywhere)
- Payload (limited lifting capacity, ~200g for this arm)
- Complexity (5+ servos, coordination required)
- Cost (more servos = more expensive)

---

##  Quick Start

### Step 1: Understand the Hardware

**Your arm has 5 servos:**
1. **Servo 1:** Gripper/Claw (1550=closed, 2500=open)
2. **Servo 3:** Wrist (rotation up/down)
3. **Servo 4:** Elbow (bend joint)
4. **Servo 5:** Shoulder (raise/lower arm)
5. **Servo 6:** Base (rotate left/right)

*Note: Servo 2 doesn't exist on this arm*

**Degrees of Freedom:** 4-DOF (base, shoulder, elbow, wrist) + gripper

**Coordinate system:**
- **X-axis:** Left (-) to Right (+)
- **Y-axis:** Forward (away from base)
- **Z-axis:** Up (height above ground)

### Step 2A: Web UI (Visual, No Coding)

**Start the web server:**
```bash
cd /home/robot/pathfinder
python3 web/web_control.py
```

**Open in browser:**
```
http://<ROBOT_IP>:8080
```

**What you'll see:**
- 5 sliders (one per servo)
- Real-time position values
- Preset buttons (Rest, Camera Forward)

**Try this:**
1. Move Servo 6 (Base) slider - arm rotates
2. Move Servo 5 (Shoulder) slider - arm raises/lowers
3. Move Servo 4 (Elbow) slider - arm extends/retracts
4. Move Servo 1 (Gripper) slider - claw opens/closes
5. Click "Rest Position" button - arm moves to safe pose

**Success = You understand what each servo does!**

### Step 2B: Action Groups (Pre-Recorded Sequences)

**Play a pre-recorded sequence:**
```bash
cd /home/robot/pathfinder/skills/robotic_arm
python3 play_action.py shake_head
```

**What happens:**
- Arm plays back recorded "shake head" gesture
- Multiple servos move in coordinated sequence
- Like playing a video recording

**Available action groups:**
- `stand` - Neutral standing position
- `shake_head` - Head shake gesture
- `wave` - Waving motion (if available)

**Try making one:**
1. Use web UI to position arm (frame 1)
2. Write down servo positions
3. Move arm to next position (frame 2)
4. Write down positions again
5. (Advanced: use recording tool to save as `.d6a` file)

**Success = You played an action group and understand they're pre-recorded sequences!**

### Step 3: Block Pickup Demo (Python)

**No web browser needed - pure Python:**
```bash
cd /home/robot/pathfinder/skills/robotic_arm
python3 run_demo.py
```

**What happens:**
1. Arm moves to the ready position
2. Gripper opens around a block
3. Arm grabs and lifts the block
4. Arm loads the block onto the robot's back

**Success = The arm picks up a block and loads it onto the back without drive motors moving.**

---

##  Implementation Guide (For Coders)

### Level 2: Safe Servo Control (Simple Python)

**Basic positioning:**
```python
from lib.board import get_board

board = get_board()

# Ready position for pickup demo
board.set_servo_position(2000, [
    (1, 1550),  # Gripper closed
    (3, 590),   # Wrist forward
    (4, 2500),  # Elbow forward
    (5, 700),   # Shoulder raised
    (6, 1500),  # Base center
])

# Example pickup actions
board.set_servo_position(1000, [(5, 1818)])  # Lower shoulder
board.set_servo_position(500, [(1, 2500)])
board.set_servo_position(300, [(1, 1550)])   # Close gripper
```

Use only positions that have been tested on the event robot. Do not add new reach, pickup, or carry positions to the workshop path until they are mechanically verified.

### Level 1.5: Action Groups (Pre-Recorded)

**Play back sequences:**
```python
from sdk.common.action_group_control import ActionGroupController

controller = ActionGroupController(board._board)

# Play action groups
controller.runAction('stand')      # Neutral pose
controller.runAction('shake_head') # Gesture
controller.runAction('wave')       # Wave motion
```

**When to use:**
- Complex gestures (wave, dance, nod)
- Demonstrations (showing capability)
- Exact repeatability (calibration sequences)

**When NOT to use:**
- Vision-guided tasks (can't adapt to object position)
- Variable targets (blocks at unknown locations)

### Level 3: XYZ Coordinates (Inverse Kinematics)

**Position gripper in 3D space:**
```python
# Move to specific coordinates (millimeters)
arm.move_to(x=50, y=200, z=80)  # 50mm right, 200mm forward, 80mm high

# Example: Reach for object
arm.move_to(0, 180, 30)   # Approach object
arm.close_gripper()        # Grab it
arm.move_to(0, 180, 100)  # Lift up
arm.move_to(80, 180, 100) # Move to place location
arm.open_gripper()         # Release
```

**Coordinate examples:**
```python
# Center, forward, low
arm.move_to(0, 200, 20)

# Right side
arm.move_to(50, 150, 80)

# Left side
arm.move_to(-50, 150, 80)

# High reach
arm.move_to(0, 120, 180)
```

**Reachability:**
- Not all XYZ positions are possible (arm too short, joint limits)
- IK solver returns `False` if unreachable
- Typical workspace: X=plus/minus 100mm, Y=50-250mm, Z=10-200mm

### Level 4: Pick-and-Place Sequence

**Complete autonomous pickup:**
```python
def pick_and_place(pickup_xyz, place_xyz, approach_height=50):
    """
    Pick object and place it elsewhere.

    Args:
        pickup_xyz: (x, y, z) tuple for pickup location
        place_xyz: (x, y, z) for place location
        approach_height: mm above object to approach from
    """
    x_pickup, y_pickup, z_pickup = pickup_xyz
    x_place, y_place, z_place = place_xyz

    # 1. Approach pickup from above
    arm.move_to(x_pickup, y_pickup, z_pickup + approach_height)
    arm.open_gripper()

    # 2. Descend to object
    arm.move_to(x_pickup, y_pickup, z_pickup)

    # 3. Grab
    arm.close_gripper()
    time.sleep(0.5)  # Wait for grip

    # 4. Lift
    arm.move_to(x_pickup, y_pickup, z_pickup + approach_height)

    # 5. Move to place location (high)
    arm.move_to(x_place, y_place, z_place + approach_height)

    # 6. Descend
    arm.move_to(x_place, y_place, z_place)

    # 7. Release
    arm.open_gripper()
    time.sleep(0.3)

    # 8. Withdraw
    arm.move_to(x_place, y_place, z_place + approach_height)

# Use it:
pick_and_place((0, 200, 30), (80, 180, 30))
```

---

##  Engineering Deep Dive (Advanced)

### Servo Control Theory

**PWM (Pulse Width Modulation):**
- Servos receive 50 Hz signal (20ms period)
- Pulse width: 500 microseconds to 2500 microseconds
- Pulse width = angle
- 1500 microseconds = center (90 degrees)
- 500 microseconds = 0 degrees, 2500 microseconds = 180 degrees

**Our mapping:**
- PWM 500-2500 = about 0-180 degrees (servo dependent)
- Some servos have different ranges (gripper: 1550-2500)

### Forward Kinematics

**Problem:** Given joint angles, where is gripper?

**DH parameters** (Denavit-Hartenberg):
```
Link lengths (approximate):
  Base to shoulder: 60mm
  Shoulder to elbow: 100mm
  Elbow to wrist: 100mm
  Wrist to gripper: 80mm
```

**Forward kinematics equations:**
```python
def forward_kinematics(theta_base, theta_shoulder, theta_elbow, theta_wrist):
    """
    Calculate gripper position from joint angles.
    Returns: (x, y, z) in mm
    """
    # Simplified 2D case (ignoring wrist for now):
    x = cos(theta_base) * (L2*cos(theta_shoulder) + L3*cos(theta_shoulder + theta_elbow))
    y = sin(theta_base) * (L2*cos(theta_shoulder) + L3*cos(theta_shoulder + theta_elbow))
    z = L1 + L2*sin(theta_shoulder) + L3*sin(theta_shoulder + theta_elbow)
    return (x, y, z)
```

### Inverse Kinematics

**Problem:** Given desired (x, y, z), what joint angles?

**Harder than forward!** (no unique solution, or no solution at all)

**Approaches:**
1. **Analytical** (solve equations) - fast, exact
2. **Numerical** (iterative search) - flexible, slower
3. **Jacobian** (gradient descent) - smooth, local

**Our implementation uses:** Analytical for 2D plane + search for pitch angle

**Singularities:**
- Positions where IK fails (arm fully extended, folded on itself)
- Multiple solutions (elbow-up vs elbow-down)
- Unreachable workspace (too far, too close, below base)

### Workspace Analysis

**Reachable volume:**
```
Maximum reach: ~250mm (all links extended)
Minimum reach: ~50mm (arm folded)

Workspace shape: Toroidal (donut) around base
  - Can't reach directly under base (Z=0)
  - Can't reach infinitely far (limited link length)
```

**Joint limits:**
```
Base: plus/minus 90 degrees (500-2500 PWM)
Shoulder: about 0-180 degrees
Elbow: about 0-180 degrees
Wrist: about 0-180 degrees
```

### Action Group File Format

**SQLite database (`.d6a`):**
```sql
CREATE TABLE ActionGroup (
    id INTEGER PRIMARY KEY,
    duration INTEGER,  -- milliseconds
    servo1 INTEGER,    -- Gripper PWM
    servo3 INTEGER,    -- Wrist PWM
    servo4 INTEGER,    -- Elbow PWM
    servo5 INTEGER,    -- Shoulder PWM
    servo6 INTEGER     -- Base PWM
);
```

**Example sequence:**
```
Frame 1: (1500ms, 2500, 695, 2415, 780, 1500)  -- Start position
Frame 2: (1000ms, 2500, 800, 2200, 900, 1500)  -- Mid-motion
Frame 3: (1200ms, 1550, 590, 2450, 700, 1500)  -- End (gripper closed)
```

**Playback:** Linear interpolation between frames (moves at constant speed)

---

## Files in This Skill

```
robotic_arm/
SKILL.md                # This file
run_demo.py             # Level 2: Block pickup and load demo
play_action.py          # Level 1.5: Action group playback
config.yaml             # Reference values; not loaded by run_demo.py
README.md               # Quick reference
  stand.d6a
  shake_head.d6a
  wave.d6a
```

---

*Learn to control - position, grab, manipulate!*
