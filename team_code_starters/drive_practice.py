#!/usr/bin/env python3
"""
Team drive practice.

Run from the robot:
    cd /home/robot/team_code
    python3 drive_practice.py

Safety:
    - Put the robot on the floor.
    - Clear a 4-foot by 4-foot area.
    - Press Ctrl+C to stop.
"""

import sys
import time

# The shared robot library lives in /home/robot/pathfinder.
# This lets a copied starter file in /home/robot/team_code still import it.
sys.path.insert(0, "/home/robot/pathfinder")

from lib.board import get_board


# Try changing these two values first when experimenting.
# Power is motor duty from -100 to 100. Start low and increase slowly.
POWER = 35
MOVE_SECONDS = 1.0


def stop(board):
    """Set every drive motor to zero power."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def forward(board, power, seconds):
    """Move straight forward, then stop."""
    # Motors 1/3 are the left side and 2/4 are the right side.
    # Positive power should move each wheel forward.
    board.set_motor_duty([(1, power), (2, power), (3, power), (4, power)])
    time.sleep(seconds)
    stop(board)


def turn_clockwise(board, power, seconds):
    """Turn in place clockwise, then stop."""
    # Clockwise means left wheels forward and right wheels backward.
    board.set_motor_duty([(1, power), (2, -power), (3, power), (4, -power)])
    time.sleep(seconds)
    stop(board)


def main():
    print("Team Drive Practice")
    print("Put the robot on the floor and clear the area.")
    input("Press Enter to move forward...")

    board = get_board()

    try:
        # Run one simple movement at a time so students can observe the result.
        forward(board, POWER, MOVE_SECONDS)
        time.sleep(0.5)

        input("Press Enter to turn clockwise...")
        turn_clockwise(board, 40, 0.8)

    finally:
        # Always stop the motors, even if Ctrl+C or an error interrupts the script.
        stop(board)
        print("Motors stopped.")


if __name__ == "__main__":
    main()
