#!/usr/bin/env python3
"""
Approach-only block demo.

This script uses block detection and target selection to approach one selected
block color. It moves the shoulder/camera angle to keep the target visible, but
it does not grab the block.

Safety design:
  - Battery must be safe before motors run.
  - Target must be stable for several frames before movement.
  - Shoulder/camera movement is limited to approach-view positions.
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
LOCK_MATCH_MAX_SHIFT_PX = 90
LOCK_DISTANCE_JUMP_MM = 120
LOCK_Y_DROP_PX = 20
LOST_TARGET_LIMIT = 8
CLOSE_TARGET_LOST_LIMIT = 3
APPROACH_EDGE_MARGIN_PX = 50
APPROACH_MAX_TARGET_DISTANCE_MM = 450
CENTER_PROGRESS_MIN_PX = 8
CENTER_PROGRESS_LIMIT = 10

X_TOLERANCE_PX = 60
PICKUP_X_TOLERANCE_PX = 25

FORWARD_POWER = 30
STRAFE_POWER = 42
FINE_STRAFE_POWER = 34
FORWARD_PULSE_SECONDS = 0.16
STRAFE_PULSE_SECONDS = 0.35
FINE_STRAFE_PULSE_SECONDS = 0.18
LOOK_PAUSE_SECONDS = 0.12

APPROACH_START_S5 = 950
APPROACH_TOUCH_S5 = 1250
APPROACH_MIN_S5 = 850
APPROACH_MAX_S5 = 1250
ARM_STEP = 35
ARM_MOVE_MS = 250
TARGET_VIEW_Y = 300
TARGET_VIEW_TOLERANCE_PX = 45
HANDOFF_S5_MIN = 1200
HANDOFF_DISTANCE_MM = 170
HANDOFF_VIEW_Y_MIN = 300


class BlockApproachDemo:
    """Approach a selected block target without pickup."""

    def __init__(self, color=DEFAULT_COLOR):
        self.color = color
        self.board = get_board()
        self.detector = BlockDetector()
        self.camera = None
        self.last_target = None
        self.locked_target = None
        self.lost_target_frames = 0
        self.best_abs_offset = None
        self.no_center_progress_frames = 0
        self.stable_count = 0
        self.current_s5 = APPROACH_START_S5
        self.pickup_handoff_armed = False

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

        pulse_seconds = self.pulse_duration(vx)

        self.set_motors(front_left, front_right, rear_left, rear_right)
        time.sleep(pulse_seconds)
        self.stop()
        time.sleep(LOOK_PAUSE_SECONDS)

    def pulse_duration(self, vx):
        """Return the calibrated duration for a forward or strafe pulse."""
        if not vx:
            return FORWARD_PULSE_SECONDS
        if abs(vx) <= FINE_STRAFE_POWER:
            return FINE_STRAFE_PULSE_SECONDS
        return STRAFE_PULSE_SECONDS

    def drive_and_tilt_pulse(self, s5, vx=0, vy=0):
        """Drive briefly while the shoulder moves the camera farther down."""
        s5 = int(max(APPROACH_MIN_S5, min(APPROACH_MAX_S5, s5)))
        pulse_seconds = self.pulse_duration(vx)
        servo_seconds = ARM_MOVE_MS / 1000.0

        front_left = vy + vx
        front_right = vy - vx
        rear_left = vy - vx
        rear_right = vy + vx

        # Servo movement continues after this command, so the short drive pulse
        # and camera tilt happen together while the target is still tracked.
        self.board.set_servo_position(ARM_MOVE_MS, [(5, s5)])
        self.current_s5 = s5
        self.set_motors(front_left, front_right, rear_left, rear_right)
        time.sleep(pulse_seconds)
        self.stop()
        time.sleep(max(0.0, servo_seconds - pulse_seconds) + LOOK_PAUSE_SECONDS)

    def set_approach_camera(self, s5, duration_ms=ARM_MOVE_MS):
        """Move only the shoulder/camera angle within approach-safe limits."""
        s5 = int(max(APPROACH_MIN_S5, min(APPROACH_MAX_S5, s5)))
        if abs(s5 - self.current_s5) < 10:
            return

        self.board.set_servo_position(duration_ms, [(5, s5)])
        self.current_s5 = s5
        time.sleep(duration_ms / 1000.0 + 0.05)

    def prepare_arm(self):
        """Set a known camera angle for the approach demo."""
        self.board.set_servo_position(600, [
            (1, 2500),  # Claw open.
            (3, 590),   # Wrist.
            (4, 2450),  # Elbow.
            (5, APPROACH_START_S5),
            (6, 1500),  # Base centered.
        ])
        self.current_s5 = APPROACH_START_S5
        time.sleep(0.7)

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
        target = self.choose_visual_target(blocks)
        return target, len(raw_blocks), len(blocks)

    def choose_visual_target(self, blocks):
        """
        Choose the block to approach.

        Before the robot moves, pick the best pickup target. After a target is
        locked, keep matching the same target by image position so the robot
        does not jump to another same-color block elsewhere in the field.
        """
        candidates = self.filter_approach_candidates(blocks)

        if self.locked_target is None:
            return self.detector.select_pickup_target(
                candidates,
                frame_width=FRAME_W,
                frame_height=FRAME_H,
                edge_margin_px=APPROACH_EDGE_MARGIN_PX,
            )

        locked_candidates = []
        reference = self.last_target or self.locked_target
        for block in candidates:
            if self.is_wrong_locked_target(block, reference):
                continue

            dx = block.center_x - reference.center_x
            dy = block.center_y - reference.center_y
            shift = (dx * dx + dy * dy) ** 0.5
            if shift <= LOCK_MATCH_MAX_SHIFT_PX:
                locked_candidates.append((shift, block))

        if not locked_candidates:
            return None

        return min(locked_candidates, key=lambda item: item[0])[1]

    def is_wrong_locked_target(self, block, reference):
        """
        Reject likely target swaps after a block is locked.

        During approach, the real target should generally get closer and lower
        in the image. If a candidate suddenly looks much farther away and moves
        higher in the image, it is probably a different same-color block.
        """
        if reference is None:
            return False

        distance_jump = block.estimated_distance_mm - reference.estimated_distance_mm
        y_drop = reference.center_y - block.center_y
        return (
            distance_jump > LOCK_DISTANCE_JUMP_MM
            and y_drop > LOCK_Y_DROP_PX
        )

    def filter_approach_candidates(self, blocks):
        """Keep only blocks that are reasonable approach targets."""
        candidates = []
        for block in blocks:
            if block.estimated_distance_mm > APPROACH_MAX_TARGET_DISTANCE_MM:
                continue
            if self.pickup_handoff_armed:
                # A close block naturally enters the bottom margin as the
                # camera tilts down. Keep following that already-locked block
                # until the detector truly loses it, while retaining the side
                # and top protections that prevent unsafe target chasing.
                x1, y1, x2, _ = self.detector._block_bounds(block)
                if (
                    x1 <= APPROACH_EDGE_MARGIN_PX
                    or x2 >= FRAME_W - APPROACH_EDGE_MARGIN_PX
                    or y1 <= APPROACH_EDGE_MARGIN_PX
                ):
                    continue
            elif self.detector._is_edge_touching(
                block,
                frame_width=FRAME_W,
                frame_height=FRAME_H,
                margin_px=APPROACH_EDGE_MARGIN_PX,
            ):
                continue
            candidates.append(block)
        return candidates

    def target_is_stable(self, target):
        """Require the selected target to stay in about the same place."""
        if target is None:
            self.last_target = None
            self.stable_count = 0
            return False

        self.lost_target_frames = 0

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

        stable = self.stable_count >= STABLE_FRAMES_REQUIRED
        if stable and self.locked_target is None:
            self.locked_target = target
            print("Locked %s target at x=%d y=%d." % (
                target.color,
                target.center_x,
                target.center_y,
            ))

        return stable

    def choose_action(self, target, track_until_lost=False):
        """Return the next safe movement action for a stable target."""
        offset = target.offset_from_center

        if not track_until_lost and self.at_front_approach_position(target):
            return 'reached', 0, 0

        if self.near_pickup_handoff(target) and abs(offset) > PICKUP_X_TOLERANCE_PX:
            if offset > 0:
                return 'fine strafe right', FINE_STRAFE_POWER, 0
            return 'fine strafe left', -FINE_STRAFE_POWER, 0

        if abs(offset) > X_TOLERANCE_PX:
            if offset > 0:
                return 'strafe right', STRAFE_POWER, 0
            return 'strafe left', -STRAFE_POWER, 0

        return 'forward', 0, FORWARD_POWER

    def near_pickup_handoff(self, target):
        """Return True when only small centering corrections should remain."""
        return (
            target.estimated_distance_mm <= HANDOFF_DISTANCE_MM + 50
            or target.center_y >= HANDOFF_VIEW_Y_MIN - 30
        )

    def centering_has_stalled(self, target):
        """
        Return True if repeated strafe pulses are not reducing target offset.

        Low battery or floor friction can make a too-small strafe pulse hum
        without moving. Stop instead of repeatedly pulsing forever.
        """
        abs_offset = abs(target.offset_from_center)
        if abs_offset <= X_TOLERANCE_PX:
            self.best_abs_offset = None
            self.no_center_progress_frames = 0
            return False

        if (
            self.best_abs_offset is None
            or abs_offset < self.best_abs_offset - CENTER_PROGRESS_MIN_PX
        ):
            self.best_abs_offset = abs_offset
            self.no_center_progress_frames = 0
            return False

        self.no_center_progress_frames += 1
        return self.no_center_progress_frames >= CENTER_PROGRESS_LIMIT

    def adjust_camera_for_target(self, target):
        """
        Keep the selected block in useful view as it gets close.

        If the block is low in the image, tilt the camera farther down. If it is
        high, tilt slightly forward again. This lets the robot approach closer
        before the block disappears below the camera.
        """
        y_error = target.center_y - TARGET_VIEW_Y
        if y_error > TARGET_VIEW_TOLERANCE_PX and self.current_s5 < APPROACH_MAX_S5:
            self.set_approach_camera(self.current_s5 + ARM_STEP)
            return 'camera down'
        if y_error < -TARGET_VIEW_TOLERANCE_PX and self.current_s5 > APPROACH_START_S5:
            self.set_approach_camera(self.current_s5 - ARM_STEP)
            return 'camera forward'
        return 'camera steady'

    def next_camera_adjustment(self, target):
        """Return the next camera action and S5 target without moving it."""
        y_error = target.center_y - TARGET_VIEW_Y
        if y_error > TARGET_VIEW_TOLERANCE_PX and self.current_s5 < APPROACH_MAX_S5:
            return 'camera down', min(self.current_s5 + ARM_STEP, APPROACH_MAX_S5)
        if y_error < -TARGET_VIEW_TOLERANCE_PX and self.current_s5 > APPROACH_START_S5:
            return 'camera forward', max(self.current_s5 - ARM_STEP, APPROACH_START_S5)
        return 'camera steady', self.current_s5

    def at_front_approach_position(self, target):
        """
        Return True when the block is close, low, and tightly centered.

        The approach-only demo stops here while the target is visible. The
        combined demo uses this state to arm its handoff, then keeps tracking
        until the same close target passes below the camera.
        """
        return (
            abs(target.offset_from_center) <= PICKUP_X_TOLERANCE_PX
            and (
                (
                    target.estimated_distance_mm <= HANDOFF_DISTANCE_MM
                    and target.center_y >= HANDOFF_VIEW_Y_MIN
                )
                or (
                    self.current_s5 >= HANDOFF_S5_MIN
                    and target.center_y >= HANDOFF_VIEW_Y_MIN
                )
            )
        )

    def run(self, timeout=MAX_RUNTIME_SECONDS, track_until_lost=False):
        """Run the approach-only demo."""
        if not self.check_battery():
            return {'success': False, 'reason': 'battery_low'}

        self.open_camera()
        self.prepare_arm()
        start = time.monotonic()
        frames = 0

        print()
        print("Looking for %s block..." % self.color)
        print("Target must be stable for %d frames before movement." %
              STABLE_FRAMES_REQUIRED)
        print("Camera starts at S5=%d and can track down to S5=%d." % (
            APPROACH_START_S5,
            APPROACH_TOUCH_S5,
        ))
        print("Press Ctrl+C to stop.")
        print("-" * 60)

        try:
            while time.monotonic() - start < timeout:
                frames += 1
                target, raw_count, merged_count = self.read_target()

                if target is None:
                    self.stop()
                    if self.locked_target is not None:
                        self.lost_target_frames += 1

                        if track_until_lost and self.pickup_handoff_armed:
                            print("Close centered target no longer visible (%d/%d)." % (
                                self.lost_target_frames,
                                CLOSE_TARGET_LOST_LIMIT,
                            ))
                            if self.lost_target_frames >= CLOSE_TARGET_LOST_LIMIT:
                                print("Target passed below camera. Motors stopped.")
                                return {
                                    'success': True,
                                    'reason': 'target_below_camera',
                                    'frames': frames,
                                    's5': self.current_s5,
                                }
                            time.sleep(0.15)
                            continue

                        print("Locked %s target lost (%d/%d)." % (
                            self.color,
                            self.lost_target_frames,
                            LOST_TARGET_LIMIT,
                        ))
                        if self.lost_target_frames >= LOST_TARGET_LIMIT:
                            print("Lost locked target. Motors stopped.")
                            return {
                                'success': False,
                                'reason': 'lost_target',
                                'frames': frames,
                            }
                    else:
                        print("No stable %s target found." % self.color)
                    time.sleep(0.25)
                    continue

                stable = self.target_is_stable(target)
                distance_cm = target.estimated_distance_mm / 10.0
                print(
                    "%s target: %.0fcm offset=%+d y=%d score=%.1f "
                    "S5=%d stable=%d/%d detections=%d/%d" % (
                        target.color,
                        distance_cm,
                        target.offset_from_center,
                        target.center_y,
                        self.detector.pickup_target_score(target),
                        self.current_s5,
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

                if track_until_lost:
                    was_armed = self.pickup_handoff_armed
                    self.pickup_handoff_armed = self.at_front_approach_position(target)
                    if self.pickup_handoff_armed and not was_armed:
                        print("  Close tracking armed; continuing until target leaves view.")

                action, vx, vy = self.choose_action(
                    target,
                    track_until_lost=track_until_lost,
                )
                camera_action, next_s5 = self.next_camera_adjustment(target)
                if camera_action != 'camera steady':
                    if track_until_lost and camera_action == 'camera down':
                        print("  Moving: %s + %s (S5=%d)" % (
                            action,
                            camera_action,
                            next_s5,
                        ))
                        self.drive_and_tilt_pulse(next_s5, vx=vx, vy=vy)
                    else:
                        self.set_approach_camera(next_s5)
                        print("  Moving: %s (S5=%d)" % (
                            camera_action,
                            self.current_s5,
                        ))
                    continue

                if self.centering_has_stalled(target):
                    self.stop()
                    print("Centering stalled. Motors stopped.")
                    return {
                        'success': False,
                        'reason': 'centering_stalled',
                        'frames': frames,
                        'offset': target.offset_from_center,
                    }

                if action == 'reached':
                    self.stop()
                    print("Reached front approach position. Motors stopped.")
                    return {
                        'success': True,
                        'reason': 'reached',
                        'frames': frames,
                        'distance_cm': round(distance_cm, 1),
                        'offset': target.offset_from_center,
                        's5': self.current_s5,
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
    print("This demo moves the drive base and shoulder/camera only.")
    print("It does not grab the block.")
    print("Put the robot on the floor with clear space around it.")
    print()

    demo = BlockApproachDemo(color=args.color)
    result = demo.run(timeout=args.timeout)
    print()
    print("Result: %s" % ("SUCCESS" if result.get('success') else "STOPPED"))
    print("Reason: %s" % result.get('reason'))


if __name__ == '__main__':
    main()
