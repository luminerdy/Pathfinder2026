# Configuration Guide

**Phase 2 support: Capabilities Exploration**

Use this guide when you want to tune robot behavior without rewriting code.

## Basic Rule

Change one setting at a time, test it, and write down what happened.

Before asking a facilitator, check:

1. Your team's notes.
2. The troubleshooting page.
3. Another team that has the same part working.

Ask a facilitator right away for battery wiring, motor wiring, servo wiring, smoke, heat, broken parts, or commands that require `sudo`.

## Safe For Teams To Edit

These files are intended for workshop tuning:

| File | What To Tune |
|------|--------------|
| `skills/mecanum_drive/config.yaml` | Demo speed, rotation time, square timing, motor direction notes |
| `skills/block_detection/config.yaml` | HSV color ranges, minimum block area, detection confidence |
| `skills/line_following/config.yaml` | Line color range, forward speed, steering gain |
| `skills/sonar_sensors/config.yaml` | Sonar thresholds and demo behavior |
| `skills/camera_vision/config.yaml` | Camera demo settings |
| `skills/robotic_arm/config.yaml` | Arm demo positions if a facilitator has verified the pose is safe |

Use the skill README before editing a config:

```bash
cd /home/robot/pathfinder
cat skills/mecanum_drive/README.md
```

## Facilitator-Only Or Advanced

Do not edit these during normal team work unless a facilitator tells you to:

| File | Why |
|------|-----|
| `config.yaml` | Older global configuration; not every active skill reads it |
| `lab_config.yaml` | Shared color calibration reference |
| `Deviation.yaml` | Servo calibration offsets |
| `lib/battery.py` | Shared voltage thresholds used by robot code |
| Files in `lib/` | Hardware control layer |
| Files in `lib/` | Lower-level board communication |

If a team wants to experiment with advanced code, copy the file into `/home/robot/team_code` first.

## Common Tuning Tasks

### Drive Demo Too Fast Or Too Slow

Edit:

```text
skills/mecanum_drive/config.yaml
```

Useful fields:

- `speeds.max`
- `speeds.rotation`
- `demo.duration`
- `demo.rotation_time`

If turns do not complete, try a slightly higher rotation speed or longer rotation time. Record battery voltage before comparing tests.

### Block Detection Misses Blocks

Edit:

```text
skills/block_detection/config.yaml
```

Useful fields:

- `colors`
- `detection.min_area`
- `detection.min_confidence`

If the robot misses a real block, widen the HSV range slightly or reduce `min_area`.

If the robot detects the floor or shadows, narrow the HSV range or increase `min_area`.

### Line Following Wobbles

Edit:

```text
skills/line_following/config.yaml
```

Useful fields:

- `control.Kp`
- `control.forward_speed`
- `control.max_steer`
- `roi.top_ratio`

If the robot wobbles, lower `Kp` or slow down.

If it misses curves, slow down or adjust the region of interest to see farther ahead.

### Arm Position Looks Unsafe

Stop the demo with `Ctrl+C`.

Do not guess new arm positions quickly. Compare with another working team and ask a facilitator before saving a pose that moves near the table, chassis, camera, or gripper limits.

## How To Test A Change

1. Copy the file to team code if you are experimenting:
   ```bash
   mkdir -p /home/robot/team_code
   cp skills/mecanum_drive/config.yaml /home/robot/team_code/mecanum_config_test.yaml
   ```
2. Make one change.
3. Run the matching demo.
4. Record:
   - File changed
   - Setting changed
   - Old value
   - New value
   - Battery voltage
   - What happened

Good tuning notes make it easier for another team to help.
