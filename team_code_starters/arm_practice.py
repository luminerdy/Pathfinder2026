#!/usr/bin/env python3
"""
Team arm practice.

Run from the robot:
    cd /home/robot/team_code
    python3 arm_practice.py

Keep hands clear of the arm and gripper.
"""

import sys
import time

sys.path.insert(0, "/home/robot/pathfinder")

from lib.board import get_board


GRIPPER_OPEN = 2500
GRIPPER_CLOSED = 1455

READY_POSITION = [
    (1, 1500),  # Gripper partly open
    (3, 590),   # Wrist
    (4, 2500),  # Elbow
    (5, 700),   # Shoulder
    (6, 1500),  # Base center
]


def move_servos(board, duration_ms, positions):
    board.set_servo_position(duration_ms, positions)
    time.sleep(duration_ms / 1000.0 + 0.2)


def main():
    print("Team Arm Practice")
    print("Keep hands clear of the arm and gripper.")
    input("Press Enter to move the arm to ready position...")

    board = get_board()

    move_servos(board, 1500, READY_POSITION)

    input("Press Enter to open the gripper...")
    move_servos(board, 700, [(1, GRIPPER_OPEN)])

    input("Press Enter to close the gripper...")
    move_servos(board, 700, [(1, GRIPPER_CLOSED)])

    print("Done.")


if __name__ == "__main__":
    main()
