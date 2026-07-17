#!/usr/bin/env python3
"""Capture an annotated line-detection image without driving the robot."""

import os
import sys
import time

import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board
from skills.line_following.line_follower import LineFollower


def format_center(value):
    """Format an optional scan-strip center for console output."""
    return '---' if value is None else str(value)


def main():
    print('=' * 60)
    print('LINE DETECTION TEST - DRIVE MOTORS WILL NOT MOVE')
    print('=' * 60)
    print()

    board = get_board()
    follower = LineFollower(board=board)
    camera = None

    try:
        print('[1/4] Positioning camera down...')
        board.set_servo_position(800, LineFollower.ARM_CAMERA_DOWN)
        time.sleep(1.5)

        print('[2/4] Opening camera...')
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, LineFollower.FRAME_W)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, LineFollower.FRAME_H)
        time.sleep(1.0)

        print('[3/4] Detecting line...')
        frame = None
        detection = None
        for _ in range(8):
            ok, candidate = camera.read()
            if ok:
                frame = candidate
                detection = follower.detect_line(frame)
            time.sleep(0.08)

        if frame is None or detection is None:
            print('ERROR: Could not capture a camera frame.')
            return

        print('Detection: %s' % ('FOUND' if detection['found'] else 'NOT FOUND'))
        print('  Far center:  %s' % format_center(detection['far_cx']))
        print('  Mid center:  %s' % format_center(detection['mid_cx']))
        print('  Near center: %s' % format_center(detection['near_cx']))
        print('  Control error: %+d pixels' % detection['error'])

        print('[4/4] Saving annotated images...')
        annotated = frame.copy()
        colors = {
            'far': (255, 180, 0),
            'mid': (0, 220, 220),
            'near': (0, 255, 0),
        }

        for name, top, bottom, _ in LineFollower.SCAN_BANDS:
            color = colors[name]
            cv2.rectangle(annotated, (0, top), (639, bottom), color, 2)
            center = detection['%s_cx' % name]
            if center is not None:
                cy = (top + bottom) // 2
                cv2.circle(annotated, (center, cy), 8, color, -1)
                cv2.line(annotated, (320, cy), (center, cy), color, 2)

        cv2.line(annotated, (320, 0), (320, 479), (180, 180, 180), 1)
        cv2.putText(
            annotated,
            'far=%s mid=%s near=%s error=%+d' % (
                format_center(detection['far_cx']),
                format_center(detection['mid_cx']),
                format_center(detection['near_cx']),
                detection['error'],
            ),
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        cv2.imwrite('line_detect_result.jpg', annotated)
        cv2.imwrite('line_mask.jpg', detection['mask'])
        print('Saved line_detect_result.jpg and line_mask.jpg')
    finally:
        follower.cleanup()
        if camera is not None:
            camera.release()
        board.set_servo_position(800, [
            (1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)
        ])


if __name__ == '__main__':
    main()
