# Block Approach - Quick Reference

**Approach one selected colored block without pickup**

This is the first movement step after the block detection viewer. It uses the same color detection, merge logic, and target-selection scoring, then moves the robot in short pulses toward the selected block.

The script moves the shoulder/camera angle to keep the block visible as it gets close. It does not close the claw and does not run a pickup sequence.

## Run

```bash
cd /home/robot/pathfinder
python3 skills/block_approach/run_demo.py --color blue
```

Other colors:

```bash
python3 skills/block_approach/run_demo.py --color red
python3 skills/block_approach/run_demo.py --color yellow
```

## Safety

- Put the robot on the floor, not on a table.
- Clear space in front of and beside the robot.
- The battery check must pass before motors run.
- The target must be stable for several frames before movement.
- The shoulder/camera only moves within approach-view positions.
- Movement happens in short pulses, then motors stop and the camera checks again.
- Press `Ctrl+C` to stop.

## What Success Looks Like

The robot should:

1. Find the selected color.
2. Wait until the selected target is stable.
3. Strafe gently until the target is near center.
4. Tilt the shoulder/camera down as the block gets close.
5. Creep forward toward the block.
6. Stop when the block is centered and visible at the close-view camera angle.

If the target jumps, the robot should stop and wait instead of chasing noise.
