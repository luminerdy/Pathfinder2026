#!/usr/bin/env python3
"""
Approach and pickup block demo.

This experimental script combines the calibrated approach-only demo with the
pickup-only arm sequence. Keep this out of the participant event flow until it
is repeatable across colors, batteries, and starting distances.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.block_approach.run_demo import (
    DEFAULT_COLOR,
    MAX_RUNTIME_SECONDS,
    VALID_COLORS,
    BlockApproachDemo,
)
from skills.block_pickup.run_demo import run_pickup_sequence


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description='Approach and pick up one block.')
    parser.add_argument(
        '--color',
        choices=VALID_COLORS,
        default=DEFAULT_COLOR,
        help='Block color to approach and pick up. Default: %(default)s',
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=MAX_RUNTIME_SECONDS,
        help='Maximum approach runtime in seconds. Default: %(default)s',
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Run without the safety confirmation prompt.',
    )
    return parser.parse_args()


def main():
    """Run approach, then pickup only if approach succeeds."""
    args = parse_args()

    print("=" * 60)
    print("BLOCK APPROACH AND PICKUP DEMO")
    print("=" * 60)
    print("Color: %s" % args.color)
    print("This demo drives the robot, then moves the arm.")
    print("Put the robot on the floor with clear space around it.")
    print("Keep hands clear of the robot, arm, and claw.")
    print()

    if not args.yes:
        input("Press Enter when the robot area is clear and the block is visible...")

    approach = BlockApproachDemo(color=args.color)
    approach_result = approach.run(timeout=args.timeout)

    print()
    print("Approach result: %s" % (
        "SUCCESS" if approach_result.get('success') else "STOPPED"
    ))
    print("Approach reason: %s" % approach_result.get('reason'))

    if not approach_result.get('success'):
        print("Pickup skipped because approach did not reach the handoff point.")
        return

    print()
    print("Approach reached handoff. Starting pickup sequence...")
    pickup_result = run_pickup_sequence(approach.board)

    print()
    print("Pickup result: %s" % (
        "SUCCESS" if pickup_result.get('success') else "STOPPED"
    ))
    print("Pickup reason: %s" % pickup_result.get('reason'))
    print("Check whether the block is held in the claw.")


if __name__ == '__main__':
    main()
