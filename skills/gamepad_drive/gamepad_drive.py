#!/usr/bin/env python3
"""
Gamepad Remote Control (E2)

Drive robot with Logitech F710 wireless gamepad.
Tank-style sticks + mecanum strafing + trigger speed + arm actions.

Arm sequences ported from PathfinderBot V1 (pf_mecanum_gamepad_drive.py)
with vendor-tested servo positions for reliable pickup/drop.

Prerequisites:
  - F710 USB receiver plugged into robot Pi
  - Gamepad on, back switch set to X (XInput)
  - pygame installed: sudo apt install python3-pygame

Usage:
    python3 gamepad_drive.py

Controls:
  Left stick Y:   Left wheels forward/backward
  Right stick Y:  Right wheels forward/backward
  Both sticks X:  Strafe left/right, each stick controls its own side
  Right trigger:  Forward (analog speed)
  Left trigger:   Backward (analog speed)
  Right bumper:   Turn right in place
  Left bumper:    Turn left in place

  D-pad Up:       Pickup block (front)
  D-pad Down:     Backward drop block (into rear bin)
  D-pad Left:     Left side pickup
  D-pad Right:    Right side pickup

  A:              Look forward (reset arm)
  B:              Look sad
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

# === CONFIG ===
MAX_SPEED = 50          # Maximum motor duty cycle (0-100)
TURN_SPEED = 40         # In-place turn speed
DEADZONE = 0.15         # Ignore stick values below this
POLL_RATE = 50          # Hz (20ms per loop)
LEFT_X_AXIS = 0         # Left stick horizontal
LEFT_Y_AXIS = 1         # Left stick vertical
RIGHT_Y_AXIS = 3        # Right stick vertical on the workshop F710 image
RIGHT_X_AXIS = 4        # Right stick horizontal on the workshop F710 image
LEFT_TRIGGER_AXIS = 2
RIGHT_TRIGGER_AXIS = 5


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
    """Read an analog trigger as 0 released to 1 fully pressed."""
    if axis_index >= gamepad.get_numaxes():
        return 0.0
    return (gamepad.get_axis(axis_index) + 1) / 2


def beep_missing_gamepad(board):
    """Beep so teams know the receiver/gamepad was not detected."""
    try:
        board.set_buzzer(1200, 0.15, 0.1, 3)
    except Exception:
        pass


# === MAIN ===

def main():
    print("=" * 50)
    print("GAMEPAD REMOTE CONTROL (E2)")
    print("=" * 50)
    print()
    print("Initializing robot hardware...")
    board = get_board()
    arm = None

    print("Initializing gamepad...")
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No gamepad detected!")
        beep_missing_gamepad(board)
        print("  - USB receiver plugged into robot Pi?")
        print("  - Gamepad powered on (green LED)?")
        print("  - Back switch set to X (not D)?")
        pygame.quit()
        sys.exit(1)

    gamepad = pygame.joystick.Joystick(0)
    gamepad.init()
    print("Gamepad: %s" % gamepad.get_name())

    arm = Arm(board)
    arm.look_forward()

    print()
    print("Controls:")
    print("  Left stick: Left wheels only")
    print("  Right stick: Right wheels only")
    print("  Both X axes: Strafe")
    print("  Triggers:   Forward/backward (analog)")
    print("  Bumpers:    Turn in place")
    print("  D-pad Up:   Pickup block (front)")
    print("  D-pad Down: Drop into rear bin")
    print("  D-pad Left: Left side pickup")
    print("  D-pad Right:Right side pickup")
    print("  A/B/X/Y:   Arm expressions")
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
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        print("STOP!")

                    # Start = quit
                    elif button == 7:
                        print("Quit")
                        running = False

                    # A = look forward (reset arm)
                    elif button == 0:
                        print("Look forward")
                        arm.look_forward()

                    # B = look sad
                    elif button == 1:
                        print("Sad")
                        arm.look_sad()

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
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.pickup_front()

                    # D-pad Down = backward drop into bin
                    elif hat == (0, -1):
                        print("Backward drop sequence...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.backward_drop()

                    # D-pad Left = left side pickup
                    elif hat == (-1, 0):
                        print("Left side pickup...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.pickup_left()

                    # D-pad Right = right side pickup
                    elif hat == (1, 0):
                        print("Right side pickup...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.pickup_right()

            # --- Continuous control (sticks + triggers) ---

            # Each stick controls only its own side of the robot:
            # left stick -> motors 1 and 3, right stick -> motors 2 and 4.
            left_x = apply_deadzone(axis_value(gamepad, LEFT_X_AXIS))
            left_y = apply_deadzone(axis_value(gamepad, LEFT_Y_AXIS))
            right_x = apply_deadzone(axis_value(gamepad, RIGHT_X_AXIS))
            right_y = apply_deadzone(axis_value(gamepad, RIGHT_Y_AXIS))

            # Triggers (axis 2 = left trigger, axis 5 = right trigger on F710)
            # Triggers range: -1 (released) to +1 (fully pressed)
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
                # Tank + strafe from sticks. Each stick only affects its side.
                left_speed = -left_y * MAX_SPEED
                right_speed = -right_y * MAX_SPEED
                left_strafe = left_x * MAX_SPEED
                right_strafe = right_x * MAX_SPEED

                fl = left_speed + left_strafe
                rl = left_speed - left_strafe
                fr = right_speed - right_strafe
                rr = right_speed + right_strafe

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
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        if arm is not None:
            arm.look_forward()
        pygame.quit()
        print("Motors stopped, gamepad released")


if __name__ == '__main__':
    main()
