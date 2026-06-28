# C3: Connect Pi 500 to the robot and test

**Purpose:** Establish SSH connection from your Pi 500 to the robot, verify all hardware works

This is the critical step — once connected, you control the robot entirely from your Pi 500.

---

## Prerequisites

- Pi 500 is powered on, connected to WiFi ([C1](C1_PI500_SETUP.md))
- robot is assembled ([B1](../workshop/B1_ROBOT_ASSEMBLY_GUIDE.md))
- robot Pi is powered on and on the workshop network ([C2](C2_ROBOT_PI_WIFI_SETUP.md))
- robot is powered on with charged batteries (>7.0V)
- Both devices on the same WiFi network
- You have the robot IP address from [C2](C2_ROBOT_PI_WIFI_SETUP.md)

## Architecture

```
┌──────────────────┐     WiFi/SSH      ┌──────────────────┐
│    Pi 500         │ ──────────────── │    robot (Pi 4)   │
│  (Control Hub)    │                   │  (Mobile Platform)│
│                   │                   │                   │
│  - Write code     │   SSH commands    │  - Motors         │
│  - Run scripts    │ ───────────────► │  - Arm/servos     │
│  - Monitor        │                   │  - Camera         │
│  - Debug          │   Camera feed     │  - Sonar          │
│  - Strategize     │ ◄─────────────── │  - Batteries      │
└──────────────────┘                   └──────────────────┘
     Your desk                              On the floor
```

**You sit at the Pi 500. The robot moves on the field. Everything happens over SSH.**

---

## Step 1: SSH Connection

Use the robot IP confirmed in [C2: robot Pi WiFi Setup](C2_ROBOT_PI_WIFI_SETUP.md).

Open a terminal on your Pi 500:

```bash
ssh robot@<ROBOT_IP>
```

- Replace `<ROBOT_IP>` with your robot's actual IP
- Username: `robot`
- Password: (provided by facilitator)
- Type `yes` if asked about fingerprint

**Success looks like:**
```
robot@pathfinder:~ $
```

The prompt changes from the Pi 500 prompt, usually `pi500@pihub:~ $`, to the robot prompt, `robot@pathfinder:~ $`.

You're now ON the robot. Every command you type runs on the robot.

## Recommended: Set Up A Simple SSH Key

Use the password connection first. After that works, set up an SSH key so this same Pi 500 can connect to the robot without typing the robot password each time.

Open a new terminal on the Pi 500. Do not run these commands while logged into the robot:

```bash
ssh-keygen -t ed25519
ls ~/.ssh/id_ed25519.pub
ssh-copy-id robot@<ROBOT_IP>
```

For `ssh-keygen`, press Enter to accept the default file location. For the event, press Enter again if asked for a passphrase.

If `ssh-copy-id` says `ERROR: No identities found`, the Pi 500 does not have a default public key yet. Run `ssh-keygen -t ed25519` again and accept the default file location. Then check that `~/.ssh/id_ed25519.pub` exists before running `ssh-copy-id`.

After the key is copied, connect the simple way:

```bash
ssh robot@<ROBOT_IP>
```

If the team changes Pi 500s, repeat this key setup from the new Pi 500.

## Step 2: Check Battery

**Do this FIRST every time you connect!**

Run these commands while you are logged into the robot. Your prompt should look like `robot@pathfinder:~ $`.

```bash
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py
```

This should print the platform, battery voltage, status, and note.

If it prints `ERROR: Cannot read battery voltage`, check robot power, battery connection, and the motor board connection before continuing.

**Battery guide:**
| Voltage | Status | Action |
|---------|--------|--------|
| >8.0V | Full | Good to go |
| 7.5-8.0V | OK | Monitor closely |
| 7.0-7.5V | Low | Replace soon |
| <7.0V | Critical | Replace NOW |

## Step 3: Test Individual Motors

This checks motor wiring before running any driving patterns.

**Caution:** The robot will move as soon as each motor starts. Put it on the floor, not on a table. Clear at least a 4-foot by 4-foot area. It can drive off a table.

```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board
import time

board = get_board()
motors = [
    (1, 'front left'),
    (2, 'front right'),
    (3, 'rear left'),
    (4, 'rear right'),
]

for motor_id, name in motors:
    input('Press Enter to test motor %d (%s).' % (motor_id, name))
    print('Motor %d (%s): running forward briefly' % (motor_id, name))
    board.set_motor_duty([(motor_id, 40)])
    time.sleep(0.5)
    board.set_motor_duty([(motor_id, 0)])
    time.sleep(0.5)

board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
print('Motor wiring test complete')
"
```

