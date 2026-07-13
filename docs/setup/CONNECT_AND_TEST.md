# Connect Pi 500 To The robot And Test

**Phase 1: Assemble**

**Purpose:** Establish SSH connection from your Pi 500 to the robot, then verify wiring and core hardware.

This is the critical step — once connected, you control the robot entirely from your Pi 500.

---

## Prerequisites

- Pi 500 is powered on, connected to WiFi ([Pi 500 Setup](PI500_SETUP.md))
- robot is assembled ([robot Assembly Guide](../workshop/ROBOT_ASSEMBLY_GUIDE.md))
- robot Pi is powered on and on the workshop network ([robot Pi WiFi Setup](ROBOT_PI_WIFI_SETUP.md))
- robot is powered on with charged batteries
- Both devices on the same WiFi network
- You have the robot IP address from [robot Pi WiFi Setup](ROBOT_PI_WIFI_SETUP.md)

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

Use the robot IP confirmed in [robot Pi WiFi Setup](ROBOT_PI_WIFI_SETUP.md).

Open a terminal on your Pi 500:

```bash
ssh robot@<ROBOT_IP>
```

- Replace `<ROBOT_IP>` with your robot's actual IP
- Username: `robot`
- Password: `R4spb3rry`
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

If the first battery read is not ready, the script will pause and try again before reporting an error.

If it prints `ERROR: Cannot read battery voltage`, check robot power, battery connection, and the motor board connection before continuing.

**Battery guide:**
| Voltage | Status | Action |
|---------|--------|--------|
| >=8.2V | Excellent | Ready for calibrated movement tests |
| 7.5-8.2V | OK | Normal testing; calibrated turns may vary |
| 7.0-7.5V | Caution | Light testing only; replace soon |
| <7.0V | Low | Replace or charge before motor operation |

## Step 3: Test Individual Motors

This is a hardware wiring and function check. It confirms each motor is plugged into the correct port and that each wheel can move before running any driving patterns.

**Caution:** The robot will move as soon as each motor starts. Put it on the floor, not on a table. Clear at least a 4-foot by 4-foot area. It can drive off a table.

```bash
cd /home/robot/pathfinder
python3 scripts/tools/check_motors.py
```

Expected:

| Motor | Wheel |
|-------|-------|
| 1 | Front left |
| 2 | Front right |
| 3 | Rear left |
| 4 | Rear right |

Each wheel should move when its motor number is tested. If the wrong wheel moves, the motor cables are connected to the wrong port. If a wheel does not move or spins backward during this single-motor test, stop before running drive patterns.

If this test fails, go back to [robot Assembly Guide](../workshop/ROBOT_ASSEMBLY_GUIDE.md) and check the motor wiring photos before changing code.

## Step 4: Test Arm Servos

This is a hardware wiring and function check. It confirms each arm servo is plugged into the correct port and that the gripper, wrist, elbow, shoulder, and base all respond.

Keep hands clear of the arm and gripper.

```bash
cd /home/robot/pathfinder
python3 scripts/tools/check_servos.py
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

If the wrong arm joint moves, or a servo does not move, go back to [robot Assembly Guide](../workshop/ROBOT_ASSEMBLY_GUIDE.md) and check the arm and servo wiring before changing code.

## Step 5: Test Sonar

This is a hardware wiring and function check. It confirms the ultrasonic sensor is connected, powered, and reading distance.

```bash
cd /home/robot/pathfinder
python3 scripts/tools/check_sonar.py
```

Put your hand in front of the robot and run the test again. The distance should change.

If you see `no reading`, check that I2C is enabled, the sonar cable is connected, and `sudo i2cdetect -y 1` shows address `77`.

If the sonar check fails, go back to [robot Assembly Guide](../workshop/ROBOT_ASSEMBLY_GUIDE.md) and check the sonar mounting and wiring before changing code.

## Step 6: Test Camera Hardware

```bash
cd /home/robot/pathfinder
python3 skills/camera_vision/test_camera.py
```

This is a snapshot test. It should report `Camera: 640x480` and save a test image.

To view the live camera feed, start the camera-only web viewer on the robot:

```bash
python3 web/camera_view.py
```

Leave that terminal running. It should print:

```text
Open in browser: http://<ROBOT_IP>:8080
```

Then, from the Pi 500 browser, open:

```
http://<ROBOT_IP>:8080
```

Replace `<ROBOT_IP>` with your robot's IP. This page is only for viewing the camera. It does not include robot movement controls.

If the page does not load, make sure the camera viewer is still running on the robot and that the Pi 500 and robot are on the same WiFi network.

---

## Phase 1 Required Tests Complete

After Step 6, the robot connection and hardware checks are complete. Phase 1 is complete.

Next:

- [Phase 2: Capabilities Exploration](../workshop/CAPABILITIES_EXPLORATION.md)
- [robot connection reference](../support/ROBOT_CONNECTION_REFERENCE.md) for terminals, copying files, editing code, and connection troubleshooting
