#!/usr/bin/env python3
"""
Robotic Arm Demo: Pick Up A Block And Load It Onto The Back

This is the C3 arm capability demo. It is based on the original
PathfinderBot arm pickup movement sequence.

Place the robot on the floor and put one block directly in front of
the gripper before starting.

Servo mapping:
  Servo 1: Gripper/Claw  (1455=closed, 2500=open)
  Servo 3: Wrist         (500-2500)
  Servo 4: Elbow         (500-2500)
  Servo 5: Shoulder      (500-2500)
  Servo 6: Base          (500-2500, 1500=center)
  Note: Servo 2 does not exist on this platform.

Usage:
    python3 skills/robotic_arm/run_demo.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from lib.board import get_board


READY_POSITION = [
    (1, 1500),  # Gripper partly open
    (3, 590),   # Wrist forward
    (4, 2500),  # Elbow forward
    (5, 700),   # Shoulder raised
    (6, 1500),  # Base center
]


PICKUP_AND_LOAD_STEPS = [
    ("Move to ready position", 2000, READY_POSITION, 0.3),
    ("Lower shoulder toward block", 1000, [(5, 1818)], 1.0),
    ("Position elbow and shoulder for pickup", 300, [(4, 2023), (5, 2091)], 0.3),
    ("Open gripper near block", 500, [(1, 2400)], 1.0),
    ("Open gripper fully", 500, [(1, 2500)], 0.3),
    ("Reach to block", 800, [(3, 750), (4, 2150), (5, 2364)], 0.8),
    ("Close gripper on block", 300, [(1, 1455), (5, 2318)], 0.3),
    ("Lift block", 1000, [(5, 1841)], 1.0),
    ("Move block over rear storage area", 2000, [(1, 1500), (3, 2500), (4, 500), (5, 1636)], 2.0),
    ("Release block onto back", 2000, [(1, 2000)], 1.5),
    ("Return to ready position", 2000, READY_POSITION, 0.3),
]


def stop_all_motors(board):
    """Stop drive motors in case anything unexpected is active."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def move_arm(board, label, duration_ms, servos, pause_seconds):
    """Run one labeled arm movement step."""
    print("  %s" % label)
    board.set_servo_position(duration_ms, servos)
    time.sleep(duration_ms / 1000.0 + pause_seconds)


def return_to_ready(board):
    """Return arm to the ready position."""
    try:
        board.set_servo_position(2000, READY_POSITION)
        time.sleep(2.2)
    except Exception:
        pass


def main():
    print("=" * 60)
    print("ROBOTIC ARM PICKUP DEMO")
    print("=" * 60)
    print()
    print("This demo picks up one block and loads it onto the robot's back.")
    print("Place the robot on the floor and put one block directly in front of the gripper.")
    print("Keep hands clear of the arm and gripper.")
    print("Press Ctrl+C to stop.")
    print("-" * 60)
    print()

    input("Press Enter when the block is in place and the arm area is clear...")

    board = get_board()
    stop_all_motors(board)

    try:
        for label, duration_ms, servos, pause_seconds in PICKUP_AND_LOAD_STEPS:
            move_arm(board, label, duration_ms, servos, pause_seconds)

        print()
        print("=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print()
        print("What you checked:")
        print("  [OK] Gripper opened and closed")
        print("  [OK] Wrist, elbow, and shoulder moved together")
        print("  [OK] Arm lifted and loaded the block onto the back")

    except KeyboardInterrupt:
        print("\nDemo stopped by user (Ctrl+C)")

    except Exception as e:
        print("\nERROR: %s" % e)
        import traceback
        traceback.print_exc()

    finally:
        print("\nReturning arm to ready position...")
        return_to_ready(board)
        stop_all_motors(board)
        print("Done.")


if __name__ == "__main__":
    main()
