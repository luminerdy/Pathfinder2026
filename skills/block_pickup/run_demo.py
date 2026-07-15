#!/usr/bin/env python3
"""
Pickup-only block demo.

The robot must already be stopped with one block directly in front of the claw.
This script does not drive the robot. It runs the tested front pickup sequence
from lib.arm_positions so pickup can be tuned separately from approach.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.arm_positions import Arm
from lib.board import get_board


def stop_drive_motors(board):
    """Stop all four drive motors before moving the arm."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def run_pickup_sequence(board=None):
    """
    Run the tested front pickup arm sequence.

    The robot must already be stopped with one block directly in front of the
    claw. This function does not drive the robot.
    """
    board = board or get_board()
    stop_drive_motors(board)

    arm = Arm(board)
    print("Running front pickup sequence...")
    arm.pickup_front()
    stop_drive_motors(board)

    return {
        'success': True,
        'reason': 'pickup_complete',
    }


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description='Run pickup-only arm demo.')
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Run without the safety confirmation prompt.',
    )
    return parser.parse_args()


def main():
    """Run the pickup-only test."""
    args = parse_args()

    print("=" * 60)
    print("BLOCK PICKUP DEMO")
    print("=" * 60)
    print("This demo moves the arm only. It does not drive the robot.")
    print("The robot must already be stopped with one block directly in front of the claw.")
    print("Keep hands clear of the arm and claw.")
    print()

    if not args.yes:
        input("Press Enter when the block is in place and the arm area is clear...")

    board = get_board()

    try:
        result = run_pickup_sequence(board)
        print()
        print("Result: COMPLETE")
        print("Reason: %s" % result['reason'])
        print("Check whether the block is held in the claw before combining this with approach.")

    except KeyboardInterrupt:
        print()
        print("Stopped by user. Drive motors stopped.")

    except Exception as exc:
        print()
        print("ERROR: %s" % exc)
        raise

    finally:
        stop_drive_motors(board)
        print("Drive motors stopped.")


if __name__ == '__main__':
    main()
