# E2: Gamepad Remote Control

**Phase 2 support: Capabilities Exploration**

Use gamepad remote control after the team has explored the individual capability scripts. The gamepad is a fast way to practice driving and field strategy.

## Hardware

- Logitech F710 gamepad
- F710 USB receiver plugged into the robot Pi, not the Pi 500
- Fresh AA batteries in the gamepad
- Gamepad back switch set to `X`

## Safety

- Put the robot on the floor, not on a table.
- Clear a 4-foot by 4-foot area.
- Keep hands clear of wheels, arm joints, and the gripper.
- Keep a thumb near the `Back` button for emergency stop.

## Gamepad Detection

The robot image should already include `python3-pygame` and `joystick`.

The control script checks for the gamepad when it starts. If no gamepad is detected, the robot beeps and keeps checking until the gamepad is connected. Press `Ctrl+C` to quit.

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
python3 skills/gamepad_drive/gamepad_drive.py
```

If the gamepad is not detected:

- Confirm the USB receiver is plugged into the robot Pi.
- Confirm the gamepad is powered on.
- Confirm the back switch is set to `X`, not `D`.
- Try fresh gamepad batteries.
- If needed, check detection manually:

  ```bash
  lsusb | grep -i logitech
  ls /dev/input/js*
  ```

If the script says `pygame not installed`, the robot image is missing the gamepad package. Ask for help before installing packages during the event.

## Run Gamepad Control

```bash
python3 skills/gamepad_drive/gamepad_drive.py
```

The script should print the gamepad name and say it is ready.

## Controls

| Control | Action |
|---------|--------|
| Left stick Y | Left wheels forward/backward |
| Right stick Y | Right wheels forward/backward |
| Either stick X | Strafe left/right using all wheels |
| Right trigger | Forward, analog speed |
| Left trigger | Backward, analog speed |
| Right bumper | Turn right |
| Left bumper | Turn left |
| D-pad Up | Front pickup |
| D-pad Down | Drop into rear bin |
| D-pad Left | Left side pickup |
| D-pad Right | Right side pickup |
| A | Look forward, reset arm |
| B | Open claw |
| Y | Nod yes |
| X | Shake no |
| Back | Emergency stop |
| Start | Quit |

## Stop Gamepad Control

Press `Start` on the gamepad, or press `Ctrl+C` in the terminal.

When the program exits, it stops the drive motors and returns the arm to the forward position.

## If It Does Not Work

- If `pygame not installed` appears, the robot image is missing the gamepad package.
- If `No gamepad detected` repeats, check the USB receiver, gamepad power, batteries, and `X` mode.
- If the robot drives the wrong direction, stop and compare with Phase 1 motor wiring checks before changing code.

Next: [Phase 3: Course Challenge](COURSE_CHALLENGE.md).
