# robot Pi WiFi Setup

**Phase 1: Assemble**

**Purpose:** Power on the assembled robot, connect the robot Pi to the workshop WiFi, and find the robot IP address for connect/test.

This is an event-time step. The robot SD card image should already be created before the event. Do not run [robot Pi OS Build](ROBOT_PI_OS_BUILD.md) during the workshop unless a facilitator tells you to rebuild a robot SD card.

## Prerequisites

- robot is assembled: [robot Assembly Guide](../workshop/ROBOT_ASSEMBLY_GUIDE.md)
- robot batteries are installed and charged
- `GuestWifi.pdf` is available on the robot Pi desktop

## Step 1: Connect The robot Pi To A Monitor And Mouse

This step is done on the robot Pi, not on the Pi 500.

1. Connect the temporary monitor to the robot Pi.
2. Move the Pi 500 mouse to the robot Pi.

## Step 2: Power On The robot Safely

**Movement warning:** When the robot powers on, the startup script may move the arm to its startup position. Keep fingers, tools, cables, and loose parts away from the arm, gripper, wheels, and linkages before turning on power.

There are two robot power switches: one on the motor controller and one on the battery container.

<img src="../images/robot/23_robot_power_switches.jpg" width="400" alt="robot power switches">

1. Put the robot on the floor or a safe test stand.
2. Keep hands clear of wheels, arm joints, and the gripper.
3. Turn on both robot power switches.
4. Wait for the robot Pi to finish booting and for any startup arm movement to stop.

## Step 3: Connect The robot Pi To WiFi

Use the Pi 500 mouse to make the WiFi changes on the robot Pi. Use the on-screen keyboard if one appears.

Open `GuestWifi.pdf` from the robot Pi desktop and use the same workshop WiFi instructions used for the Pi 500.

Check the network icon at the top-right of the taskbar. If the network icon looks disconnected, click it and select the correct workshop WiFi network.

<img src="../images/robot/25_robot_wifi_icon_disconnected.jpg" width="200" alt="disconnected WiFi icon on Raspberry Pi desktop">

Type the WiFi password using the on-screen keyboard if needed.

## Step 4: Find The robot IP

When the robot is connected to WiFi, hover the mouse cursor over the active WiFi icon. Write down the assigned IPv4 address.

<img src="../images/robot/26_robot_wifi_ip_hover.jpg" width="600" alt="WiFi hover showing robot IP address">

Use the workshop network IPv4 address.

Write the robot IP on the team handout or a piece of tape near the Pi 500.

## Ready For Connect And Test In Phase 1

The team is ready for connect/test when:

- robot is powered on.
- robot Pi is connected to the workshop WiFi.
- robot IP was found from the robot Pi.

Next: [Connect and Test](CONNECT_AND_TEST.md)
