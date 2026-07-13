# Demo Tuning Guide

**Phase 2 support: Capabilities Exploration**

The recommended demos are tuned by changing named constants in the Python file that the team runs. Their nearby `config.yaml` files are reference material and are not loaded by these demos.

## Basic Rule

Change one value at a time, save the file, run the same demo again, and write down what happened.

Do team experiments in `/home/robot/team_code`. Use [Team code workflow](../support/TEAM_CODE_WORKFLOW.md) before editing.

## Mecanum Drive

File:

```text
skills/mecanum_drive/run_demo.py
```

Find the `TEAM TUNING` section near the top:

| Constant | Effect |
|----------|--------|
| `DRIVE_SPEED` | Forward, backward, and strafe power |
| `DIAGONAL_SPEED` | Diagonal wheel-pair power |
| `TURN_SPEED` | Turning power |
| `SIDE_DURATION_SECONDS` | Length of each square side |
| `TURN_DURATION_SECONDS` | Approximate 90-degree turn time |
| `PATTERN_PAUSE_SECONDS` | Pause between square patterns |

Battery voltage and floor surface affect every movement. Record both when comparing results.

## Sonar Sensors

File:

```text
skills/sonar_sensors/run_demo.py
```

Find the `TEAM TUNING` section near the top:

| Constant | Effect |
|----------|--------|
| `DANGER_DISTANCE_CM` | Stop distance and red zone |
| `CAUTION_DISTANCE_CM` | Yellow-zone boundary |
| `OBSTACLE_DISTANCE_CM` | Distance that triggers avoidance |
| `SAFE_MOVE_SPEED` | Forward speed during the stop test |
| `AVOID_MOVE_SPEED` | Movement power during avoidance |
| `BACKUP_DURATION_SECONDS` | How long the robot backs away |
| `TURN_DURATION_SECONDS` | How long the avoidance turn lasts |

Test with a person ready to press `Ctrl+C`. Keep the robot on the floor in a clear area.

## Robotic Arm

File:

```text
skills/robotic_arm/run_demo.py
```

The tested targets are in `READY_POSITION` and `PICKUP_AND_LOAD_STEPS`.

Arm changes can cause collisions. Change only one servo target at a time, stay within the documented limits, and stop immediately if any movement is not correct. Re-check assembly and wiring before assuming a code value is wrong.

## What Teams Should Not Edit

Do not change these during normal workshop tuning unless a facilitator directs it:

- `Deviation.yaml`
- `lib/battery.py`
- Files in `lib/`
- Servo targets that have not been physically tested

Ask a facilitator immediately for battery or wiring problems, heat, smoke, broken parts, or commands requiring `sudo`.
