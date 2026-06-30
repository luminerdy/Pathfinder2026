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

sys.path.insert(0, "/home/robot/pathfinder")

from lib.board import get_board


POWER = 35
MOVE_SECONDS = 1.0


def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def forward(board, power, seconds):
    board.set_motor_duty([(1, power), (2, power), (3, power), (4, power)])
    time.sleep(seconds)
    stop(board)


def turn_clockwise(board, power, seconds):
    board.set_motor_duty([(1, power), (2, -power), (3, power), (4, -power)])
    time.sleep(seconds)
    stop(board)


def main():
    print("Team Drive Practice")
    print("Put the robot on the floor and clear the area.")
    input("Press Enter to move forward...")

    board = get_board()

    try:
        forward(board, POWER, MOVE_SECONDS)
        time.sleep(0.5)

        input("Press Enter to turn clockwise...")
        turn_clockwise(board, 40, 0.8)

    finally:
        stop(board)
        print("Motors stopped.")


if __name__ == "__main__":
    main()
