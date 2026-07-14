#!/usr/bin/env python3
"""
Gamepad Remote Control

Drive robot with Logitech F710 wireless gamepad.
Tank-style sticks + mecanum strafing + trigger speed + arm actions.

Arm sequences use tested servo positions for reliable pickup/drop.

Prerequisites:
  - F710 USB receiver plugged into robot Pi
  - Gamepad on, back switch set to X (XInput)
  - pygame installed: sudo apt install python3-pygame

Usage:
    python3 gamepad_drive.py

Controls:
  Left stick Y:   Left wheels forward/backward
  Right stick Y:  Right wheels forward/backward
  Either stick X: Strafe left/right with all wheels
  Right trigger:  Forward (analog speed)
  Left trigger:   Backward (analog speed)
  Right bumper:   Turn right in place
  Left bumper:    Turn left in place

  D-pad Up:       Pickup block (front)
  D-pad Down:     Backward drop block (into rear bin)
  D-pad Left:     AprilTag navigation automation
  D-pad Right:    Line following automation

  A:              Look forward (reset arm)
  B:              Open claw
  Y:              Nod yes
  X:              Shake no

  Back:           EMERGENCY STOP
  Start:          Quit
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

try:
    import pygame
except ImportError:
    print("pygame not installed. Run: sudo apt install python3-pygame")
    sys.exit(1)

from lib.board import get_board
from lib.arm_positions import Arm
from skills.strafe_nav import StrafeNavigator
from skills.line_following.line_follower import LineFollower

# === CONFIG ===
MAX_SPEED = 50          # Maximum motor duty cycle (0-100)
TURN_SPEED = 40         # In-place turn speed
DEADZONE = 0.15         # Ignore stick values below this
POLL_RATE = 50          # Hz (20ms per loop)
LEFT_X_AXIS = 0         # Left stick horizontal
LEFT_Y_AXIS = 1         # Left stick vertical
LEFT_TRIGGER_AXIS = 2   # Left trigger on the F710 in XInput mode
RIGHT_X_AXIS = 3        # Right stick horizontal
RIGHT_Y_AXIS = 4        # Right stick vertical
RIGHT_TRIGGER_AXIS = 5  # Right trigger on the F710 in XInput mode
EVENT_TAG_IDS = (582, 583, 584, 585)
APRILTAG_TARGET_DISTANCE = 0.50
APRILTAG_SEARCH_TIMEOUT = 40.0
APRILTAG_NAV_TIMEOUT = 30.0
LINE_FOLLOW_TIMEOUT = 30.0


# === DRIVE HELPERS ===

def apply_deadzone(value):
    """Zero out small values (stick drift)."""
    if abs(value) < DEADZONE:
        return 0.0
    return value


def clamp(value, min_val, max_val):
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def axis_value(gamepad, axis_index):
    """Read an axis if it exists; return 0 for missing optional axes."""
    if axis_index >= gamepad.get_numaxes():
        return 0.0
    return gamepad.get_axis(axis_index)


def trigger_value(gamepad, axis_index):
    """Read an analog trigger as 0 released to 1 fully pressed.

    The F710 may report trigger rest as -1, but a missing or centered axis reads
    near 0. Treat that as released so the robot never drives by itself.
    """
    if axis_index >= gamepad.get_numaxes():
        return 0.0

    raw = gamepad.get_axis(axis_index)
    if raw <= -0.5:
        value = (raw + 1.0) / 2.0
    elif raw <= DEADZONE:
        value = 0.0
    else:
        value = raw

    return clamp(value, 0.0, 1.0)


def beep_missing_gamepad(board):
    """Beep so teams know the receiver/gamepad was not detected."""
    try:
        board.set_buzzer(1200, 0.15, 0.1, 1)
    except Exception:
        pass


def wait_for_gamepad(board):
    """Keep beeping and checking until a gamepad is detected."""
    while pygame.joystick.get_count() == 0:
        print("No gamepad detected!")
        beep_missing_gamepad(board)
        print("  - USB receiver plugged into robot Pi?")
        print("  - Gamepad powered on (green LED)?")
        print("  - Back switch set to X (not D)?")
        print("  Waiting for gamepad. Press Ctrl+C to quit.")
        time.sleep(1.0)
        pygame.joystick.quit()
        pygame.joystick.init()

    gamepad = pygame.joystick.Joystick(0)
    gamepad.init()
    return gamepad


def combined_strafe(left_x, right_x):
    """Use either stick X to strafe all four wheels."""
    if left_x and right_x:
        return (left_x + right_x) / 2
    if left_x:
        return left_x
    return right_x


def stop_drive(board):
    """Stop all four drive motors."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def automation_cancel_requested(board):
    """Return True when Back or Start is pressed during an automation.

    Automation routines run inside the gamepad process, so pygame events must
    still be drained while the automation is active. Otherwise the Back button
    would not be seen until after the automation finished.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop_drive(board)
            return True
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 6:  # Back
                stop_drive(board)
                print("Automation cancelled with Back")
                return True
            if event.button == 7:  # Start
                stop_drive(board)
                print("Automation cancelled with Start")
                return True
    return False


def run_apriltag_navigation(board):
    """Run AprilTag navigation, then return to gamepad control."""
    print("AprilTag navigation automation...")
    print("  Looking for event tags: %s" % ", ".join(str(t) for t in EVENT_TAG_IDS))
    print("  Press Back to cancel and return to gamepad control.")
    stop_drive(board)

    # Create the navigator only for this run so its camera/sonar resources are
    # released before returning to manual gamepad control.
    nav = StrafeNavigator()

    def callback(tag_id, dist, angle, action):
        print("  Tag %s: %.2fm, %+.1fdeg - %s" % (tag_id, dist, angle, action))

    try:
        result = nav.search_and_navigate(
            target_ids=EVENT_TAG_IDS,
            target_distance=APRILTAG_TARGET_DISTANCE,
            search_timeout=APRILTAG_SEARCH_TIMEOUT,
            nav_timeout=APRILTAG_NAV_TIMEOUT,
            callback=callback,
            # The automation loop calls this regularly. Back/Start will stop
            # the automation and drop back into the gamepad loop below.
            cancel_callback=lambda: automation_cancel_requested(board),
        )
        print("AprilTag automation finished: %s" % result['reason'])
    except Exception as exc:
        print("AprilTag automation error: %s" % exc)
    finally:
        nav.cleanup()
        stop_drive(board)
        print("Returned to gamepad control")


def run_line_following(board):
    """Run line following, then return to gamepad control."""
    print("Line following automation...")
    print("  Press Back to cancel and return to gamepad control.")
    stop_drive(board)

    # Reuse the already-open board object so line following sends motor commands
    # through the same hardware connection as manual gamepad driving.
    follower = LineFollower(board=board)

    def callback(detection, strafe, turn):
        print("  line err=%+d, heading=%+d, strafe=%+.1f, turn=%+.1f" % (
            detection['error'], detection['heading_error'], strafe, turn))

    try:
        result = follower.follow(
            timeout=LINE_FOLLOW_TIMEOUT,
            callback=callback,
            # Back/Start can cancel line following without exiting the whole
            # gamepad program.
            cancel_callback=lambda: automation_cancel_requested(board),
        )
        print("Line following finished: %s" % result['reason'])
    except Exception as exc:
        print("Line following error: %s" % exc)
    finally:
        follower.cleanup()
        stop_drive(board)
        print("Returned to gamepad control")


# === MAIN ===

def main():
    print("=" * 50)
    print("GAMEPAD REMOTE CONTROL")
    print("=" * 50)
    print()
    print("Initializing robot hardware...")
    board = get_board()
    arm = None

    print("Initializing gamepad...")
    pygame.init()
    pygame.joystick.init()

    try:
        gamepad = wait_for_gamepad(board)
    except KeyboardInterrupt:
        print("\nStopped while waiting for gamepad")
        pygame.quit()
        return

    print("Gamepad: %s" % gamepad.get_name())

    arm = Arm(board)
    arm.look_forward()

    print()
    print("Controls:")
    print("  Left stick Y: Left wheels")
    print("  Right stick Y: Right wheels")
    print("  Either X axis: Strafe all wheels")
    print("  Triggers:   Forward/backward (analog)")
    print("  Bumpers:    Turn in place")
    print("  D-pad Up:   Pickup block (front)")
    print("  D-pad Down: Drop into rear bin")
    print("  D-pad Left: AprilTag navigation")
    print("  D-pad Right: Line following")
    print("  A:         Look forward")
    print("  B:         Open claw")
    print("  X/Y:       Shake no / nod yes")
    print("  Back:       STOP  |  Start: Quit")
    print()
    print("Ready -- drive!")
    print()

    running = True
    clock = pygame.time.Clock()

    try:
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Button presses
                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button

                    # Back = emergency stop
                    if button == 6:
                        stop_drive(board)
                        print("STOP!")

                    # Start = quit
                    elif button == 7:
                        print("Quit")
                        running = False

                    # A = look forward (reset arm)
                    elif button == 0:
                        print("Look forward")
                        arm.look_forward()

                    # B = open claw
                    elif button == 1:
                        print("Open claw")
                        arm.gripper_open()

                    # Y = nod yes
                    elif button == 3:
                        print("Yes!")
                        arm.say_yes()

                    # X = shake no
                    elif button == 2:
                        print("No!")
                        arm.say_no()

                # D-pad
                elif event.type == pygame.JOYHATMOTION:
                    hat = event.value

                    # D-pad Up = front pickup
                    if hat == (0, 1):
                        print("Front pickup sequence...")
                        stop_drive(board)
                        arm.pickup_front()

                    # D-pad Down = backward drop into bin
                    elif hat == (0, -1):
                        print("Backward drop sequence...")
                        stop_drive(board)
                        arm.backward_drop()

                    # D-pad Left = AprilTag navigation automation
                    elif hat == (-1, 0):
                        # This blocks manual driving until navigation finishes
                        # or is cancelled, then returns to this same loop.
                        run_apriltag_navigation(board)

                    # D-pad Right = line following automation
                    elif hat == (1, 0):
                        # This blocks manual driving until line following
                        # finishes or is cancelled, then returns to this loop.
                        run_line_following(board)

            # --- Continuous control (sticks + triggers) ---

            # Stick Y controls each side. Stick X controls strafe for all wheels.
            left_x = apply_deadzone(axis_value(gamepad, LEFT_X_AXIS))
            left_y = apply_deadzone(axis_value(gamepad, LEFT_Y_AXIS))
            right_x = apply_deadzone(axis_value(gamepad, RIGHT_X_AXIS))
            right_y = apply_deadzone(axis_value(gamepad, RIGHT_Y_AXIS))

            # F710 XInput trigger axes: left trigger = 2, right trigger = 5.
            # Some systems report released as -1; others report 0.
            left_trigger = trigger_value(gamepad, LEFT_TRIGGER_AXIS)
            right_trigger = trigger_value(gamepad, RIGHT_TRIGGER_AXIS)

            # Bumpers
            left_bumper = gamepad.get_button(4)
            right_bumper = gamepad.get_button(5)

            # Calculate motor speeds
            if left_bumper:
                # Turn left in place
                fl = -TURN_SPEED
                fr = TURN_SPEED
                rl = -TURN_SPEED
                rr = TURN_SPEED
            elif right_bumper:
                # Turn right in place
                fl = TURN_SPEED
                fr = -TURN_SPEED
                rl = TURN_SPEED
                rr = -TURN_SPEED
            elif right_trigger > 0.1:
                # Trigger forward (overrides sticks)
                speed = right_trigger * MAX_SPEED
                fl = fr = rl = rr = speed
            elif left_trigger > 0.1:
                # Trigger backward
                speed = left_trigger * MAX_SPEED
                fl = fr = rl = rr = -speed
            else:
                # Tank drive from stick Y; strafe all wheels from either stick X.
                left_speed = -left_y * MAX_SPEED
                right_speed = -right_y * MAX_SPEED
                strafe = combined_strafe(left_x, right_x) * MAX_SPEED

                fl = left_speed + strafe
                rl = left_speed - strafe
                fr = right_speed - strafe
                rr = right_speed + strafe

            # Clamp and send
            fl = int(clamp(fl, -MAX_SPEED, MAX_SPEED))
            fr = int(clamp(fr, -MAX_SPEED, MAX_SPEED))
            rl = int(clamp(rl, -MAX_SPEED, MAX_SPEED))
            rr = int(clamp(rr, -MAX_SPEED, MAX_SPEED))

            board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])

            clock.tick(POLL_RATE)

    except KeyboardInterrupt:
        print("\nStopped")

    finally:
        stop_drive(board)
        if arm is not None:
            arm.look_forward()
        pygame.quit()
        print("Motors stopped, gamepad released")


if __name__ == '__main__':
    main()
