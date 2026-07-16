# Block Approach And Pickup

Experimental combined block automation for Pathfinder2026.

This is not part of the event participant flow yet. It is for calibration work
only.

## What It Does

1. Finds one selected block color.
2. Drives to the approach handoff position.
3. Stops the drive motors.
4. Moves forward a tiny settle distance.
5. Stops the drive motors again.
6. Runs the tested front pickup arm sequence.

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

To skip the final settle nudge:

```bash
python3 skills/block_approach_pickup/run_demo.py --color blue --no-settle
```

Valid colors are `red`, `blue`, and `yellow`.

## Safety

- Put the robot on the floor with clear space around it.
- Keep hands clear of the robot, arm, and claw.
- Use a fresh battery before judging movement tuning.
- Stop if the block is not visible and directly reachable after approach.
