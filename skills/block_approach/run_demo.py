#!/usr/bin/env python3
"""
Approach-only block demo.

This script uses block detection and target selection to approach one selected
block color. It does not grab the block and it does not move the arm.

Safety design:
  - Battery must be safe before motors run.
  - Target must be stable for several frames before movement.
  - Movement happens in short pulses, then motors stop and camera checks again.
  - Ctrl+C and all errors stop the motors.
"""

import argparse
import os
import sys
import time

import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import PLATFORM, get_board
from lib.battery import is_runtime_safe, read_voltage, status_for_voltage
from skills.block_detect import BlockDetector


FRAME_W = 640
FRAME_H = 480
CENTER_X = FRAME_W // 2

DEFAULT_COLOR = 'blue'
VALID_COLORS = ('red', 'blue', 'yellow')

MAX_RUNTIME_SECONDS = 20.0
STABLE_FRAMES_REQUIRED = 4
STABLE_CENTER_SHIFT_PX = 45

STOP_DISTANCE_CM = 24.0
STOP_Y_MIN = 330
X_TOLERANCE_PX = 45

FORWARD_POWER = 30
STRAFE_POWER = 32
MOVE_PULSE_SECONDS = 0.18
LOOK_PAUSE_SECONDS = 0.12


class BlockApproachDemo:
    """Approach a selected block target without pickup."""

    def __init__(self, color=DEFAULT_COLOR):
        self.color = color
        self.board = get_board()
        self.detector = BlockDetector()
        self.camera = None
        self.last_target = None
        self.stable_count = 0

    def open_camera(self):
        """Open the USB camera."""
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
            time.sleep(1.0)

    def close_camera(self):
        """Release the USB camera."""
        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
            self.camera = None

    def stop(self):
        """Stop all four drive motors."""
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

    def set_motors(self, front_left, front_right, rear_left, rear_right):
        """Set motors using the same logical numbering as the drive demos."""
        self.board.set_motor_duty([
            (1, int(front_left)),
            (2, int(front_right)),
            (3, int(rear_left)),
            (4, int(rear_right)),
        ])

    def drive_pulse(self, vx=0, vy=0):
        """
        Drive briefly, then stop.

        vx: sideways speed, positive = strafe right
        vy: forward speed, positive = forward
        """
        front_left = vy + vx
        front_right = vy - vx
        rear_left = vy - vx
        rear_right = vy + vx

        self.set_motors(front_left, front_right, rear_left, rear_right)
        time.sleep(MOVE_PULSE_SECONDS)
        self.stop()
        time.sleep(LOOK_PAUSE_SECONDS)

    def check_battery(self):
        """Return True when battery is safe for motor movement."""
        voltage = read_voltage(self.board)
        status, message, safe = status_for_voltage(voltage, PLATFORM)

        print("Battery: %s" % ("%.2fV" % voltage if voltage is not None else "unknown"))
        print("Status: %s - %s" % (status, message))
        if not is_runtime_safe(voltage, PLATFORM):
            print("Stop: battery is not safe for motor operation.")
            return False
        return True

    def read_target(self):
        """Read one frame and return the selected pickup target."""
        ok, frame = self.camera.read()
        if not ok:
            return None, 0, 0

        raw_blocks = self.detector.detect(frame, colors=[self.color])
        blocks = self.detector.merge_close_detections(raw_blocks)
        target = self.detector.select_pickup_target(
            blocks,
            frame_width=FRAME_W,
            frame_height=FRAME_H,
        )
        return target, len(raw_blocks), len(blocks)

    def target_is_stable(self, target):
        """Require the selected target to stay in about the same place."""
        if target is None:
            self.last_target = None
            self.stable_count = 0
            return False

        if self.last_target is None:
            self.last_target = target
            self.stable_count = 1
            return False

        dx = target.center_x - self.last_target.center_x
        dy = target.center_y - self.last_target.center_y
        close_enough = (dx * dx + dy * dy) ** 0.5 <= STABLE_CENTER_SHIFT_PX

        self.last_target = target
        if close_enough:
            self.stable_count += 1
        else:
            self.stable_count = 1

        return self.stable_count >= STABLE_FRAMES_REQUIRED

    def choose_action(self, target):
        """Return the next safe movement action for a stable target."""
        offset = target.offset_from_center
        distance_cm = target.estimated_distance_mm / 10.0

        if (
            distance_cm <= STOP_DISTANCE_CM
            or target.center_y >= STOP_Y_MIN
        ) and abs(offset) <= X_TOLERANCE_PX:
            return 'reached', 0, 0

        if abs(offset) > X_TOLERANCE_PX:
            if offset > 0:
                return 'strafe right', STRAFE_POWER, 0
            return 'strafe left', -STRAFE_POWER, 0

        return 'forward', 0, FORWARD_POWER

    def run(self, timeout=MAX_RUNTIME_SECONDS):
        """Run the approach-only demo."""
        if not self.check_battery():
            return {'success': False, 'reason': 'battery_low'}

        self.open_camera()
        start = time.monotonic()
        frames = 0

        print()
        print("Looking for %s block..." % self.color)
        print("Target must be stable for %d frames before movement." %
              STABLE_FRAMES_REQUIRED)
        print("Press Ctrl+C to stop.")
        print("-" * 60)

        try:
            while time.monotonic() - start < timeout:
                frames += 1
                target, raw_count, merged_count = self.read_target()

                if target is None:
                    self.stop()
                    print("No stable %s target found." % self.color)
                    time.sleep(0.25)
                    continue

                stable = self.target_is_stable(target)
                distance_cm = target.estimated_distance_mm / 10.0
                print(
                    "%s target: %.0fcm offset=%+d y=%d score=%.1f "
                    "stable=%d/%d detections=%d/%d" % (
                        target.color,
                        distance_cm,
                        target.offset_from_center,
                        target.center_y,
                        self.detector.pickup_target_score(target),
                        min(self.stable_count, STABLE_FRAMES_REQUIRED),
                        STABLE_FRAMES_REQUIRED,
                        merged_count,
                        raw_count,
                    )
                )

                if not stable:
                    self.stop()
                    time.sleep(0.15)
                    continue

                action, vx, vy = self.choose_action(target)
                if action == 'reached':
                    self.stop()
                    print("Reached approach position. Motors stopped.")
                    return {
                        'success': True,
                        'reason': 'reached',
                        'frames': frames,
                        'distance_cm': round(distance_cm, 1),
                        'offset': target.offset_from_center,
                    }

                print("  Moving: %s" % action)
                self.drive_pulse(vx=vx, vy=vy)

            self.stop()
            print("Timed out. Motors stopped.")
            return {'success': False, 'reason': 'timeout', 'frames': frames}

        except KeyboardInterrupt:
            self.stop()
            print()
            print("Stopped by user. Motors stopped.")
            return {'success': False, 'reason': 'interrupted', 'frames': frames}

        finally:
            self.stop()
            self.close_camera()


def parse_args():
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description='Approach one selected block.')
    parser.add_argument(
        '--color',
        choices=VALID_COLORS,
        default=DEFAULT_COLOR,
        help='Block color to approach. Default: %(default)s',
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=MAX_RUNTIME_SECONDS,
        help='Maximum runtime in seconds. Default: %(default)s',
    )
    return parser.parse_args()


def main():
    """Run the approach-only demo."""
    args = parse_args()

    print("=" * 60)
    print("BLOCK APPROACH DEMO")
    print("=" * 60)
    print("Color: %s" % args.color)
    print("This demo moves the drive base only. It does not grab the block.")
    print("Put the robot on the floor with clear space around it.")
    print()

    demo = BlockApproachDemo(color=args.color)
    result = demo.run(timeout=args.timeout)
    print()
    print("Result: %s" % ("SUCCESS" if result.get('success') else "STOPPED"))
    print("Reason: %s" % result.get('reason'))


if __name__ == '__main__':
    main()
