#!/usr/bin/env python3
"""
Check individual arm servo wiring.

Run from the repository root:
    python3 scripts/tools/check_servos.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from lib.board import get_board


SERVOS = [
    (1, "gripper", 2500, 1475, 2500),
    (6, "base rotation", 1300, 1700, 1500),
    (5, "shoulder", 700, 1000, 700),
    (4, "elbow", 2450, 2200, 2450),
    (3, "wrist", 590, 900, 590),
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
    stop_all_motors(board)

    try:
        for servo_id, name, pos1, pos2, home in SERVOS:
            input("Press Enter to test servo %d (%s)." % (servo_id, name))
            print("Servo %d (%s): %d -> %d -> %d" % (servo_id, name, pos1, pos2, home))
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
        print("If a drive motor moved during this test, stop and ask a facilitator.")

    finally:
        stop_all_motors(board)


if __name__ == "__main__":
    main()
