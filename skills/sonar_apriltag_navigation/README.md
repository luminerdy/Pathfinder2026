# Sonar + AprilTag Navigation - Quick Reference

Experimental Area 2 navigation.

The robot drives toward AprilTag `583` while the forward sonar watches for the fixed white cardboard barriers. When sonar sees a barrier, the robot strafes until it finds the barrier edge, strafes a little farther for wheel clearance, then resumes AprilTag navigation.

## Quick Start

```bash
cd /home/robot/pathfinder
python3 skills/sonar_apriltag_navigation/run_demo.py
```

If the robot needs to clear barriers in the opposite direction:

```bash
python3 skills/sonar_apriltag_navigation/run_demo.py --strafe-direction left
```

## What It Does

1. Moves the arm/camera to the AprilTag viewing position.
2. Looks for Area 2 AprilTag `583`.
3. Drives toward the tag in short pulses.
4. Checks sonar before every movement pulse.
5. When sonar sees a barrier, strafes along the barrier until the edge clears.
6. Strafes a little farther so the wheels do not clip the barrier.
7. Repeats for each barrier until the robot reaches the tag.

## Tuning Values

| Option | Default | Meaning |
|--------|---------|---------|
| `--tag-id` | `583` | AprilTag to approach |
| `--barrier-cm` | `28` | Stop and clear a barrier when sonar is this close |
| `--clear-cm` | `55` | Treat the barrier edge as clear at this distance |
| `--strafe-direction` | `right` | Direction to slide around barriers |
| `--extra-clearance` | `0.45` | Extra strafe seconds after the edge is found |
| `--target-distance` | `0.50` | Stop distance from the AprilTag in meters |

## Safety

- The robot will move, strafe, and turn.
- Use only on the floor.
- Keep hands clear of the wheels, barriers, arm, and claw.
- Press `Ctrl+C` to stop.

## Testing Notes

Start with one barrier. Confirm:

- Sonar detects the barrier before the robot reaches it.
- The robot strafes the correct direction.
- The extra clearance is enough for the wheels.
- AprilTag `583` stays visible or becomes visible again after the strafe.

Then add the next barrier and test again.
