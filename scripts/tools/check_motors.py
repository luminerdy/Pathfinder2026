#!/usr/bin/env python3
"""
Check individual drive motor wiring.

Run from the repository root:
    python3 scripts/tools/check_motors.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from lib.board import get_board


MOTORS = [
    (1, "front left"),
    (2, "front right"),
    (3, "rear left"),
    (4, "rear right"),
]


def stop_all(board):
    """Stop all drive motors."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def main():
    print("Pathfinder2026 Motor Wiring Check")
    print("-" * 40)
    print("Put the robot on the floor, not on a table.")
    print("Clear a 4-foot by 4-foot area.")
    print("Each motor will run for 0.5 seconds.")
    print()

    board = get_board()
    time.sleep(0.5)

    try:
        for motor_id, name in MOTORS:
            input("Press Enter to test motor %d (%s)." % (motor_id, name))
            print("Motor %d (%s): running forward briefly" % (motor_id, name))
            board.set_motor_duty([(motor_id, 40)])
            time.sleep(0.5)
            board.set_motor_duty([(motor_id, 0)])
            time.sleep(0.5)

        print()
        print("Expected mapping:")
        for motor_id, name in MOTORS:
            print("  Motor %d: %s wheel" % (motor_id, name))
        print()
        print("If the wrong wheel moved, check the motor cable port.")
        print("If a wheel did not move or spun backward, ask a facilitator.")

    finally:
        stop_all(board)


if __name__ == "__main__":
    main()
