# Pathfinder2026

**Summer 2026 Pathfinder robotics event**

Pathfinder2026 is the event repo for the 2026 Pathfinder robot workshop. It is meant to be easy for humans first: participants, facilitators, setup helpers, and whoever is editing the course.

The workshop flow follows the original PathfinderBot event shape:

1. Robot Assembly
2. Capabilities Exploration
3. Course Challenge

The robot software underneath comes from PathfinderV2.

## Start Here

If you are new to this repo, use this order:

1. [START_HERE.md](START_HERE.md) - event-day guide
2. [Robot Assembly](docs/workshop/ROBOT_ASSEMBLY.md) - build the robot and verify it works
3. [Capabilities Exploration](docs/workshop/CAPABILITIES_EXPLORATION.md) - run the robot demos
4. [Course Challenge](docs/workshop/COURSE_CHALLENGE.md) - combine skills on the field

## Where Is The Robot Code?

On the robot, the code should live here:

```bash
/home/robot/pathfinder
```

You usually reach it from the Pi 500:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
```

In this repo, the robot code is organized like this:

| Folder/File | What It Is For |
|-------------|----------------|
| `skills/` | Main workshop demos. Start here when testing robot capabilities. |
| `scripts/tools/` | Useful utilities like battery checks, camera checks, and web helpers. |
| `scripts/testing/` | Hardware and field test scripts. |
| `lib/` | Shared robot control code used by the demos. |
| `web/` | Browser-based robot control interface. |
| `config.yaml` | Shared robot configuration. |
| `sdk/` | Lower-level vendor communication layer used by the robot code. |

Most participants should run scripts from `skills/`. Most code changes should also start there.

## Where Are The Documents?

| Folder/File | What It Is For |
|-------------|----------------|
| `README.md` | Repo overview and orientation. |
| `START_HERE.md` | Event-day participant path. |
| `CONTRIBUTING.md` | GitHub repo file rules, including no emojis in committed files. |
| `docs/workshop/` | Human-facing workshop phases. |
| `docs/setup/` | Pre-event Pi 500, Robot Pi, SD card, and connection setup. |
| `docs/calibration/` | Calibration and tuning notes. |
| `docs/archive/` | Historical development notes from PathfinderV2. |

## What Should I Work On?

If you are preparing the event:

- Use `docs/setup/` for SD cards, Pi setup, and connection testing.
- Use `docs/workshop/ROBOT_ASSEMBLY.md` to tighten the assembly flow.
- Use `docs/workshop/CAPABILITIES_EXPLORATION.md` to choose which demos participants run.
- Use `docs/workshop/COURSE_CHALLENGE.md` to capture the course design in your head.

If you are testing robot behavior:

- Start with `skills/mecanum_drive/`
- Then `skills/sonar_sensors/`
- Then `skills/robotic_arm/`
- Then `skills/camera_vision/`
- Then `skills/apriltag_navigation/`, `skills/block_detection/`, `skills/visual_servoing/`, `skills/autonomous_pickup/`, and `skills/line_following/`

If you are running the web controls:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
python3 web/web_control.py
```

Then open this from the Pi 500 browser:

```text
http://<ROBOT_IP>:8080
```

## Workshop Phases

### 1. Robot Assembly

Teams build the robot, prepare the Pi 500, connect to the Robot Pi, and verify the robot can safely move.

Guide: [Robot Assembly](docs/workshop/ROBOT_ASSEMBLY.md)

### 2. Capabilities Exploration

Teams run focused demos to learn the robot:

- Drive
- Sonar
- Arm
- Camera
- AprilTags
- Block detection
- Visual servoing
- Pickup
- Line following
- Web/manual control

Guide: [Capabilities Exploration](docs/workshop/CAPABILITIES_EXPLORATION.md)

### 3. Course Challenge

Teams combine capabilities on the field:

- Navigate the course
- Avoid obstacles
- Detect blocks
- Pick up, push, store, or deliver blocks
- Tune strategy for reliability and speed

Guide: [Course Challenge](docs/workshop/COURSE_CHALLENGE.md)

## Setup Links

For pre-event setup:

- [Pi 500 OS Build](docs/setup/A1_PI500_OS_BUILD.md)
- [Robot Pi OS Build](docs/setup/A2_ROBOT_PI_OS_BUILD.md)
- [Pi 500 Setup](docs/setup/C1_PI500_SETUP.md)
- [Connect and Test](docs/setup/C2_CONNECT_AND_TEST.md)
- [Bill of Materials](docs/setup/BILL_OF_MATERIALS.md)

## License

MIT License. See [LICENSE](LICENSE).
