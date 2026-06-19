# Start Here: Pathfinder2026 Event Guide

Welcome to Pathfinder2026. This workshop has three phases:

1. robot assembly
2. Capabilities Exploration
3. Course Challenge

The goal is to build a working robot, learn its capabilities, then combine those skills into a course run.

## Phase 1: robot assembly

Build and prepare the robot before running code.

Use the phase guide: [robot assembly](docs/workshop/ROBOT_ASSEMBLY.md)

Minimum checklist:

- robot chassis assembled
- Mecanum wheels installed correctly
- Arm and gripper attached
- Camera mounted and connected
- Sonar connected
- Batteries charged
- robot Pi booted
- Pi 500 connected to workshop WiFi
- Pi 500 can SSH into the robot
- Battery check passes

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py
```

## Phase 2: Capabilities Exploration

Run the capability demos before trying the course.

Use the phase guide: [Capabilities Exploration](docs/workshop/CAPABILITIES_EXPLORATION.md)

Recommended order:

| Step | Capability | Demo |
|------|------------|------|
| D1 | Mecanum drive | `python3 skills/mecanum_drive/run_demo.py` |
| D2 | Sonar sensors | `python3 skills/sonar_sensors/run_demo.py` |
| D3 | robotic arm | `python3 skills/robotic_arm/run_demo.py` |
| D4 | Camera vision | `python3 skills/camera_vision/test_camera.py` |
| E2 | AprilTag navigation | `python3 skills/apriltag_navigation/run_demo.py` |
| E3 | Block detection | `python3 skills/block_detection/run_demo.py` |
| E4 | Visual servoing | `python3 skills/visual_servoing/run_demo.py` |
| E5 | Autonomous pickup | `python3 skills/autonomous_pickup/run_demo.py` |
| E6 | Line following | `python3 skills/line_following/run_demo.py` |

Manual control is available from the web interface:

```bash
python3 web/web_control.py
```

Open `http://<ROBOT_IP>:8080` from the Pi 500.

## Phase 3: Course Challenge

Use the robot capabilities to complete a course.

Use the phase guide: [Course Challenge](docs/workshop/COURSE_CHALLENGE.md)

The course challenge should test:

- Driving accuracy
- AprilTag or line navigation
- Obstacle awareness
- Block detection
- Pickup or storage strategy
- Delivery to a target area
- Team communication and iteration

Before a course run:

- Check battery voltage.
- Confirm camera is working.
- Confirm the arm starts in a safe position.
- Clear the course of people and loose cables.
- Choose a simple first strategy, then improve it.

## Troubleshooting

**robot does not move**

- Check battery: `python3 scripts/tools/check_battery.py`
- Try a higher motor power with fresh batteries.
- Confirm the robot is on the floor, not lifted by a cable or stand.

**Camera not working**

- Run `ls /dev/video*`
- Re-seat the USB camera cable.
- Try `python3 skills/camera_vision/test_camera.py`

**AprilTags not detected**

- Use tag36h11 tags.
- Improve lighting.
- Make sure tags are large enough and not glossy.

**Block detection unreliable**

- Avoid shadows.
- Tune HSV values in `skills/block_detection/config.yaml`.

**Line following loses the line**

- Use lime green tape.
- Slow down the line-following config.
- Avoid tight curves until the robot is tuned.

## License

MIT License. See [LICENSE](LICENSE).
