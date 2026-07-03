# C2: robot Pi WiFi Setup

**Phase 1: Assemble**

**Purpose:** Power on the assembled robot, confirm it is on the workshop network, and find the robot IP address for C3.

This is an event-time step. The robot SD card image should already be created before the event. Do not run [A2: robot Pi OS Build](A2_ROBOT_PI_OS_BUILD.md) during the workshop unless a facilitator tells you to rebuild a robot SD card.

## Prerequisites

- robot is assembled: [B1 robot Assembly Guide](../workshop/B1_ROBOT_ASSEMBLY_GUIDE.md)
- robot batteries are installed and charged
- Pi 500 is on workshop WiFi: [C1 Pi 500 Setup](C1_PI500_SETUP.md)
- temporary monitor and keyboard/mouse for the robot Pi, if the robot does not have a display attached

## Step 1: Power On The robot Safely

1. Put the robot on the floor or a safe test stand.
2. Keep hands clear of wheels and arm joints.
3. Turn on robot power.
4. Wait for the robot Pi to finish booting.

## Step 2: Open A Terminal On The robot Pi

This step is done on the robot Pi, not on the Pi 500.

If the robot has a monitor attached, open a terminal on the robot Pi.

The prompt should look something like:

```text
robot@pathfinder:~ $
```

If you cannot open a terminal on the robot Pi, ask a facilitator for help connecting a temporary monitor and keyboard/mouse.

## Step 3: Find The robot IP

On the robot Pi terminal, run:

```bash
hostname -I
```

You may see one or more addresses. Use the workshop network IPv4 address.

Example:

```text
10.10.10.142
```

Do not use:

- `127.0.0.1`
- `169.254.x.x`
- the Pi 500 IP

Write the robot IP on the team handout or a piece of tape near the Pi 500.

## Step 4: If The robot Has No Workshop IP

If `hostname -I` returns nothing, or only shows an address that starts with `169.254`, the robot is probably not on the workshop WiFi yet.

Ask a facilitator to check the robot WiFi connection.

Useful facilitator command:

```bash
nmcli dev wifi list
```

If the robot image already has the workshop WiFi saved, rebooting the robot may be enough:

```bash
sudo reboot
```

After the robot boots again, repeat Step 3.

## Step 5: Confirm Network From The Pi 500

Now move back to the Pi 500.

On the Pi 500 terminal, run:

```bash
ping <ROBOT_IP>
```

Stop the ping with `Ctrl+C`.

Success means the Pi 500 can see the robot on the workshop network.

If ping fails:

- Confirm you typed the robot IP from Step 3.
- Confirm the Pi 500 is on the workshop WiFi.
- Repeat Step 3 on the robot Pi in case the IP changed.
- Compare with another team before asking a facilitator.

## Step 6: Keep The Team On One Address

Use only the robot IP for:

- SSH
- VS Code Remote SSH
- Web controls

Do not use the Pi 500 IP as a robot connection target.

## Ready For C3 In Phase 1

The team is ready for connect/test when:

- robot is powered on.
- robot IP was found from the robot Pi using `hostname -I`.
- Pi 500 can ping the robot IP.
- Team knows to use `robot@<ROBOT_IP>`.

Next: [C3: Connect and Test](C3_CONNECT_AND_TEST.md)
