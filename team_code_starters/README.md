# Pathfinder Team Code

This folder is your team's safe place to experiment.

The official robot code lives here:

```text
/home/robot/pathfinder
```

Your editable practice code lives here:

```text
/home/robot/team_code
```

Start with these files:

- `drive_practice.py` - try simple robot movement
- `arm_practice.py` - try simple gripper and arm movement
- `camera_practice.py` - take one camera picture

Run a starter file from the robot terminal:

```bash
cd /home/robot/team_code
python3 drive_practice.py
```

In VS Code Remote SSH:

1. Open folder `/home/robot/team_code`.
2. Open `Terminal` -> `New Terminal`.
3. Run:

```bash
python3 drive_practice.py
python3 arm_practice.py
python3 camera_practice.py
```

Change one small thing at a time, save, and run it again.

Good first edits:

- In `drive_practice.py`, change `MOVE_SECONDS = 1.0` to `MOVE_SECONDS = 0.5`.
- In `arm_practice.py`, change only one gripper value at a time.
- In `camera_practice.py`, change `OUTPUT_FILE` to save a different picture name.
