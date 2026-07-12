# robot connection reference

**Phase 1 support: Assemble**

Use this page after [C3: Connect and Test](../setup/C3_CONNECT_AND_TEST.md), or anytime a team needs help with terminals, copying files, editing code, or connection troubleshooting.

This page is reference material. It is not part of the required Phase 1 hardware test sequence.

## Working with Two Terminals

You'll often want multiple SSH sessions:

**Terminal 1:** Running a script on the robot
**Terminal 2:** Monitoring or editing

Open a new terminal tab on your Pi 500 (`Ctrl+Shift+T`) and SSH again:

```bash
ssh robot@<ROBOT_IP>
```

## Copying Files

**Pi 500 to robot:**

```bash
# From Pi 500 terminal (not SSH'd into robot)
ssh robot@<ROBOT_IP> "mkdir -p /home/robot/team_code"
scp ~/Pathfinder2026/my_script.py robot@<ROBOT_IP>:/home/robot/team_code/
```

**robot to Pi 500:**

```bash
# From Pi 500 terminal
scp robot@<ROBOT_IP>:/home/robot/pathfinder/test_frame.jpg ~/
```

## Editing Code

Recommended workflow: keep `/home/robot/pathfinder` as the official updateable repo, and edit starter files in `/home/robot/team_code`. See [Team code workflow](TEAM_CODE_WORKFLOW.md).

### Option A: VS Code + Remote SSH

1. Open VS Code on Pi 500.
2. `Ctrl+Shift+P` -> "Remote-SSH: Connect to Host" -> `robot@<ROBOT_IP>`.
3. If you set up the SSH key in [C3: Connect and Test](../setup/C3_CONNECT_AND_TEST.md), VS Code should connect without asking for the robot password. If not, enter the robot password when prompted.
4. Wait for VS Code to install its server component on the robot. This happens automatically the first time and may take about a minute.
5. Open folder: `/home/robot/team_code`.
6. You should see `README.md`, `drive_practice.py`, and `arm_practice.py`.
7. Open VS Code's built-in terminal: `Terminal` -> `New Terminal`.
8. Run a starter file:

   ```bash
   cd /home/robot/team_code
   python3 drive_practice.py
   ```

9. Open `drive_practice.py`, change one small value such as `MOVE_SECONDS`, save the file, and run it again.
10. Try the arm starter file:

    ```bash
    python3 arm_practice.py
    ```

See [C1: Pi 500 Setup](../setup/C1_PI500_SETUP.md) for VS Code install and extension checks.

If `/home/robot/team_code` is missing, open a robot terminal and run:

```bash
mkdir -p /home/robot/team_code
cp -a /home/robot/pathfinder/team_code_starters/. /home/robot/team_code/
```

### Option B: Edit on Pi 500, Copy to robot

```bash
# On Pi 500
nano ~/Pathfinder2026/skills/my_script.py

# Then copy to the team folder on the robot
ssh robot@<ROBOT_IP> "mkdir -p /home/robot/team_code"
scp ~/Pathfinder2026/skills/my_script.py robot@<ROBOT_IP>:/home/robot/team_code/
```

### Option C: Edit Directly on robot via SSH Terminal

```bash
# While SSH'd into robot
mkdir -p /home/robot/team_code
nano /home/robot/team_code/my_script.py
```

## Troubleshooting

For a shorter student checklist, see [Student troubleshooting](TROUBLESHOOTING.md).

**Connection refused:**

- Is the robot powered on?
- Are both devices on the same WiFi?
- Check robot IP: `ping <ROBOT_IP>`.
- Compare with another team before changing settings.

**Cannot connect to the robot IP:**

- Confirm you are using the robot IP, not the Pi 500 IP.
- Confirm the Pi 500 and robot are on the same workshop network.
- Compare with another team that can connect.
- Repeat [C2: robot Pi WiFi Setup](../setup/C2_ROBOT_PI_WIFI_SETUP.md) on the robot Pi if it still fails.
- If the robot was rebooted or moved to another network, its IP may have changed.
- Try: `ping <ROBOT_IP>` from the Pi 500.

**Permission denied:**

- Wrong password? Compare with another team, then ask facilitator.
- Username must be `robot` (lowercase).

**robot not responding to commands:**

- Battery dead? Check voltage.
- SSH session frozen? Close terminal, reconnect.

**robot does not move:**

- Check battery: `python3 scripts/tools/check_battery.py`.
- Re-check motor wiring against [B1: robot Assembly Guide](../workshop/B1_ROBOT_ASSEMBLY_GUIDE.md).
- Try a higher motor power with fresh batteries.
- Confirm the robot is on the floor, not lifted by a cable or stand.

**Arm or sonar check fails:**

- Re-check assembly wiring against [B1: robot Assembly Guide](../workshop/B1_ROBOT_ASSEMBLY_GUIDE.md).
- Confirm the correct cable is connected before changing code.

**Camera not working:**

- Run `ls /dev/video*` on the robot.
- If there is no `video0`, unplug and replug the USB camera.
- Try `python3 skills/camera_vision/test_camera.py`.

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

# Start camera-only web feed on the robot
python3 web/camera_view.py

# Then view camera from the Pi 500 browser
# Open browser: http://<ROBOT_IP>:8080
```

Need the latest code on the robot? Use [Update robot code](UPDATE_ROBOT_CODE.md).

## Next

- For safe team edits, use [Team code workflow](TEAM_CODE_WORKFLOW.md).
- For capability demos, continue to [Phase 2: Capabilities Exploration](../workshop/CAPABILITIES_EXPLORATION.md).