Expected:

| Motor | Wheel |
|-------|-------|
| 1 | Front left |
| 2 | Front right |
| 3 | Rear left |
| 4 | Rear right |

Each wheel should move when its motor number is tested. If the wrong wheel moves, the motor cables are connected to the wrong port. If a wheel does not move or spins backward during this single-motor test, note it for facilitator review before running drive patterns.

## Step 4: Test Arm Servos

This checks that the arm servos respond separately from the drive motors.

Keep hands clear of the arm and gripper.

```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board
import time

board = get_board()
tests = [
    (1, 'gripper', 2500, 1475, 2500),
    (6, 'base', 1300, 1700, 1500),
    (5, 'shoulder', 700, 1000, 700),
    (4, 'elbow', 2450, 2200, 2450),
    (3, 'wrist', 590, 900, 590),
]

for servo_id, name, pos1, pos2, home in tests:
    input('Press Enter to test servo %d (%s).' % (servo_id, name))
    print('Servo %d (%s): %d -> %d -> %d' % (servo_id, name, pos1, pos2, home))
    board.set_servo_position(700, [(servo_id, pos1)])
    time.sleep(1.0)
    board.set_servo_position(700, [(servo_id, pos2)])
    time.sleep(1.0)
    board.set_servo_position(700, [(servo_id, home)])
    time.sleep(1.0)

print('Servo wiring test complete')
"
```

Expected:

| Servo | Part |
|-------|------|
| 1 | Gripper |
| 3 | Wrist |
| 4 | Elbow |
| 5 | Shoulder |
| 6 | Base rotation |

Servo 2 is not used on this robot.

If a drive motor moves during a servo test, stop and ask a facilitator to check the board connection and software image.

## Step 5: Test Sonar

This checks that the ultrasonic sensor is connected and reading distance.

```bash
cd /home/robot/pathfinder
python3 -c "
from lib.sonar import Sonar
import time

s = Sonar()
for i in range(5):
    d = s.get_distance()
    print('Reading %d: %.0f mm' % (i + 1, d) if d is not None else 'Reading %d: no reading' % (i + 1))
    if d is not None:
        s.set_led_by_distance(d)
    time.sleep(0.5)
s.off()
"
```

Put your hand in front of the robot and run the test again. The distance should change.

If you see `no reading`, check that I2C is enabled, the sonar cable is connected, and `sudo i2cdetect -y 1` shows address `77`.

## Step 6: Test Drive Patterns

**Caution:** The robot will move as soon as the demo starts. Put it on the floor, not on a table. Clear at least a 4-foot by 4-foot area so it can move about 2 feet in any direction. It can drive off a table.

```bash
cd /home/robot/pathfinder
python3 skills/mecanum_drive/run_demo.py
```

**Watch the robot!** It should move in 8 patterns: forward, backward, strafe, rotate, diagonals, square.

The rotate and square-pattern turns are tuned to use 40% motor power so the robot can turn reliably around an 8V battery level.

**If motors don't move:**
- Check battery (>7.0V needed)
- Are wheels touching the ground?
- Try higher power scripts

## Step 7: Test Arm Demo

```bash
python3 skills/robotic_arm/run_demo.py
```

The arm should move through several positions and test the gripper.

## Step 8: Test Camera

```bash
python3 skills/camera_vision/test_camera.py
```

This is a snapshot test. It should report `Camera: 640x480` and save a test image.

To view the live camera feed, start the web control server on the robot:

```bash
python3 web/web_control.py
```

Leave that terminal running. It should print:

```text
Open in browser: http://<ROBOT_IP>:8080
```

Then, from the Pi 500 browser, open:

```
http://<ROBOT_IP>:8080
```

Replace `<ROBOT_IP>` with your robot's IP. If the page does not load, make sure the web control server is still running on the robot and that the Pi 500 and robot are on the same WiFi network.

---

## Working with Two Terminals

You'll often want multiple SSH sessions:

**Terminal 1:** Running a script on the robot
**Terminal 2:** Monitoring or editing

Open a new terminal tab on your Pi 500 (Ctrl+Shift+T) and SSH again:
```bash
ssh robot@<ROBOT_IP>
```

