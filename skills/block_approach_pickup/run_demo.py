#!/usr/bin/env python3
"""
Approach and pickup block demo.

This experimental script combines the calibrated approach-only demo with the
pickup-only arm sequence. Keep this out of the participant event flow until it
is repeatable across colors, batteries, and starting distances.
"""

import argparse
import importlib.util
import os
import sys

SCRIPT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../..'))
sys.path.insert(0, REPO_ROOT)


def load_module(module_name, relative_path):
    """Load a helper module by file path to avoid legacy module name conflicts."""
    module_path = os.path.join(REPO_ROOT, relative_path)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


approach_module = load_module(
    'pathfinder_block_approach_demo',
    os.path.join('skills', 'block_approach', 'run_demo.py'),
)
pickup_module = load_module(
    'pathfinder_block_pickup_demo',
    os.path.join('skills', 'block_pickup', 'run_demo.py'),
)

DEFAULT_COLOR = approach_module.DEFAULT_COLOR
MAX_RUNTIME_SECONDS = approach_module.MAX_RUNTIME_SECONDS
VALID_COLORS = approach_module.VALID_COLORS
BlockApproachDemo = approach_module.BlockApproachDemo
run_pickup_sequence = pickup_module.run_pickup_sequence

SETTLE_FORWARD_POWER = 24
SETTLE_FORWARD_SECONDS = 0.28
MAX_SETTLE_POWER = 45
MAX_SETTLE_SECONDS = 0.60


def stop_drive_motors(board):
    """Stop all four drive motors."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def clamp_settle(value, minimum, maximum):
    """Keep command-line settle tuning inside a safe test range."""
    return max(minimum, min(maximum, value))


def settle_forward(board, power, seconds):
    """
    Move forward a tiny amount after vision handoff.

    The approach handoff leaves the block centered and close, but photos showed
    the block can still sit just forward of the claw. This small nudge moves
    the robot into the tested pickup geometry before the arm sequence starts.
    """
    power = int(clamp_settle(power, 0, MAX_SETTLE_POWER))
    seconds = clamp_settle(seconds, 0.0, MAX_SETTLE_SECONDS)

    print("Settling forward at %d%% for %.2fs..." % (power, seconds))
    try:
        board.set_motor_duty([
            (1, power),
            (2, power),
            (3, power),
            (4, power),
        ])
        import time
        time.sleep(seconds)
    finally:
        stop_drive_motors(board)
        print("Settle complete. Drive motors stopped.")


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
    parser.add_argument(
        '--no-settle',
        action='store_true',
        help='Skip the tiny forward settle before pickup.',
    )
    parser.add_argument(
        '--settle-power',
        type=int,
        default=SETTLE_FORWARD_POWER,
        help='Forward settle motor power percent. Default: %(default)s',
    )
    parser.add_argument(
        '--settle-seconds',
        type=float,
        default=SETTLE_FORWARD_SECONDS,
        help='Forward settle time in seconds. Default: %(default)s',
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
    print("Approach reached handoff.")
    if not args.no_settle:
        settle_forward(approach.board, args.settle_power, args.settle_seconds)
    else:
        print("Forward settle skipped.")

    print("Starting pickup sequence...")
    pickup_result = run_pickup_sequence(approach.board)

    print()
    print("Pickup result: %s" % (
        "SUCCESS" if pickup_result.get('success') else "STOPPED"
    ))
    print("Pickup reason: %s" % pickup_result.get('reason'))
    print("Check whether the block is held in the claw.")


if __name__ == '__main__':
    main()
