# robot assembly

robot assembly is the first workshop phase. The goal is to turn a kit into a robot that is mechanically built, powered, connected, and safe to test.

## What This Phase Covers

1. Physical robot assembly
2. Pi 500 control hub setup
3. robot Pi setup
4. First SSH connection
5. Hardware verification

## Physical Assembly

Use the kit parts and event instructions to build the robot before running code.

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

## Pi 500 Setup

Use the Pi 500 as the team's coding and control hub.

Relevant setup docs:

- [Pi 500 OS Build](../setup/A1_PI500_OS_BUILD.md)
- [Pi 500 Setup](../setup/C1_PI500_SETUP.md)

## robot Pi setup

The robot Pi runs the code on the robot.

Relevant setup docs:

- [robot Pi OS build](../setup/A2_ROBOT_PI_OS_BUILD.md)
- [Connect and Test](../setup/C2_CONNECT_AND_TEST.md)

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

Run only one robot at a time during verification.

```bash
python3 scripts/tools/check_battery.py
python3 skills/camera_vision/test_camera.py
python3 skills/robotic_arm/run_demo.py
python3 skills/mecanum_drive/run_demo.py
```

## Ready To Move On

The team is ready for Capabilities Exploration when:

- robot is physically assembled.
- Wheels spin freely.
- Arm and gripper move without binding.
- Camera and sonar are mounted.
- Battery voltage is safe.
- SSH works from the Pi 500.
- Camera test passes.
- Drive demo runs safely.
- Team understands how to stop the robot.
