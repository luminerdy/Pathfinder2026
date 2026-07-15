# Block Pickup

Experimental pickup-only test for Pathfinder2026 block automation.

This is not part of the event participant flow yet. Use it only while tuning
the autonomous block approach and pickup behavior.

## What It Does

- Stops the drive motors.
- Opens the claw.
- Moves the arm to the tested front pickup pose.
- Closes the claw on the block.
- Lifts the arm to the carry position.

The script does not drive the robot. The robot must already be positioned with
one block directly in front of the claw.

## Run

```bash
cd /home/robot/pathfinder
python3 skills/block_pickup/run_demo.py
```

For repeat testing when the block is already placed and the arm area is clear:

```bash
python3 skills/block_pickup/run_demo.py --yes
```

## Safety

- Keep hands clear of the arm and claw.
- Use this only after servo wiring has passed the Phase 1 arm test.
- Stop if the block is not directly in front of the claw.
