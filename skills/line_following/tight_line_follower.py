#!/usr/bin/env python3
"""
Experimental tight line follower.

This test controller leaves the normal LineFollower unchanged. It borrows the
vendor controller's useful idea of measuring the line in three thin horizontal
strips, including one near the bottom of the camera image. The closest visible
part of the line controls mecanum centering while the difference between the
near and far strips provides a small heading correction.
"""

import time

import cv2
import numpy as np

from skills.line_following.line_follower import LineFollower


class TightLineFollower(LineFollower):
    """Line-following experiment that emphasizes the tape nearest the robot."""

    # Rows are based on the vendor VisualPatrol controller. Run the detection-
    # only test before driving because the Pathfinder arm angle may require
    # these rows to move slightly up or down.
    SCAN_BANDS = (
        ("far", 240, 280, 0.10),
        ("mid", 340, 380, 0.30),
        ("near", 420, 465, 0.60),
    )

    MIN_CONTOUR_AREA = 25

    # Start a correction after the line leaves the wider window, then continue
    # until it reaches the tighter window. This prevents rapid on/off chatter.
    CENTER_ENTER_PIXELS = 12
    CENTER_EXIT_PIXELS = 5

    LOST_FRAMES = 3
    SEARCH_TURN_POWER = 40
    SEARCH_TURN_SECONDS = 0.10
    SEARCH_SETTLE_SECONDS = 0.18

    def __init__(self, robot=None, board=None):
        super().__init__(robot=robot, board=board)
        self._strafe_active = False

    @staticmethod
    def _largest_contour_center(mask):
        """Return the center and area of the largest connected mask region."""
        contours = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )[-2]
        if not contours:
            return None, 0.0

        contour = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(contour))
        if area < TightLineFollower.MIN_CONTOUR_AREA:
            return None, area

        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return None, area

        return int(moments["m10"] / moments["m00"]), area

    def detect_line(self, frame):
        """Detect the strongest lime-green line region in each scan strip."""
        full_mask = np.zeros((self.FRAME_H, self.FRAME_W), dtype=np.uint8)
        centers = {"far": None, "mid": None, "near": None}
        areas = {"far": 0.0, "mid": 0.0, "near": 0.0}
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
                "found": False,
                "cx": 0,
                "cy": 0,
                "error": 0,
                "heading_error": 0,
                "near_cx": None,
                "mid_cx": None,
                "far_cx": None,
                "band_areas": areas,
                "ratio": ratio,
                "mask": full_mask,
            }

        cx = int(weighted_center / weight_sum)

        # Center using the closest strip that currently sees the tape. The far
        # strip helps anticipate direction but does not pull the robot off the
        # line directly beneath it.
        control_cx = centers["near"]
        if control_cx is None:
            control_cx = centers["mid"]
        if control_cx is None:
            control_cx = centers["far"]

        near_cx = centers["near"]
        mid_cx = centers["mid"]
        far_cx = centers["far"]

        if near_cx is not None and far_cx is not None:
            heading_error = far_cx - near_cx
        elif near_cx is not None and mid_cx is not None:
            heading_error = mid_cx - near_cx
        else:
            heading_error = 0

        return {
            "found": True,
            "cx": cx,
            "cy": 0,
            "error": control_cx - self.CENTER_X,
            "heading_error": heading_error,
            "near_cx": near_cx,
            "mid_cx": mid_cx,
            "far_cx": far_cx,
            "band_areas": areas,
            "ratio": ratio,
            "mask": full_mask,
        }

    def _search_for_line(self, max_rotations=12, cancel_callback=None):
        """Search using enough turn power to move reliably on the foam floor."""
        for _ in range(max_rotations):
            if cancel_callback and cancel_callback():
                self._stop()
                return False

            frame = self._get_frame()
            if frame is not None and self.detect_line(frame)["found"]:
                self._stop()
                return True

            power = self.SEARCH_TURN_POWER
            self.board.set_motor_duty([
                (1, power), (2, -power), (3, power), (4, -power)
            ])
            time.sleep(self.SEARCH_TURN_SECONDS)
            self._stop()
            time.sleep(self.SEARCH_SETTLE_SECONDS)

        self._stop()
        return False

    def _calculate_strafe(self, error):
        """Calculate lateral correction with separate enter and exit limits."""
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
        """Follow the line and stop immediately while a lost line is confirmed."""
        self._open_camera()
        self._strafe_active = False

        if position_camera:
            self._position_camera()

        if search_first and not self._search_for_line(
                cancel_callback=cancel_callback):
            reason = (
                "cancelled"
                if cancel_callback and cancel_callback()
                else "line_not_found"
            )
            return {
                "success": False,
                "reason": reason,
                "frames": 0,
                "duration": 0,
            }

        start = time.time()
        frames = 0
        lost_count = 0

        try:
            while time.time() - start < timeout:
                if cancel_callback and cancel_callback():
                    self._stop()
                    return {
                        "success": False,
                        "reason": "cancelled",
                        "frames": frames,
                        "duration": time.time() - start,
                    }

                frame = self._get_frame()
                if frame is None:
                    continue

                frames += 1
                detection = self.detect_line(frame)
                if not detection["found"]:
                    lost_count += 1
                    self._stop()
                    if lost_count >= self.LOST_FRAMES:
                        return {
                            "success": True,
                            "reason": "line_ended",
                            "frames": frames,
                            "duration": time.time() - start,
                        }
                    time.sleep(0.03)
                    continue

                lost_count = 0
                strafe = self._calculate_strafe(detection["error"])

                if abs(detection["heading_error"]) > self.HEADING_DEADBAND:
                    turn = detection["heading_error"] * self.K_TURN
                else:
                    turn = 0.0
                turn = max(-self.MAX_TURN, min(self.MAX_TURN, turn))

                self._drive(self.FORWARD_SPEED, strafe, turn)

                if callback and frames % 5 == 0:
                    callback(detection, strafe, turn)

                time.sleep(0.02)

            self._stop()
            return {
                "success": False,
                "reason": "timeout",
                "frames": frames,
                "duration": time.time() - start,
            }
        except KeyboardInterrupt:
            self._stop()
            return {
                "success": False,
                "reason": "interrupted",
                "frames": frames,
                "duration": time.time() - start,
            }
        finally:
            self._stop()

