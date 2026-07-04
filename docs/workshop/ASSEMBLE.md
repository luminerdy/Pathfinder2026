# Assemble

**Phase 1 of 3**

Assemble is the first workshop phase. The goal is to prepare the team's Pi 500 control hub and build a robot that is mechanically ready, powered, connected, and safe to test.

For the workshop, the Pi 500 and robot OS images should already be created. Teams should skip the image-build documents and start with the event-day setup guides.

## What This Phase Covers

1. Pi 500 unbox, boot, network, GitHub, and VS Code setup
2. robot unpacking and physical assembly
3. robot Pi setup
4. First SSH connection from the Pi 500 to the robot
5. Hardware verification

## Pi 500 Setup

Use the Pi 500 as the team's coding and control hub.

Quick team handout:

- [Team Start Handout](../handouts/TEAM_START_HANDOUT.md)

This track covers:

- Unbox and connect the Pi 500.
- Boot Raspberry Pi OS.
- Connect to workshop WiFi.
- Confirm GitHub access.
- Verify VS Code and Remote SSH are ready.

Relevant setup docs:

- [Pi 500 Setup](../setup/C1_PI500_SETUP.md) - event-day guide
- [Pi 500 OS Build](../setup/A1_PI500_OS_BUILD.md) - facilitator pre-event image build, skip during workshop

## robot assembly

Use the kit parts and event instructions to build the robot before running code.

Dedicated event guide:

- [B1 robot Assembly Guide](B1_ROBOT_ASSEMBLY_GUIDE.md)

### Chassis

- Assemble the lower chassis.
- Mount the motor brackets.
- Route motor wires so they cannot touch the wheels.
- Keep access to the battery compartment.

### Mecanum Wheels

- Install all four mecanum wheels.
- Confirm the roller directions are mirrored correctly from left to right.
- Spin each wheel by hand and check for rubbing.
- Make sure wheel screws are tight before powered driving.

### Arm And Gripper

- Attach the arm base to the robot.
- Attach shoulder, elbow, wrist, and gripper assemblies.
- Move the arm gently by hand before powering servos.
- Check that the gripper can open and close without hitting the chassis.

### Camera

- Mount the camera where it can see the floor in front of the robot.
- Keep the cable away from the wheels and arm.
- Leave enough slack for small bumps, but not enough to snag.

### Sonar

- Mount sonar facing forward.
- Keep it level.
- Make sure the sensor is not blocked by the arm, camera, or team-built storage.

### Batteries

- Install charged 18650 batteries.
- Keep one spare charged pair per team if possible.
- Do not start driving until the battery check passes.

## Event Modifications

Teams may add storage or guides for blocks, but changes should not block:

- Camera view
- Sonar view
- Wheel movement
- Arm movement
- Battery access
- Power switch access

## robot Pi setup

The robot Pi runs the code on the robot.

Relevant setup docs:

- [C2 robot Pi WiFi Setup](../setup/C2_ROBOT_PI_WIFI_SETUP.md) - event-day guide
- [C3 Connect and Test](../setup/C3_CONNECT_AND_TEST.md) - event-day guide
- [robot Pi OS build](../setup/A2_ROBOT_PI_OS_BUILD.md) - facilitator pre-event image build, skip during workshop
- [C4 Update robot code](../setup/C4_UPDATE_ROBOT_CODE.md)
- [C5 Team code workflow](../setup/C5_TEAM_CODE_WORKFLOW.md)

## Where The Code Lives

On the robot:

```bash
/home/robot/pathfinder
```

From the Pi 500:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
```

Useful folders:

- `skills/` - workshop demos
- `scripts/tools/` - checks and utilities
- `web/` - browser control interface
- `lib/` - shared robot control code

## First Connection

From the Pi 500:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py
```

## Hardware Verification

Use C3 for the Phase 1 hardware checks:

- [C3 Connect and Test](../setup/C3_CONNECT_AND_TEST.md)

C3 checks battery, individual motors, arm servos, sonar, camera hardware, and the SSH connection. Capability demos happen in Phase 2.

## Phase 1 Complete

The team is ready for Capabilities Exploration when:

- robot is physically assembled.
- Wheels spin freely.
- Arm and gripper move without binding.
- Camera and sonar are mounted.
- Battery voltage is safe.
- SSH works from the Pi 500.
- Camera hardware test passes.
- Individual motor and servo checks pass.
- Team understands how to stop the robot.

## Next Phase

Continue to [Phase 2: Capabilities Exploration](CAPABILITIES_EXPLORATION.md).
