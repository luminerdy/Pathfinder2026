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
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import cv2

from lib.board import get_board
from skills.block_detect import BlockDetector


VALID_COLORS = ('red', 'blue', 'yellow')
DEFAULT_COLOR = 'blue'
FRAME_W = 640
FRAME_H = 480
PICKUP_CHECK_X_MIN = 120
PICKUP_CHECK_X_MAX = 520
PICKUP_CHECK_Y_MIN = 345
PICKUP_CHECK_MIN_PIXELS = 250
PICKUP_CHECK_MIN_CONTOUR_AREA = 80
PICKUP_ARM_MOVE_MS = 1200
MAX_PICKUP_DRIVE_POWER = 40
MAX_PICKUP_DRIVE_SECONDS = 0.60


def stop_drive_motors(board):
    """Stop all four drive motors before moving the arm."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def clamp(value, minimum, maximum):
    """Keep calibration values inside a conservative test range."""
    return max(minimum, min(maximum, value))


def drive_forward_while_arm_moves(board, power, seconds, total_seconds):
    """
    Move forward briefly while the arm lowers into pickup position.

    The block approach code stops with the cube centered and visible, but the
    claw may still be a few inches behind it. This synchronized nudge lets the
    robot keep moving into the block while the camera/arm moves into pickup pose.
    """
    power = int(clamp(power, 0, MAX_PICKUP_DRIVE_POWER))
    seconds = clamp(seconds, 0.0, MAX_PICKUP_DRIVE_SECONDS)
    if power <= 0 or seconds <= 0:
        time.sleep(total_seconds)
        return

    print("Driving forward during arm drop at %d%% for %.2fs..." % (power, seconds))
    try:
        board.set_motor_duty([
            (1, power),
            (2, power),
            (3, power),
            (4, power),
        ])
        time.sleep(seconds)
    finally:
        stop_drive_motors(board)
        remaining = max(0.0, total_seconds - seconds)
        time.sleep(remaining)


def block_visible_under_claw(color):
    """
    Check for target-color pixels in the lower center of the camera frame.

    At the pickup pose, the cube may be partly hidden by the claw and may touch
    the bottom image edge. The normal full-block detector is too strict there,
    so this check only asks whether enough of the target color is still visible
    in the pickup zone.
    """
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    time.sleep(0.3)

    try:
        frame = None
        for _ in range(3):
            ok, frame = camera.read()
            if ok:
                time.sleep(0.05)

        if frame is None:
            return {
                'visible': False,
                'reason': 'camera_failed',
                'pixels': 0,
                'largest_area': 0,
            }

        detector = BlockDetector(colors=[color])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = detector._create_mask(hsv, color)
        roi = mask[PICKUP_CHECK_Y_MIN:FRAME_H, PICKUP_CHECK_X_MIN:PICKUP_CHECK_X_MAX]
        pixels = int(cv2.countNonZero(roi))
        contours, _ = cv2.findContours(
            roi,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        largest_area = int(max([cv2.contourArea(c) for c in contours] or [0]))
        visible = (
            pixels >= PICKUP_CHECK_MIN_PIXELS
            and largest_area >= PICKUP_CHECK_MIN_CONTOUR_AREA
        )

        return {
            'visible': visible,
            'reason': 'visible' if visible else 'not_visible',
            'pixels': pixels,
            'largest_area': largest_area,
        }

    finally:
        camera.release()


def run_pickup_sequence(
    board=None,
    color=DEFAULT_COLOR,
    verify_before_grab=False,
    drive_during_arm=False,
    drive_power=0,
    drive_seconds=0.0,
):
    """
    Run the tested front pickup arm sequence.

    The robot must already be stopped with one block directly in front of the
    claw. This function does not drive the robot.
    """
    board = board or get_board()
    stop_drive_motors(board)

    print("Running front pickup sequence...")

    # Open first so the claw can fit around the block.
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(0.6)

    # Move the arm to the tested right-in-front pickup pose.
    # Servo 1 is intentionally not included here; it closes last.
    board.set_servo_position(PICKUP_ARM_MOVE_MS, [
        (6, 1500),
        (5, 2120),
        (4, 2500),
        (3, 940),
    ])
    if drive_during_arm:
        drive_forward_while_arm_moves(
            board,
            drive_power,
            drive_seconds,
            PICKUP_ARM_MOVE_MS / 1000.0 + 0.1,
        )
    else:
        time.sleep(PICKUP_ARM_MOVE_MS / 1000.0 + 0.1)

    if verify_before_grab:
        check = block_visible_under_claw(color)
        print(
            "Pickup camera check: %s pixels=%d largest=%d" % (
                check['reason'],
                check['pixels'],
                check['largest_area'],
            )
        )
        if not check['visible']:
            stop_drive_motors(board)
            return {
                'success': False,
                'reason': 'block_not_visible_under_claw',
                'camera_check': check,
            }

    # Close on the block after the arm is in position and the check passes.
    board.set_servo_position(500, [(1, 1680)])
    time.sleep(0.6)

    # Lift and return the arm while keeping the claw at the tested grip.
    board.set_servo_position(1000, [(5, 1841)])
    time.sleep(1.1)
    board.set_servo_position(1200, [
        (3, 700),
        (4, 2425),
        (5, 790),
        (6, 1500),
    ])
    time.sleep(1.3)
    stop_drive_motors(board)

    return {
        'success': True,
        'reason': 'pickup_complete',
    }


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description='Run pickup-only arm demo.')
    parser.add_argument(
        '--color',
        choices=VALID_COLORS,
        default=DEFAULT_COLOR,
        help='Block color to confirm before grabbing. Default: %(default)s',
    )
    parser.add_argument(
        '--check-camera',
        action='store_true',
        help='Stop before closing the claw if the target color is not visible.',
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Run without the safety confirmation prompt.',
    )
    parser.add_argument(
        '--drive-during-arm',
        action='store_true',
        help='Calibration only: drive forward while lowering the arm.',
    )
    parser.add_argument(
        '--drive-power',
        type=int,
        default=24,
        help='Calibration drive power percent. Default: %(default)s',
    )
    parser.add_argument(
        '--drive-seconds',
        type=float,
        default=0.45,
        help='Calibration drive time while lowering the arm. Default: %(default)s',
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
        result = run_pickup_sequence(
            board,
            color=args.color,
            verify_before_grab=args.check_camera,
            drive_during_arm=args.drive_during_arm,
            drive_power=args.drive_power,
            drive_seconds=args.drive_seconds,
        )
        print()
        print("Result: %s" % ("COMPLETE" if result['success'] else "STOPPED"))
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
