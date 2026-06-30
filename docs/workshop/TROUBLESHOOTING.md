# Student Troubleshooting

Use this page when the robot does not do what the guide says it should do.

## First Checks

Run these while connected to the robot:

```bash
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py
python3 scripts/tools/robot_status.py
```

Confirm:

- You are logged in as `robot`.
- You are in `/home/robot/pathfinder`.
- You are using the robot IP, not the Pi 500 IP.
- The robot is on the floor with room to move.

## Cannot SSH To The robot

From the Pi 500:

```bash
ping <ROBOT_IP>
ssh robot@<ROBOT_IP>
```

If ping fails:

- Confirm the Pi 500 and robot are on the same WiFi network.
- Ask the facilitator to confirm the current robot IP.
- Make sure the robot is powered on.

If SSH asks for a password after keys were set up:

- Use the robot password if needed.
- Ask for help before deleting SSH keys.

## Battery Low Or No Reading

Run:

```bash
python3 scripts/tools/check_battery.py
```

If the battery is low:

- Replace or charge the batteries.
- Do not run drive, pickup, or course demos.

If there is no reading:

- Check that the robot power switch is on.
- Check battery holder wiring.
- Ask a facilitator before continuing.

## robot Does Not Move

Run:

```bash
python3 scripts/tools/check_motors.py
```

If one wheel does not move:

- Check that motor cable.
- Check that the wheel is not blocked.
- Re-run the motor check after fixing the cable.

If all wheels do not move:

- Check battery first.
- Confirm the robot is on the floor, not hanging by a cable.
- Press `Ctrl+C` to stop any running demo, then try again.

## Arm Or Gripper Does Not Move

Run:

```bash
python3 scripts/tools/check_servos.py
```

Expected servo mapping:

| Servo | Part |
|-------|------|
| 1 | Gripper |
| 3 | Shoulder |
| 4 | Elbow |
| 5 | Wrist |
| 6 | Base |

If the wrong joint moves, ask a facilitator to check the servo wiring.

## Sonar Has No Reading

Run:

```bash
python3 scripts/tools/check_sonar.py
```

If it reports no reading:

- Make sure nothing is touching the sonar sensor.
- Point the robot toward a wall or large object.
- Re-seat the sonar cable if a facilitator says it is safe.

## Camera Is Not Working

Run:

```bash
ls /dev/video*
python3 skills/camera_vision/test_camera.py
```

If no camera appears:

- Re-seat the USB camera cable.
- Try a different USB port.
- Ask a facilitator to confirm the camera is detected.

## Web Page Does Not Load

On the robot:

```bash
cd /home/robot/pathfinder
python3 web/web_control.py
```

On the Pi 500 browser:

```text
http://<ROBOT_IP>:8080
```

If it does not load:

- Confirm the robot IP.
- Confirm the web server is still running on the robot.
- Do not use the Pi 500 IP in the browser URL.

## Demo Starts But Behaves Wrong

Stop the demo:

```text
Ctrl+C
```

Then write down:

- Demo name
- Battery voltage
- What moved correctly
- What moved incorrectly
- Any error message

Give that information to a facilitator.
