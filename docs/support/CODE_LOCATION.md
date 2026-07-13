# Where the code lives

Use this page when you need to know where the robot code is, where to run commands, or which folder to look at first.

## On the robot

On the robot, the official workshop code should live here:

```bash
/home/robot/pathfinder
```

You usually reach it from the Pi 500:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
```

The team edit folder is separate:

```bash
/home/robot/team_code
```

Use `/home/robot/pathfinder` for official examples and updates. Use `/home/robot/team_code` for team edits and experiments.

## Repo Folders

| Folder/File | What It Is For |
|-------------|----------------|
| `skills/` | Main workshop demos. Start here when testing robot capabilities. |
| `scripts/tools/` | Useful utilities like battery checks, camera checks, and web helpers. |
| `lib/` | Shared robot control code used by the demos. |
| `web/` | Browser-based robot control interface. |
| `robot.py` | Shared high-level robot interface used by combined skills. |
| `start_robot.py` | Boot-time hardware initialization and status checks. |
| `Deviation.yaml` | Servo calibration offsets; facilitator-only. |

Most participants should run scripts from `skills/`. Most code changes should start in `/home/robot/team_code`.

## Testing Robot Behavior

If you are testing robot behavior directly:

- Start with `skills/README.md`
- Then `skills/mecanum_drive/`
- Then `skills/sonar_sensors/`
- Then `skills/robotic_arm/`
- Then `skills/camera_vision/`
- Then `skills/apriltag_navigation/`, `skills/block_detection/`, `skills/visual_servoing/`, `skills/autonomous_pickup/`, and `skills/line_following/`

Manual control tools come after the core capability demos:

- [Web Manual Control](../workshop/WEB_MANUAL_CONTROL.md)
- [Gamepad Remote Control](../workshop/GAMEPAD_REMOTE_CONTROL.md)
