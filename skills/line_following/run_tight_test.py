#!/usr/bin/env python3
"""Run the experimental tight line follower or capture a detection image."""

import argparse
import os
import sys
import time

import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from skills.line_following.tight_line_follower import TightLineFollower


def format_center(value):
    """Format a scan-strip center for console output."""
    return "---" if value is None else str(value)


def print_status(detection, strafe, turn):
    """Show what each scan strip sees and how the robot responds."""
    print(
        "  far=%s mid=%s near=%s err=%+d heading=%+d "
        "strafe=%+.1f turn=%+.1f" % (
            format_center(detection["far_cx"]),
            format_center(detection["mid_cx"]),
            format_center(detection["near_cx"]),
            detection["error"],
            detection["heading_error"],
            strafe,
            turn,
        )
    )


def capture_detection(follower):
    """Capture an annotated image without moving the drive motors."""
    print("Positioning camera and opening video...")
    follower._open_camera()
    follower._position_camera()

    frame = None
    detection = None
    for _ in range(8):
        frame = follower._get_frame()
        if frame is not None:
            detection = follower.detect_line(frame)
        time.sleep(0.08)

    if frame is None or detection is None:
        print("ERROR: Could not capture a camera frame.")
        return False

    annotated = frame.copy()
    colors = {
        "far": (255, 180, 0),
        "mid": (0, 220, 220),
        "near": (0, 255, 0),
    }

    for name, top, bottom, _ in follower.SCAN_BANDS:
        color = colors[name]
        cv2.rectangle(annotated, (0, top), (639, bottom), color, 2)
        center = detection["%s_cx" % name]
        if center is not None:
            cy = (top + bottom) // 2
            cv2.circle(annotated, (center, cy), 8, color, -1)
            cv2.line(annotated, (320, cy), (center, cy), color, 2)

    cv2.line(annotated, (320, 0), (320, 479), (180, 180, 180), 1)
    cv2.putText(
        annotated,
        "far=%s mid=%s near=%s error=%+d" % (
            format_center(detection["far_cx"]),
            format_center(detection["mid_cx"]),
            format_center(detection["near_cx"]),
            detection["error"],
        ),
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    cv2.imwrite("tight_line_test.jpg", annotated)
    cv2.imwrite("tight_line_mask.jpg", detection["mask"])

    print("Detection: %s" % ("FOUND" if detection["found"] else "NOT FOUND"))
    print("  Far center:  %s" % format_center(detection["far_cx"]))
    print("  Mid center:  %s" % format_center(detection["mid_cx"]))
    print("  Near center: %s" % format_center(detection["near_cx"]))
    print("  Control error: %+d pixels" % detection["error"])
    print("Saved tight_line_test.jpg and tight_line_mask.jpg")
    return detection["found"]


def main():
    parser = argparse.ArgumentParser(
        description="Test tighter line following without changing the normal demo."
    )
    parser.add_argument(
        "--detect-only",
        action="store_true",
        help="save annotated camera images without moving the drive motors",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="maximum driving time in seconds (default: 30)",
    )
    args = parser.parse_args()

    follower = TightLineFollower()
    try:
        if args.detect_only:
            capture_detection(follower)
            return

        print("=" * 60)
        print("EXPERIMENTAL TIGHT LINE FOLLOWING TEST")
        print("=" * 60)
        print()
        print("The robot will move and may turn while searching for the line.")
        print("Put it on the floor with a clear path and keep hands away.")
        print("Press Ctrl+C at any time to stop.")
        print()
        input("Press Enter when the area is clear...")

        result = follower.follow(timeout=args.timeout, callback=print_status)
        print()
        print("Result: %s" % result["reason"])
        print("Frames: %d" % result["frames"])
        print("Duration: %.1fs" % result["duration"])
    finally:
        follower.cleanup()


if __name__ == "__main__":
    main()
