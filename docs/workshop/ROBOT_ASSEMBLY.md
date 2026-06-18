# Robot Assembly

Robot Assembly gets each team from parts to a verified robot.

## Goal

At the end of this phase, the team should have a robot that can power on, connect to the Pi 500, report battery voltage, move safely, see through the camera, and move the arm.

## Build Checklist

- Assemble the robot chassis.
- Install the mecanum wheels in the correct orientation.
- Attach the robotic arm and gripper.
- Mount the camera where it can see the floor and course targets.
- Connect sonar and RGB module.
- Install charged 18650 batteries.
- Label the robot and Pi 500 for the team.

## Pi 500 Setup

Use the Pi 500 as the team's coding and control hub.

Relevant setup docs:

- [Pi 500 OS Build](../setup/A1_PI500_OS_BUILD.md)
- [Pi 500 Setup](../setup/C1_PI500_SETUP.md)

## Robot Pi Setup

The Robot Pi runs headless on the robot.

Relevant setup docs:

- [Robot Pi OS Build](../setup/A1_ROBOT_PI_OS_BUILD.md)
- [Connect and Test](../setup/C2_CONNECT_AND_TEST.md)

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

- Battery voltage is safe.
- SSH works from the Pi 500.
- Camera test passes.
- Arm demo runs without binding.
- Drive demo runs safely.
- Team understands how to stop the robot.