## Copying Files

**Pi 500 → robot:**
```bash
# From Pi 500 terminal (NOT SSH'd into robot)
ssh robot@<ROBOT_IP> "mkdir -p /home/robot/team_code"
scp ~/Pathfinder2026/my_script.py robot@<ROBOT_IP>:/home/robot/team_code/
```

**robot → Pi 500:**
```bash
# From Pi 500 terminal
scp robot@<ROBOT_IP>:/home/robot/pathfinder/test_frame.jpg ~/
```

## Editing Code

Recommended workflow: keep `/home/robot/pathfinder` as the official updateable repo, and copy files into `/home/robot/team_code` before students modify them. See [C5: Team code workflow](C5_TEAM_CODE_WORKFLOW.md).

**Option A: VS Code + Remote SSH (Recommended!)**
1. Open VS Code on Pi 500
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host" → `robot@<ROBOT_IP>`
3. If you set up the SSH key above, VS Code should connect without asking for the robot password. If not, enter the robot password when prompted.
4. Wait for VS Code to install its server component on the robot. This happens automatically the first time and may take about a minute.
5. Create the team folder if needed: `mkdir -p /home/robot/team_code`
6. Open folder: `/home/robot/team_code`
7. Copy examples from `/home/robot/pathfinder` into `/home/robot/team_code` before editing.
8. Use VS Code's built-in terminal to run scripts.
(See [C1 Pi 500 Setup](C1_PI500_SETUP.md) for VS Code install)

**Option B: Edit on Pi 500, copy to robot**
```bash
# On Pi 500
nano ~/Pathfinder2026/skills/my_script.py
# Then copy to the team folder on the robot
ssh robot@<ROBOT_IP> "mkdir -p /home/robot/team_code"
scp ~/Pathfinder2026/skills/my_script.py robot@<ROBOT_IP>:/home/robot/team_code/
```

**Option C: Edit directly on robot via SSH terminal**
```bash
# While SSH'd into robot
mkdir -p /home/robot/team_code
nano /home/robot/team_code/my_script.py
```

---

## Troubleshooting

**"Connection refused":**
- Is the robot powered on?
- Are both devices on the same WiFi?
- Check robot IP: `ping <ROBOT_IP>`

**Cannot connect to the robot IP:**
- Confirm you are using the robot IP, not the Pi 500 IP.
- Confirm the Pi 500 and robot are on the same workshop network.
- Ask the facilitator to confirm the robot IP.
- If the robot was rebooted or moved to another network, its IP may have changed.
- Try: `ping <ROBOT_IP>` from the Pi 500.

**"Permission denied":**
- Wrong password? Ask facilitator
- Username must be `robot` (lowercase)

**robot not responding to commands:**
- Battery dead? Check voltage
- SSH session frozen? Close terminal, reconnect

**robot does not move:**
- Check battery: `python3 scripts/tools/check_battery.py`
- Try a higher motor power with fresh batteries.
- Confirm the robot is on the floor, not lifted by a cable or stand.

**Camera not working:**
- Run `ls /dev/video*` on the robot
- If no video0, unplug/replug USB camera
- Try `python3 skills/camera_vision/test_camera.py`

**AprilTags not detected:**
- Use tag36h11 tags.
- Improve lighting.
- Make sure tags are large enough and not glossy.

**Block detection unreliable:**
- Avoid shadows.
- Tune HSV values in `skills/block_detection/config.yaml`.

**Line following loses the line:**
- Use lime green tape.
- Slow down the line-following config.
- Avoid tight curves until the robot is tuned.

---

## Connection Cheat Sheet

```bash
# Connect
ssh robot@<ROBOT_IP>

# Check battery
python3 scripts/tools/check_battery.py

# Emergency stop (if robot is moving unexpectedly)
python3 -c "from lib.board import get_board; b=get_board(); b.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])"

# Copy file to robot
scp file.py robot@<ROBOT_IP>:/home/robot/team_code/

# Start camera web feed on the robot
python3 web/web_control.py

# Then view camera from the Pi 500 browser
# Open browser: http://<ROBOT_IP>:8080
```

Need the latest code on the robot? Use [C4: Update robot code](C4_UPDATE_ROBOT_CODE.md).

---

**You're connected!** Now head to [START_HERE.md](../../START_HERE.md) to begin the workshop skills.
