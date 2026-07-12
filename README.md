# Pathfinder2026

**Summer 2026 Pathfinder robotics event**

**Last Updated:** July 11, 2026

Pathfinder2026 is the event repo for the 2026 Pathfinder robot workshop. It is meant to be easy for humans first: participants, facilitators, setup helpers, and whoever is editing the course.

The workshop flow has three phases:

1. Assemble
2. Capabilities Exploration
3. Course Challenge

## Start Here

If you are at the event, work through the three phases in order:

1. [Phase 1: Assemble](docs/workshop/ASSEMBLE.md)
2. [Phase 2: Capabilities Exploration](docs/workshop/CAPABILITIES_EXPLORATION.md)
3. [Phase 3: Course Challenge](docs/workshop/COURSE_CHALLENGE.md)

For the workshop, the Pi 500 and robot images should already be created. The OS build documents are for facilitators preparing equipment before the event.

## Quick Event Links

| Phase | Start Here |
|-------|------------|
| Phase 1: Assemble | [Assemble](docs/workshop/ASSEMBLE.md) |
| Phase 2: Capabilities Exploration | [Capabilities Exploration](docs/workshop/CAPABILITIES_EXPLORATION.md) |
| Phase 3: Course Challenge | [Course Challenge](docs/workshop/COURSE_CHALLENGE.md) |

## Support Links

Use these when a phase tells you to, or when something is not working:

| Need | Guide |
|------|-------|
| Troubleshooting | [Student Troubleshooting](docs/workshop/TROUBLESHOOTING.md) |
| Safe team code edits | [C5: Team Code Workflow](docs/setup/C5_TEAM_CODE_WORKFLOW.md) |
| robot connection reference | [C6: robot Connection Reference](docs/setup/C6_ROBOT_CONNECTION_REFERENCE.md) |
| Update robot code | [C4: Update robot Code](docs/setup/C4_UPDATE_ROBOT_CODE.md) |

## Where Does The Code Live?

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

Most participants should run scripts from `skills/`. Most code changes should also start there.

## Testing Robot Behavior

If you are testing robot behavior directly:

- Start with `skills/README.md`
- Then `skills/mecanum_drive/`
- Then `skills/sonar_sensors/`
- Then `skills/robotic_arm/`
- Then `skills/camera_vision/`
- Then `skills/apriltag_navigation/`, `skills/block_detection/`, `skills/visual_servoing/`, `skills/autonomous_pickup/`, and `skills/line_following/`

Manual control tools come after the core capability demos:

- [E1: Web Manual Control](docs/workshop/E1_WEB_MANUAL_CONTROL.md)
- [E2: Gamepad Remote Control](docs/workshop/E2_GAMEPAD_REMOTE_CONTROL.md)

## Facilitator Setup Links

Use these before the event when preparing images, hardware, and setup flow:

- [Pi 500 OS Build](docs/setup/A1_PI500_OS_BUILD.md) - pre-event image build
- [robot Assembly Guide](docs/workshop/B1_ROBOT_ASSEMBLY_GUIDE.md)
- [robot Pi OS build](docs/setup/A2_ROBOT_PI_OS_BUILD.md) - pre-event image build
- [Pi 500 Setup](docs/setup/C1_PI500_SETUP.md)
- [robot Pi WiFi Setup](docs/setup/C2_ROBOT_PI_WIFI_SETUP.md)
- [Connect and Test](docs/setup/C3_CONNECT_AND_TEST.md)
- [robot Connection Reference](docs/setup/C6_ROBOT_CONNECTION_REFERENCE.md)
- [Bill of Materials](docs/setup/BILL_OF_MATERIALS.md)

## Repo Map

| Folder/File | What It Is For |
|-------------|----------------|
| `docs/workshop/` | The three event phases and their support pages. |
| `docs/setup/` | Pre-event Pi 500, robot Pi, SD card, and connection setup. |
| `docs/handouts/` | Short printable team handouts. |
| `docs/calibration/` | Calibration and tuning notes. |
| `docs/archive/` | Historical development notes. |
| `skills/` | Main workshop demos and robot capabilities. |
| `scripts/tools/` | Utilities like battery, motor, servo, sonar, and camera checks. |
| `lib/` | Shared robot control code used by the demos. |
| `web/` | Browser-based robot control interface. |
| `CONTRIBUTING.md` | GitHub repo file rules, including no emojis in committed files. |

## License

MIT License. See [LICENSE](LICENSE).
