# Assemble

**Phase 1 of 3**

The goal of Phase 1 is to prepare the Pi 500, assemble the robot, connect the two computers, and verify the robot hardware.

The Pi 500 and robot SD cards are already imaged for the event. Do not use the OS build guides during the workshop unless a facilitator is repairing an image.

## Start In Parallel

A three-person team can begin both tracks at the same time:

| Team Members | Track | Guide | Finish With |
|--------------|-------|-------|-------------|
| Person 1 | Pi 500 | [Pi 500 Setup](../setup/PI500_SETUP.md) | Pi 500 powered, online, and ready for VS Code |
| Persons 2 and 3 | robot | [robot Assembly Guide](ROBOT_ASSEMBLY_GUIDE.md) | robot assembled and safe to power on |

Talk to the other team members as you work. The Pi 500 track may finish first; use that time to help check the robot assembly.

## Come Back Together

When both tracks are complete, the whole team continues in this order:

1. [robot Pi WiFi Setup](../setup/ROBOT_PI_WIFI_SETUP.md) - power on safely and find the robot IP.
2. [Connect and Test](../setup/CONNECT_AND_TEST.md) - connect from the Pi 500 and verify the battery, motors, servos, sonar, and camera.

These checks confirm that the robot is assembled and wired correctly. Capability demonstrations belong in Phase 2.

## Phase 1 Complete

The team is ready for Phase 2 when:

- The Pi 500 and robot are on the workshop network.
- SSH works from the Pi 500 to the robot.
- Battery, motor, servo, sonar, and camera checks pass.
- The team knows how to stop a running program with `Ctrl+C`.

If a check fails, use [Student troubleshooting](../support/TROUBLESHOOTING.md) and re-check the assembly before changing code.

## Next Phase

Continue to [Phase 2: Capabilities Exploration](CAPABILITIES_EXPLORATION.md).
