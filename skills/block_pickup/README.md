# Block Pickup

Experimental pickup-only test for Pathfinder2026 block automation.

This is not part of the event participant flow yet. Use it only while tuning
the autonomous block approach and pickup behavior.

## What It Does

- Stops the drive motors.
- Opens the claw.
- Moves the arm to the tested front pickup pose.
- For calibration only, can drive forward briefly while lowering the arm.
- Optionally checks whether the selected block color is visible under the claw.
- Closes the claw on the block if the camera check passes, or immediately if
  the camera check is not enabled.
- Lifts the arm to the carry position.

The script does not drive the robot by default. The robot must already be
positioned with one block directly in front of the claw.

## Run

```bash
cd /home/robot/pathfinder
python3 skills/block_pickup/run_demo.py
```

For repeat testing when the block is already placed and the arm area is clear:

```bash
python3 skills/block_pickup/run_demo.py --yes
```

To stop before closing the claw unless the target color is visible under the
claw:

```bash
python3 skills/block_pickup/run_demo.py --color blue --check-camera
```

Calibration only: to test the synchronized forward nudge used by the combined
approach-and-pickup script:

```bash
python3 skills/block_pickup/run_demo.py --color blue --check-camera --drive-during-arm --drive-power 24 --drive-seconds 0.25
```

## Safety

- Keep hands clear of the arm and claw.
- Use this only after servo wiring has passed the Phase 1 arm test.
- Stop if the block is not directly in front of the claw.
