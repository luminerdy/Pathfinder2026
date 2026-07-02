# Pathfinder2026 Workshop Guide

This is the main event guide for Pathfinder2026.

Use this folder when you are planning, running, or editing the workshop flow.

The workshop has three phases:

1. Assemble
2. Capabilities Exploration
3. Course Challenge

The goal is to build a working robot, learn its capabilities, then combine those skills into a course run.

For a short printable team guide, use [Team Start Handout](../handouts/TEAM_START_HANDOUT.md).

If something fails during the event, use [Student Troubleshooting](TROUBLESHOOTING.md). Compare with another team before asking a facilitator, unless the issue involves wiring, batteries, heat, smoke, broken parts, or `sudo` commands.

## Where To Work

Use these files for the event flow:

| File | Use it for |
|------|------------|
| [README.md](README.md) | Main workshop index and event flow |
| [ASSEMBLE.md](ASSEMBLE.md) | Phase 1 overview |
| [B1_ROBOT_ASSEMBLY_GUIDE.md](B1_ROBOT_ASSEMBLY_GUIDE.md) | robot assembly instructions |
| [CAPABILITIES_EXPLORATION.md](CAPABILITIES_EXPLORATION.md) | Phase 2 demos and tuning path |
| [CONFIG_GUIDE.md](CONFIG_GUIDE.md) | Safe configuration changes |
| [COURSE_CHALLENGE.md](COURSE_CHALLENGE.md) | Phase 3 course structure |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Student-facing troubleshooting |

Use [../setup](../setup) for image builds, Pi setup, robot WiFi, connection testing, and update procedures.

## Phase 1: Assemble

Set up the Pi 500 control hub and assemble the robot before running code.

Teams split into two paths, then come back together:

| Path | Guide | Goal |
|------|-------|------|
| Pi 500 setup | [C1: Pi 500 Setup](../setup/C1_PI500_SETUP.md) | Get the control hub powered, online, and ready for VS Code |
| robot assembly | [B1: robot Assembly Guide](B1_ROBOT_ASSEMBLY_GUIDE.md) | Build the robot and make it safe to power |
| robot Pi/WiFi | [C2: robot Pi WiFi Setup](../setup/C2_ROBOT_PI_WIFI_SETUP.md) | Power the robot and get the robot IP |
| Connect/test | [C3: Connect and Test](../setup/C3_CONNECT_AND_TEST.md) | Connect Pi 500 to robot and verify hardware |

Facilitator references:

- [C4: Update robot code](../setup/C4_UPDATE_ROBOT_CODE.md)
- [C5: Team code workflow](../setup/C5_TEAM_CODE_WORKFLOW.md)

Use the overview guide if you want the whole Assemble phase on one page: [Assemble](ASSEMBLE.md).

## Phase 2: Capabilities Exploration

Run the capability demos before trying the course.

Use the phase guide: [Capabilities Exploration](CAPABILITIES_EXPLORATION.md)

Use [Configuration Guide](CONFIG_GUIDE.md) before changing tuning files.

Start with manual web control:

```bash
python3 web/web_control.py
```

Open `http://<ROBOT_IP>:8080` from the Pi 500.

Required before the Course Challenge:

| Step | Capability | Demo |
|------|------------|------|
| D1 | Mecanum drive | `python3 skills/mecanum_drive/run_demo.py` |
| D2 | Sonar sensors | `python3 skills/sonar_sensors/run_demo.py` |
| D3 | robotic arm | `python3 skills/robotic_arm/run_demo.py` |
| D4 | Camera vision | `python3 skills/camera_vision/test_camera.py` |
| E3 | Block detection | `python3 skills/block_detection/run_demo.py` |

Optional if time allows:

| Step | Capability | Demo |
|------|------------|------|
| E2 | AprilTag navigation | `python3 skills/apriltag_navigation/run_demo.py` |
| E4 | Visual servoing | `python3 skills/visual_servoing/run_demo.py` |
| E5 | Autonomous pickup | `python3 skills/autonomous_pickup/run_demo.py` |
| E6 | Line following | `python3 skills/line_following/run_demo.py` |

## Phase 3: Course Challenge

Use the robot capabilities to complete a course.

Use the phase guide: [Course Challenge](COURSE_CHALLENGE.md)

The Course Challenge structure is still being refined. Keep this phase simple until the field and scoring are proven.

Before a course run:

- Check battery voltage.
- Confirm camera is working.
- Confirm the arm starts in a safe position.
- Clear the course of people and loose cables.
- Choose a simple first strategy, then improve it.
