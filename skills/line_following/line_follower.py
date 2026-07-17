#!/usr/bin/env python3
"""
Line following controller.

The camera looks at three thin horizontal strips across the floor. The nearest
visible strip controls mecanum centering, while the difference between the near
and far strips provides a small heading correction for curves.

Before driving, the robot turns until the far strip sees the tape ahead. During
the run, the robot stops while it confirms that a missing line is the tape end.

Usage:
    from skills.line_following.line_follower import LineFollower

    follower = LineFollower()
    result = follower.follow(timeout=30)
    follower.cleanup()
"""

import os
import sys
import time

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board


class LineFollower:
    """Follow lime-green tape using camera feedback and mecanum drive."""

    FRAME_W = 640
    FRAME_H = 480
    CENTER_X = 320

    # Each tuple is: name, first row, last row, steering weight. Thin strips
    # avoid averaging unrelated green pixels across most of the image.
    SCAN_BANDS = (
        ('far', 240, 280, 0.10),
        ('mid', 340, 380, 0.30),
        ('near', 420, 465, 0.60),
    )

    HSV_LOWER = np.array([35, 50, 50])
    HSV_UPPER = np.array([85, 255, 255])
    KERNEL_SIZE = 5
    MIN_CONTOUR_AREA = 25

    K_STRAFE = 0.22
    K_TURN = 0.08
    FORWARD_SPEED = 38
    MIN_STRAFE = 18
    MAX_STRAFE = 28
    MAX_TURN = 10
    CENTER_ENTER_PIXELS = 12
    CENTER_EXIT_PIXELS = 5
    HEADING_DEADBAND = 18

    LOST_FRAMES = 3
    SEARCH_STEPS = 18
    SEARCH_TURN_POWER = 40
    SEARCH_TURN_SECONDS = 0.10
    SEARCH_SETTLE_SECONDS = 0.18
    ACQUIRE_FAR_MAX_ERROR = 100

    ARM_CAMERA_DOWN = [
        (1, 2500), (3, 590), (4, 2450), (5, 1214), (6, 1500)
    ]

    def __init__(self, robot=None, board=None):
        """Create a follower using a shared robot or a raw motor board."""
        self._robot = robot
        self._own_camera = False
        self._strafe_active = False

        if robot and hasattr(robot, 'board'):
            self.board = robot.board
        elif board:
            self.board = board
        else:
            self.board = get_board()

        self.camera = None
        self.kernel = np.ones(
            (self.KERNEL_SIZE, self.KERNEL_SIZE), dtype=np.uint8
        )

    def _open_camera(self):
        """Use the robot camera when shared, or open camera zero directly."""
        if self._robot and hasattr(self._robot, 'camera') and self._robot.camera:
            self.camera = self._robot.camera
            return

        if self.camera is None or (
                hasattr(self.camera, 'isOpened') and not self.camera.isOpened()):
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.FRAME_W)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.FRAME_H)
            time.sleep(1.0)
            self._own_camera = True

    def _close_camera(self):
        """Release only a camera that this follower opened."""
        if self._own_camera and self.camera and hasattr(self.camera, 'release'):
            self.camera.release()
            self.camera = None

    def _get_frame(self):
        """Get a frame from the shared camera object or OpenCV camera."""
        if self.camera is not None and hasattr(self.camera, 'get_raw_frame'):
            return self.camera.get_raw_frame()
        if self.camera is not None:
            ok, frame = self.camera.read()
            return frame if ok else None
        return None

    def _stop(self):
        """Stop every drive motor."""
        if self._robot and hasattr(self._robot, 'stop'):
            self._robot.stop()
        else:
            self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

    def _drive(self, forward, strafe, turn):
        """Mix forward, lateral, and heading commands for mecanum wheels."""
        fl = int(forward + strafe + turn)
        fr = int(forward - strafe - turn)
        rl = int(forward - strafe + turn)
        rr = int(forward + strafe - turn)

        def clamp(value):
            return max(-100, min(100, value))

        self.board.set_motor_duty([
            (1, clamp(fl)), (2, clamp(fr)),
            (3, clamp(rl)), (4, clamp(rr)),
        ])

    def _position_camera(self):
        """Point the arm camera down at the tape."""
        self.board.set_servo_position(800, self.ARM_CAMERA_DOWN)
        time.sleep(1.0)

    @classmethod
    def _largest_contour_center(cls, mask):
        """Return the center and area of the largest connected mask region."""
        contours = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[-2]
        if not contours:
            return None, 0.0

        contour = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(contour))
        if area < cls.MIN_CONTOUR_AREA:
            return None, area

        moments = cv2.moments(contour)
        if moments['m00'] == 0:
            return None, area
        return int(moments['m10'] / moments['m00']), area

    def detect_line(self, frame):
        """Detect the strongest lime-green region in each camera scan strip."""
        full_mask = np.zeros((self.FRAME_H, self.FRAME_W), dtype=np.uint8)
        centers = {'far': None, 'mid': None, 'near': None}
        areas = {'far': 0.0, 'mid': 0.0, 'near': 0.0}
        weighted_center = 0.0
        weight_sum = 0.0
        green_pixels = 0
        sampled_pixels = 0

        for name, top, bottom, weight in self.SCAN_BANDS:
            band = frame[top:bottom, :]
            hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, self.HSV_LOWER, self.HSV_UPPER)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)

            full_mask[top:bottom, :] = mask
            green_pixels += cv2.countNonZero(mask)
            sampled_pixels += mask.shape[0] * mask.shape[1]

            center, area = self._largest_contour_center(mask)
            centers[name] = center
            areas[name] = area
            if center is not None:
                weighted_center += center * weight
                weight_sum += weight

        ratio = green_pixels / sampled_pixels if sampled_pixels else 0.0
        if weight_sum == 0:
            return {
                'found': False,
                'cx': 0,
                'cy': 0,
                'error': 0,
                'heading_error': 0,
                'near_cx': None,
                'mid_cx': None,
                'far_cx': None,
                'band_areas': areas,
                'ratio': ratio,
                'mask': full_mask,
            }

        display_cx = int(weighted_center / weight_sum)

        # The closest strip controls lateral position. A farther strip is used
        # only when the tape has not yet entered a closer one.
        control_cx = centers['near']
        if control_cx is None:
            control_cx = centers['mid']
        if control_cx is None:
            control_cx = centers['far']

        near_cx = centers['near']
        mid_cx = centers['mid']
        far_cx = centers['far']

        if near_cx is not None and far_cx is not None:
            heading_error = far_cx - near_cx
        elif near_cx is not None and mid_cx is not None:
            heading_error = mid_cx - near_cx
        else:
            heading_error = 0

        return {
            'found': True,
            'cx': display_cx,
            'cy': 0,
            'error': control_cx - self.CENTER_X,
            'heading_error': heading_error,
            'near_cx': near_cx,
            'mid_cx': mid_cx,
            'far_cx': far_cx,
            'band_areas': areas,
            'ratio': ratio,
            'mask': full_mask,
        }

    def _search_for_line(self, max_rotations=None, cancel_callback=None):
        """Turn until the far scan strip confirms a usable line ahead."""
        steps = self.SEARCH_STEPS if max_rotations is None else max_rotations
        direction = 1

        for step in range(steps):
            if cancel_callback and cancel_callback():
                self._stop()
                return False

            frame = self._get_frame()
            detection = self.detect_line(frame) if frame is not None else None

            if detection is not None:
                far_cx = detection['far_cx']
                mid_cx = detection['mid_cx']
                near_cx = detection['near_cx']
                print('  Search: far=%s mid=%s near=%s' % (
                    '---' if far_cx is None else far_cx,
                    '---' if mid_cx is None else mid_cx,
                    '---' if near_cx is None else near_cx,
                ))

                if far_cx is not None:
                    far_error = far_cx - self.CENTER_X
                    if abs(far_error) <= self.ACQUIRE_FAR_MAX_ERROR:
                        self._stop()
                        print('  Far strip acquired. Starting line following.')
                        return True
                    direction = 1 if far_error > 0 else -1
                elif detection['found']:
                    closest_cx = near_cx if near_cx is not None else mid_cx
                    if closest_cx is not None:
                        closest_error = closest_cx - self.CENTER_X
                        if abs(closest_error) > self.CENTER_EXIT_PIXELS:
                            direction = 1 if closest_error > 0 else -1

            # Search one side first, then sweep back through the starting view.
            if (detection is None or not detection['found']) and step == 6:
                direction = -1

            power = self.SEARCH_TURN_POWER * direction
            self.board.set_motor_duty([
                (1, power), (2, -power), (3, power), (4, -power)
            ])
            time.sleep(self.SEARCH_TURN_SECONDS)
            self._stop()
            time.sleep(self.SEARCH_SETTLE_SECONDS)

        self._stop()
        return False

    def _calculate_strafe(self, error):
        """Apply minimum useful strafe power with centering hysteresis."""
        if self._strafe_active:
            if abs(error) <= self.CENTER_EXIT_PIXELS:
                self._strafe_active = False
        elif abs(error) >= self.CENTER_ENTER_PIXELS:
            self._strafe_active = True

        if not self._strafe_active:
            return 0.0

        strafe = error * self.K_STRAFE
        if abs(strafe) < self.MIN_STRAFE:
            strafe = self.MIN_STRAFE if error > 0 else -self.MIN_STRAFE
        return max(-self.MAX_STRAFE, min(self.MAX_STRAFE, strafe))

    def follow(self, timeout=30, position_camera=True, search_first=True,
               callback=None, cancel_callback=None):
        """Find and follow the line until its end, timeout, or cancellation."""
        self._open_camera()
        self._strafe_active = False

        if position_camera:
            self._position_camera()

        if search_first and not self._search_for_line(
                cancel_callback=cancel_callback):
            reason = (
                'cancelled'
                if cancel_callback and cancel_callback()
                else 'line_not_found'
            )
            return {
                'success': False,
                'reason': reason,
                'frames': 0,
                'duration': 0,
            }

        start = time.time()
        frames = 0
        lost_count = 0

        try:
            while time.time() - start < timeout:
                if cancel_callback and cancel_callback():
                    self._stop()
                    return {
                        'success': False,
                        'reason': 'cancelled',
                        'frames': frames,
                        'duration': time.time() - start,
                    }

                frame = self._get_frame()
                if frame is None:
                    continue

                frames += 1
                detection = self.detect_line(frame)
                if not detection['found']:
                    lost_count += 1
                    self._stop()
                    if lost_count >= self.LOST_FRAMES:
                        return {
                            'success': True,
                            'reason': 'line_ended',
                            'frames': frames,
                            'duration': time.time() - start,
                        }
                    time.sleep(0.03)
                    continue

                lost_count = 0
                strafe = self._calculate_strafe(detection['error'])

                if abs(detection['heading_error']) > self.HEADING_DEADBAND:
                    turn = detection['heading_error'] * self.K_TURN
                else:
                    turn = 0.0
                turn = max(-self.MAX_TURN, min(self.MAX_TURN, turn))

                self._drive(self.FORWARD_SPEED, strafe, turn)

                if callback and frames % 5 == 0:
                    callback(detection, strafe, turn)

                time.sleep(0.02)

            self._stop()
            return {
                'success': False,
                'reason': 'timeout',
                'frames': frames,
                'duration': time.time() - start,
            }
        except KeyboardInterrupt:
            self._stop()
            return {
                'success': False,
                'reason': 'interrupted',
                'frames': frames,
                'duration': time.time() - start,
            }
        finally:
            self._stop()

    def cleanup(self):
        """Stop the drive base and release owned camera resources."""
        self._stop()
        self._close_camera()


if __name__ == '__main__':
    print('Use run_demo.py to run the line-following demonstration.')
