# Web Manual Control

**Phase 2 support: Capabilities Exploration**

Use web manual control after the team has run the individual capability demos. The web page is useful for practice driving, camera viewing, battery checking, and moving the arm from the Pi 500 browser.

## Why Use This

Web manual control lets the team test strategy without writing new code first. It is also useful for checking whether the robot responds before trying a course run.

## Safety

- Put the robot on the floor, not on a table.
- Clear a 4-foot by 4-foot area.
- Keep hands clear of wheels, arm joints, and the gripper.
- Keep a terminal open so you can press `Ctrl+C` to stop the web server if needed.

## Start The Web Server

Run these commands while connected to the robot:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
python3 web/web_control.py
```

Leave that terminal running.

## Open The Web Page

From the Pi 500 browser, open:

```text
http://<ROBOT_IP>:8080
```

Use the robot IP from Phase 1. Do not use the Pi 500 IP.

## Controls

- WASD or arrow keys: drive
- Q/E: strafe left/right
- Space: stop
- Drive buttons: press and hold to move, release to stop
- The page repeats movement commands only while a control is held.
- The robot stops automatically if movement commands stop arriving.
- Motor power sliders: adjust speed
- Arm sliders: move individual servos
- Save/load positions: store arm poses for testing

## Automation Buttons

The web page also includes two automation buttons near the live camera feed.

Use these only after the team has already tested the individual capability demos from Capabilities Exploration.

| Button | Action |
|--------|--------|
| AprilTag Nav | Moves the arm/camera forward, searches for event AprilTags `582`, `583`, `584`, or `585`, drives toward the detected tag, then returns to web control |
| Line Follow | Moves the camera down, follows the lime green tape, then returns to web control |
| Stop Automation | Requests cancellation and stops the drive motors |

While an automation runs, the live camera feed shows tracking overlays:

- AprilTag Nav: visible event tags are boxed and labeled.
- Line Follow: the center line and detected line position are shown.

Manual drive commands are blocked while automation is running. Press `Stop Automation` before returning to manual driving.

## If A Movement Button Does Not Respond

- Check the drive status message under the buttons.
- Confirm the robot battery status says it is safe to drive.
- Confirm the terminal running `web_control.py` is still active.
- Refresh the browser page.
- Stop and restart the web server if needed.

## If An Automation Does Not Work

- Press `Stop Automation`.
- Run the matching individual capability demo first.
- For AprilTag Nav, confirm the arm/camera is looking forward and the tag is visible.
- For Line Follow, confirm the camera can see the lime green tape.
- Use the tracking overlay to see whether the robot is detecting the target.

## Stop Web Control

In the terminal running the web server, press:

```text
Ctrl+C
```

Then continue with [Gamepad Remote Control](GAMEPAD_REMOTE_CONTROL.md) or [Phase 3: Course Challenge](COURSE_CHALLENGE.md).
