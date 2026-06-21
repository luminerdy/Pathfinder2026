# Pathfinder2026 Team Start Handout

Use this handout to get your team to the Pathfinder2026 GitHub repo and through the first phase: Assemble.

## Team Roles

For a 3-person team:

| Person | First job |
|--------|-----------|
| 1 | Set up the Pi 500 control hub |
| 2 | Start assembling the robot |
| 3 | Help both tracks and keep the checklist moving |

## Open The GitHub Repo

On the Pi 500, open a browser and go to:

```text
https://github.com/luminerdy/Pathfinder2026
```

Start with:

```text
START_HERE.md
```

## Pi 500 Track

Goal: get the Pi 500 ready as the team's coding and control hub.

1. Connect monitor, mouse, and power.
2. Boot the Pi 500.
3. Connect to workshop WiFi.
4. Open a terminal with `Ctrl+Alt+T`.
5. Confirm internet:
   ```bash
   ping -c 3 google.com
   ```
6. Open the Pathfinder2026 GitHub repo in the browser.
7. Install or verify VS Code and the required extensions:
   - Python
   - Remote - SSH

Detailed guide:

```text
docs/setup/C1_PI500_SETUP.md
```

## robot Assembly Track

Goal: build a robot that is safe to power and test.

1. Unpack robot parts.
2. Assemble the chassis.
3. Install mecanum wheels.
4. Attach arm and gripper.
5. Mount camera and sonar.
6. Install charged batteries.
7. Check that cables cannot touch wheels or arm joints.

Detailed guide:

```text
docs/workshop/ASSEMBLE.md
```

## Meet Back Together

When the Pi 500 is ready and the robot is assembled:

1. Get your assigned robot IP address from the facilitator.
2. Open the connect/test guide:
   ```text
   docs/setup/C2_CONNECT_AND_TEST.md
   ```
3. Connect from the Pi 500 to the robot:
   ```bash
   ssh robot@<ROBOT_IP>
   ```
4. Run battery, camera, arm, and drive checks.

Use only the robot IP for SSH, VS Code Remote SSH, and web controls.
