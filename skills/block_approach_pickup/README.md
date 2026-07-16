# Block Approach And Pickup

Experimental combined block automation for Pathfinder2026.

This is not part of the event participant flow yet. It is for calibration work
only.

## What It Does

1. Finds one selected block color.
2. Locks onto one block and keeps checking it after every movement.
3. Centers the block while driving closer.
4. Drives forward while moving the camera down in small steps.
5. Keeps following the locked block into the bottom edge of the camera view.
6. Stops when that close, centered block is no longer detected for three frames.
7. Moves the arm to the pickup pose.
8. Checks for target-color pixels under the claw.
9. Closes the claw only if that final pickup-zone check passes.

The pickup sequence only runs if approach succeeds.

## Run

```bash
cd /home/robot/pathfinder
python3 skills/block_approach_pickup/run_demo.py --color blue
```

For repeat testing when the robot area is already clear:

```bash
python3 skills/block_approach_pickup/run_demo.py --color blue --yes
```

To skip the pickup camera check during calibration:

```bash
python3 skills/block_approach_pickup/run_demo.py --color blue --no-pickup-check
```

The tracked handoff does not use a blind forward settle by default. If testing
shows that a small extra nudge is still required, enable one explicitly:

```bash
python3 skills/block_approach_pickup/run_demo.py --color blue --settle-seconds 0.35
```

Do this only during calibration. The robot cannot see the block during that
extra movement.

Valid colors are `red`, `blue`, and `yellow`.

## Safety

- Put the robot on the floor with clear space around it.
- Keep hands clear of the robot, arm, and claw.
- Use a fresh battery before judging movement tuning.
- Stop if the block is not visible and directly reachable after approach.
