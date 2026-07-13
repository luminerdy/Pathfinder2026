# 2026 Movement Test Plan

Use this page to record real Pathfinder2026 movement behavior before locking in demo or challenge settings.

## Test Rules

- Test on the same floor surface used for the event.
- Start with charged batteries.
- Record battery voltage before and after each test set.
- Put the robot on the floor with at least a 4-foot by 4-foot clear area.
- Run each test at least three times.
- Change one variable at a time.

## Battery

Before testing:

```bash
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py
```

| Test Set | Start Voltage | End Voltage | Notes |
|----------|---------------|-------------|-------|
| Rotate | | | |
| Forward | | | |
| Strafe | | | |
| Square | | | |

## Rotate 90 Degrees

Goal: find a reliable 90 degree turn for the 2026 robot.

| Power | Time | Trial 1 | Trial 2 | Trial 3 | Notes |
|-------|------|---------|---------|---------|-------|
| 35 | 1.0s | | | | |
| 40 | 1.0s | | | | |
| 40 | 1.2s | | | | |
| 45 | 1.0s | | | | |

Record whether the robot under-turns, over-turns, slips, or stalls.

## Forward Distance

Goal: estimate distance traveled per second at practical powers.

| Power | Time | Trial 1 Distance | Trial 2 Distance | Trial 3 Distance | Average |
|-------|------|------------------|------------------|------------------|---------|
| 30 | 1.0s | | | | |
| 35 | 1.0s | | | | |
| 40 | 1.0s | | | | |
| 40 | 2.0s | | | | |

## Strafe Distance

Goal: estimate sideways travel and drift.

| Direction | Power | Time | Distance | Drift Forward/Back | Notes |
|-----------|-------|------|----------|--------------------|-------|
| Left | 35 | 1.0s | | | |
| Right | 35 | 1.0s | | | |
| Left | 40 | 1.0s | | | |
| Right | 40 | 1.0s | | | |

## Square Pattern

Goal: tune side duration and turn timing together.

| Speed | Side Time | Turn Power | Turn Time | Ending Error | Notes |
|-------|-----------|------------|-----------|--------------|-------|
| 35 | 1.5s | 40 | 1.0s | | |
| 35 | 1.5s | 40 | 1.2s | | |
| 40 | 1.5s | 40 | 1.2s | | |

Ending error means how far the robot is from its starting point after the square.

## Update After Testing

After choosing reliable values, update:

- `skills/mecanum_drive/config.yaml`
- `skills/mecanum_drive/run_demo.py` if the demo has hardcoded timing
- `docs/setup/CONNECT_AND_TEST.md` if participant expectations change
- `lib/movement.py` only after repeatable calibration is confirmed

Keep old test notes. Battery voltage and floor surface explain many differences.
