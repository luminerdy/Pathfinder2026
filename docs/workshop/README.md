# Pathfinder2026 Workshop Guide

This is the main event guide for Pathfinder2026.

Work through the phases in order:

1. Assemble
2. Capabilities Exploration
3. Course Challenge

For the workshop, the Pi 500 and robot images should already be created. Skip image-build documents during the event.

If something fails, use [Student Troubleshooting](TROUBLESHOOTING.md). Compare with another team first. Get help right away if the issue involves wiring, batteries, heat, smoke, broken parts, or `sudo` commands.

## Phase 1: Assemble

Set up the Pi 500 control hub, assemble the robot, then connect and test.

Teams can split up at first:

| Path | Guide | Goal |
|------|-------|------|
| Pi 500 setup | [C1: Pi 500 Setup](../setup/C1_PI500_SETUP.md) | Get the control hub powered, online, and ready |
| robot assembly | [B1: robot Assembly Guide](B1_ROBOT_ASSEMBLY_GUIDE.md) | Build the robot and make it safe to power |

Then come back together:

| Step | Guide | Goal |
|------|-------|------|
| robot IP | [C2: robot Pi WiFi Setup](../setup/C2_ROBOT_PI_WIFI_SETUP.md) | Power the robot and find the robot IP |
| Connect/test | [C3: Connect and Test](../setup/C3_CONNECT_AND_TEST.md) | Connect Pi 500 to robot and verify hardware |

Use the overview guide if you want the whole Assemble phase on one page: [Assemble](ASSEMBLE.md).

## Phase 2: Capabilities Exploration

Run the capability demos before trying the course.

Start here:

- [Capabilities Exploration](CAPABILITIES_EXPLORATION.md)
- [Configuration Guide](CONFIG_GUIDE.md)

Recommended before Phase 3:

| Step | Capability | Demo |
|------|------------|------|
| D1 | Mecanum drive | `python3 skills/mecanum_drive/run_demo.py` |
| D2 | Sonar sensors | `python3 skills/sonar_sensors/run_demo.py` |
| D3 | robotic arm | `python3 skills/robotic_arm/run_demo.py` |
| D4 | Camera vision | `python3 skills/camera_vision/test_camera.py` |
| E3 | Block detection | `python3 skills/block_detection/run_demo.py` |

Manual control after capability demos:

| Step | Tool | Guide |
|------|------|-------|
| D5 | Web manual control | [D5: Web Manual Control](D5_WEB_MANUAL_CONTROL.md) |
| D6 | Gamepad remote control | [D6: Gamepad Remote Control](D6_GAMEPAD_REMOTE_CONTROL.md) |

Optional if time allows:

| Step | Capability | Demo |
|------|------------|------|
| E2 | AprilTag navigation | `python3 skills/apriltag_navigation/run_demo.py` |
| E4 | Visual servoing | `python3 skills/visual_servoing/run_demo.py` |
| E5 | Autonomous pickup | `python3 skills/autonomous_pickup/run_demo.py` |
| E6 | Line following | `python3 skills/line_following/run_demo.py` |

## Phase 3: Course Challenge

Use the robot capabilities to complete a course.

Start here:

- [Course Challenge](COURSE_CHALLENGE.md)

Keep the first strategy simple, then improve it.

Before a course run:

- Check battery voltage.
- Confirm camera is working.
- Confirm the arm starts in a safe position.
- Clear the course of people and loose cables.
- Choose a simple first strategy.

## Helpful Links

| Need | Guide |
|------|-------|
| Troubleshooting | [Student Troubleshooting](TROUBLESHOOTING.md) |
| Safe team code edits | [C5: Team Code Workflow](../setup/C5_TEAM_CODE_WORKFLOW.md) |
| Short team handout | [Team Start Handout](../handouts/TEAM_START_HANDOUT.md) |
