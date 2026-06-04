#!/usr/bin/env python3
"""
Camera Intrinsic Calibration — headless, runs over SSH.

Hold a printed checkerboard in front of the camera at different angles,
distances, and positions. Script auto-captures when it detects the board,
then saves a .npz that camera.py and Robot() can load directly.

Print a checkerboard pattern:
  https://calib.io  →  Checkerboard  →  Rows: 7, Cols: 10
  (inner corners: 6 rows x 9 cols — matches BOARD_H/BOARD_W below)
  Any square size works; 30mm squares on letter/A4 paper is ideal.

Usage:
  python3 scripts/calibration/calibrate_camera_intrinsics.py

Output:
  lib/camera_calibration.npz

Load in code:
  with Robot(calibration_path='lib/camera_calibration.npz') as robot: ...
"""

import cv2
import numpy as np
import time
import sys
from pathlib import Path

# Inner corners of the checkerboard (cols, rows)
# An 8x6 square board has 7x5 inner corners
BOARD_W = 7
BOARD_H = 5
BOARD_SIZE = (BOARD_W, BOARD_H)

TARGET_CAPTURES = 20   # Captures needed before calibrating
COOLDOWN_SEC    = 2.0  # Seconds between auto-captures (time to reposition)
IMG_W, IMG_H    = 640, 480

REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
OUTPUT_PATH = REPO_ROOT / "lib" / "camera_calibration.npz"


def main():
    print("=" * 60)
    print("CAMERA INTRINSIC CALIBRATION")
    print("=" * 60)
    print(f"\nBoard:   {BOARD_W}x{BOARD_H} inner corners  (8x6 square checkerboard)")
    print(f"Target:  {TARGET_CAPTURES} captures")
    print(f"Cooldown: {COOLDOWN_SEC}s between captures (time to reposition)")
    print(f"Output:  {OUTPUT_PATH}")
    print()
    print("Instructions:")
    print("  1. Hold the printed checkerboard in front of the camera")
    print("  2. Tilt, rotate, and move it to different corners of the frame")
    print("  3. Include some close shots (~20cm) and far shots (~60cm)")
    print("  4. Script auto-captures every 2s when the board is detected")
    print()
    print("Press Ctrl+C to cancel.\n")

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_H)
    time.sleep(1.5)

    if not cap.isOpened():
        print("ERROR: Camera not available.")
        sys.exit(1)

    # 3-D object points for one checkerboard view (z=0 plane)
    objp = np.zeros((BOARD_H * BOARD_W, 3), np.float32)
    objp[:, :2] = np.mgrid[0:BOARD_W, 0:BOARD_H].T.reshape(-1, 2)

    obj_points = []
    img_points = []

    subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    last_capture_time = 0
    captures          = 0
    frame_idx         = 0

    try:
        while captures < TARGET_CAPTURES:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            frame_idx += 1

            # Only run detection every 6th frame (~5 fps at 30fps camera)
            if frame_idx % 6 != 0:
                continue

            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(
                gray, BOARD_SIZE,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
            )

            now = time.time()

            if not found:
                if frame_idx % 60 == 0:
                    print("  Searching for checkerboard — hold it steady and fully in frame...")
                continue

            cooldown_remaining = COOLDOWN_SEC - (now - last_capture_time)

            if cooldown_remaining > 0:
                if frame_idx % 30 == 0:
                    print(f"  Board detected — capturing in {cooldown_remaining:.1f}s — reposition now")
                continue

            # Auto-capture
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), subpix_criteria)
            obj_points.append(objp)
            img_points.append(corners2)
            last_capture_time = now
            captures += 1

            print(f"  [{captures:>2}/{TARGET_CAPTURES}] Captured!  Move to a new angle/position.")

    except KeyboardInterrupt:
        print("\nCancelled.")
        cap.release()
        sys.exit(0)

    cap.release()

    if captures < 10:
        print(f"\nOnly {captures} captures collected — need at least 10.")
        print("Re-run and vary the board angle more.")
        sys.exit(1)

    print(f"\nRunning calibration on {captures} captures...")

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, (IMG_W, IMG_H), None, None
    )

    # Mean reprojection error — lower is better; < 0.5px is good
    total_error = 0.0
    for i in range(len(obj_points)):
        projected, _ = cv2.projectPoints(obj_points[i], rvecs[i], tvecs[i], mtx, dist)
        total_error += cv2.norm(img_points[i], projected, cv2.NORM_L2) / len(projected)
    mean_error = total_error / len(obj_points)

    fx, fy = mtx[0, 0], mtx[1, 1]
    cx, cy = mtx[0, 2], mtx[1, 2]

    print()
    print("Results:")
    print(f"  fx = {fx:.2f}  (was: 500 estimated)")
    print(f"  fy = {fy:.2f}  (was: 500 estimated)")
    print(f"  cx = {cx:.2f}  (was: 320 estimated)")
    print(f"  cy = {cy:.2f}  (was: 240 estimated)")
    print(f"  Reprojection error: {mean_error:.4f} px")
    print(f"    < 0.5 px  → excellent")
    print(f"    < 1.0 px  → acceptable")
    print(f"    > 1.0 px  → re-run with more varied angles")

    np.savez(OUTPUT_PATH, mtx_array=mtx, dist_array=dist)
    print(f"\nSaved: {OUTPUT_PATH}")

    print()
    print("Load in your code:")
    print("  with Robot(calibration_path='lib/camera_calibration.npz') as robot:")
    print("      ...")
    print()
    print("Or verify it loaded:")
    print("  robot.status()  # shows 'Camera cal: fx=...' if loaded")


if __name__ == "__main__":
    main()
