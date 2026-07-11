#!/usr/bin/env python3
"""
Check individual arm servo wiring.

Run from the repository root:
    python3 scripts/tools/check_servos.py
"""

import os
import sys
import time

# Add the repository root so this tool can import lib/ when run from anywhere.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from lib.board import get_board


# Each row is (servo number, name, first position, second position, return position).
# The small two-position movement makes it clear which joint is plugged into each port.
SERVOS = [
    (1, "gripper", 2500, 1550, 2500),
    (6, "base rotation", 1300, 1700, 1500),
    (3, "wrist", 590, 900, 590),
    (4, "elbow", 2450, 2200, 2450),
    (5, "shoulder", 700, 1000, 700),
]


def stop_all_motors(board):
    """Stop all drive motors in case anything unexpected happens."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def main():
    print("Pathfinder2026 Arm Servo Wiring Check")
    print("-" * 40)
    print("Keep hands clear of the arm and gripper.")
    print("Servo 2 is not used on this robot.")
    print()

    board = get_board()
    time.sleep(0.5)
    # This is a servo test, but stop the drive motors before moving the arm.
    stop_all_motors(board)

    try:
        for servo_id, name, pos1, pos2, home in SERVOS:
            input("Press Enter to test servo %d (%s)." % (servo_id, name))
            print("Servo %d (%s): %d -> %d -> %d" % (servo_id, name, pos1, pos2, home))
            # Move out, move back, then return to the known safe position.
            board.set_servo_position(700, [(servo_id, pos1)])
            time.sleep(1.0)
            board.set_servo_position(700, [(servo_id, pos2)])
            time.sleep(1.0)
            board.set_servo_position(700, [(servo_id, home)])
            time.sleep(1.0)

        print()
        print("Expected mapping:")
        print("  Servo 1: gripper")
        print("  Servo 3: wrist")
        print("  Servo 4: elbow")
        print("  Servo 5: shoulder")
        print("  Servo 6: base rotation")
        print()
        print("If a drive motor moved during this test, stop and ask a facilitator to check the board connection and software image.")
        print("If the wrong arm joint moved, or a servo did not move, go back to B1: robot Assembly Guide and check the arm and servo wiring before changing code.")

    finally:
        # If the user presses Ctrl+C, make sure the drive motors are still off.
        stop_all_motors(board)


if __name__ == "__main__":
    main()
