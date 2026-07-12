# Skills

This folder contains robot capability demos and advanced behaviors.

## Start With Demo Folders

Most teams should begin with folders that contain `run_demo.py`:

| Folder | What It Tests |
|--------|---------------|
| `mecanum_drive/` | Driving, strafing, and turning |
| `sonar_sensors/` | Distance sensing and obstacle checks |
| `robotic_arm/` | Tested pickup-and-load arm sequence |
| `camera_vision/` | Camera capture and basic vision |
| `block_detection/` | Colored block detection |
| `apriltag_navigation/` | AprilTag detection and navigation |
| `visual_servoing/` | Camera-guided approach |
| `autonomous_pickup/` | Block pickup sequence |
| `line_following/` | Tape line following |
| `gamepad_drive/` | Gamepad/manual driving |

Run demos from the robot:

```bash
cd /home/robot/pathfinder
python3 skills/mecanum_drive/run_demo.py
```

## Advanced Flat Files

The loose `.py` files in this folder are advanced combined behaviors. They may use several robot capabilities at once.

Examples:

| File | Purpose |
|------|---------|
| `bump_grab.py` | Find, approach, and grab a block |
| `strafe_nav.py` | AprilTag navigation with mecanum strafing |
| `block_approach.py` | Vision-guided block approach |
| `block_pursue.py` | Continuous block pursuit |
| `auto_pickup.py` | Older standalone pickup flow |

Use these after the basic demos work.

## Editing Code

Do not experiment directly in the official `/home/robot/pathfinder` copy during the event unless a facilitator says to.

Preferred workflow:

1. Copy the file into the team's working folder.
2. Rename it clearly.
3. Make one small change.
4. Test it.
5. Write down what changed and what happened.

The official code can be updated from GitHub during the event. Team experiments can be overwritten if they are made directly inside the official files.
