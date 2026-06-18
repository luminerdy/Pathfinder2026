# Pathfinder2026

**Summer 2026 Pathfinder robotics event**

Pathfinder2026 is an event-focused robotics workshop built around the Hiwonder MasterPi robot, Raspberry Pi 500 control hub, mecanum drive, robotic arm, camera vision, sonar, AprilTags, and a final course challenge.

This repo keeps the workshop flow from PathfinderBot and uses the updated PathfinderV2 software as the robot code foundation.

## Workshop Phases

### 1. Robot Assembly

Teams build and prepare the robot:

- Assemble the MasterPi chassis, mecanum wheels, arm, gripper, camera, and sonar.
- Prepare the Raspberry Pi 500 control hub.
- Prepare the Robot Pi image.
- Connect the Pi 500 to the robot over WiFi/SSH.
- Verify battery, motors, arm, camera, and sonar before driving.

Start here: [Robot Assembly](docs/workshop/ROBOT_ASSEMBLY.md)

### 2. Capabilities Exploration

Teams learn what the robot can do by running short, focused demos:

- Mecanum drive
- Sonar sensing
- Robotic arm movement
- Camera vision
- AprilTag navigation
- Block detection
- Visual servoing
- Autonomous pickup
- Line following
- Web/manual control

Start here: [Capabilities Exploration](docs/workshop/CAPABILITIES_EXPLORATION.md)

### 3. Course Challenge

Teams combine the capabilities into a course run:

- Navigate using AprilTags and/or line following.
- Avoid obstacles.
- Find and collect colored blocks.
- Use the arm or robot-mounted storage to carry blocks.
- Deliver blocks to the target area.
- Tune strategy for reliability, speed, and battery life.

Start here: [Course Challenge](docs/workshop/COURSE_CHALLENGE.md)

## Quick Start

If you are at the event, open [START_HERE.md](START_HERE.md).

If you are setting up hardware before the event, use:

- [Pi 500 OS Build](docs/setup/A1_PI500_OS_BUILD.md)
- [Robot Pi OS Build](docs/setup/A1_ROBOT_PI_OS_BUILD.md)
- [Pi 500 Setup](docs/setup/C1_PI500_SETUP.md)
- [Connect and Test](docs/setup/C2_CONNECT_AND_TEST.md)

Already connected to the robot?

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py
python3 web/web_control.py
```

Then open `http://<robot-ip>:8080` from the Pi 500.

## Repository Layout

```text
Pathfinder2026/
├── START_HERE.md
├── docs/
│   ├── workshop/       # Event phase guides
│   ├── setup/          # OS, Pi 500, Robot Pi, and connection setup
│   ├── calibration/    # Calibration notes
│   └── archive/        # Historical development notes
├── skills/             # Workshop capability demos
├── scripts/            # Calibration, testing, and utility scripts
├── lib/                # Robot control libraries
├── sdk/                # Vendor board communication layer
├── web/                # Browser-based robot control
└── LICENSE
```

## Software Foundation

Pathfinder2026 is based on PathfinderV2 and includes the newer robot software stack:

- Pi 500 control hub plus headless Robot Pi
- Platform auto-detection
- Mecanum movement helpers
- AprilTag navigation
- HSV block detection
- Visual servoing
- Autonomous pickup experiments
- Line following
- Web control interface

## License

MIT License. See [LICENSE](LICENSE).
