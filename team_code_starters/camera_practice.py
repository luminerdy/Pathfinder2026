#!/usr/bin/env python3
"""
Team camera practice.

Run from the robot:
    cd /home/robot/team_code
    python3 camera_practice.py
"""

import time

import cv2


OUTPUT_FILE = "team_camera_test.jpg"


def main():
    print("Team Camera Practice")
    print("Opening camera...")

    # VideoCapture(0) opens the first USB camera, usually /dev/video0.
    camera = cv2.VideoCapture(0)
    # Ask for a small, fast image size that is useful for robot vision.
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not camera.isOpened():
        print("Could not open camera. Check the USB camera cable.")
        return

    print("Letting the camera adjust...")
    frame = None
    ok = False
    # The first frames can be dark or blurry while auto-exposure adjusts.
    # Keep the last frame from this short warm-up.
    for _ in range(5):
        ok, frame = camera.read()
        time.sleep(0.1)

    # Release the camera so the browser viewer or another script can use it.
    camera.release()

    if ok and frame is not None:
        cv2.imwrite(OUTPUT_FILE, frame)
        print("Saved", OUTPUT_FILE)
    else:
        print("Could not capture a camera frame.")


if __name__ == "__main__":
    main()
