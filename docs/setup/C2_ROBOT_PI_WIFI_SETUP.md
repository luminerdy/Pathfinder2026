# C2: robot Pi WiFi Setup

**Purpose:** Power on the assembled robot, confirm it is on the workshop network, and get the robot IP address for C3.

This is an event-time step. The robot SD card image should already be created before the event. Do not run [A2: robot Pi OS Build](A2_ROBOT_PI_OS_BUILD.md) during the workshop unless a facilitator tells you to rebuild a robot SD card.

## Prerequisites

- robot is assembled: [B1 robot Assembly Guide](../workshop/B1_ROBOT_ASSEMBLY_GUIDE.md)
- robot batteries are installed and charged
- Pi 500 is on workshop WiFi: [C1 Pi 500 Setup](C1_PI500_SETUP.md)

## Step 1: Power On The robot

1. Put the robot on the floor or a safe test stand.
2. Turn on robot power.
3. Wait for the robot Pi to finish booting.
4. Keep hands clear of wheels and arm joints.

## Step 2: Get The robot IP

Use the robot IP from the facilitator.

If a facilitator needs to confirm the robot IP directly on the robot, run:

```bash
hostname -I
```

Write down only the robot IP for the team.

## Step 3: Confirm Network From The Pi 500

On the Pi 500:

```bash
ping <ROBOT_IP>
```

Stop the ping with `Ctrl+C`.

Success means the Pi 500 can see the robot on the workshop network.

## Step 4: Keep The Team On One Address

Use only the robot IP for:

- SSH
- VS Code Remote SSH
- Web controls

Do not use the Pi 500 IP as a robot connection target.

## Ready For C3

The team is ready for connect/test when:

- robot is powered on.
- robot IP is known.
- Pi 500 can ping the robot IP.
- Team knows to use `robot@<ROBOT_IP>`.

Next: [C3: Connect and Test](C3_CONNECT_AND_TEST.md)
