#!/usr/bin/env python3
"""
Sample LAB color values from live camera for block detection tuning.

Automatically finds the block in the frame (brightest object on dark floor),
centers the crop on it, saves a preview for confirmation, then samples.

Usage:
    python3 scripts/calibration/sample_lab_colors.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import cv2
import numpy as np
import time
from robot import Robot

COLORS     = ['red', 'blue', 'yellow']
SAMPLES    = 25
INTERVAL   = 0.4
CROP_PX    = 80
STD_MARGIN = 2.0
FIXED_PAD  = 15
SNAP_PATH  = '/tmp/lab_sample_preview.jpg'

# Ignore top strip (checkerboard lives there)
IGNORE_TOP_ROWS = 80


def find_block_center(frame):
    """Find the brightest colored object on the floor. Returns (cx, cy) or None."""
    # Mask out top strip where checkerboard appears
    masked = frame.copy()
    masked[:IGNORE_TOP_ROWS, :] = 0

    hsv = cv2.cvtColor(masked, cv2.COLOR_BGR2HSV)
    # Bright AND saturated pixels = colored block (floor is dark and unsaturated)
    bright_mask = cv2.inRange(hsv, (0, 30, 60), (180, 255, 255))
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))

    contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest) < 200:
        return None

    M = cv2.moments(largest)
    if M['m00'] == 0:
        return None

    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return cx, cy


def save_preview(frame, cx, cy, color, found):
    preview = frame.copy()
    half = CROP_PX // 2
    if found:
        box_color = (0, 255, 0)
        label = f"Block found - sample region"
    else:
        box_color = (0, 0, 255)
        label = f"Block NOT found - reposition {color}"
    cv2.rectangle(preview, (cx - half, cy - half), (cx + half, cy + half), box_color, 2)
    cv2.putText(preview, label, (cx - half, max(cy - half - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)
    cv2.imwrite(SNAP_PATH, preview)


def sample_color(robot, color):
    print(f"\n  Place the {color.upper()} block on the floor in front of the robot.")

    while True:
        input("  Press ENTER when block is in place...")

        frame = robot.camera.get_frame()
        if frame is None:
            print("  No frame - try again.")
            continue

        center = find_block_center(frame)
        h, w = frame.shape[:2]

        if center is None:
            cx, cy = w // 2, h // 2 + 60
            save_preview(frame, cx, cy, color, found=False)
            print(f"  Could not auto-detect block. Preview saved to {SNAP_PATH}")
            print("  Make sure the block is well-lit and on the dark mat.")
            retry = input("  Try again? (y/n): ").strip().lower()
            if retry != 'y':
                print("  Skipping auto-detect, using frame center.")
                cx, cy = w // 2, h // 2 + 60
                break
            continue

        cx, cy = center
        save_preview(frame, cx, cy, color, found=True)
        print(f"  Block detected at pixel ({cx}, {cy}). Preview saved to {SNAP_PATH}")
        confirm = input("  Does the green box cover the block? (y/n): ").strip().lower()
        if confirm == 'y':
            break
        print("  Repositioning - try again.")

    print(f"  Sampling {SAMPLES} frames", end='', flush=True)

    all_pixels = []
    count = 0
    last_t = 0
    half = CROP_PX // 2

    while count < SAMPLES:
        frame = robot.camera.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue
        now = time.time()
        if now - last_t < INTERVAL:
            time.sleep(0.02)
            continue
        last_t = now

        fh, fw = frame.shape[:2]
        x1 = max(0, cx - half)
        y1 = max(0, cy - half)
        x2 = min(fw, cx + half)
        y2 = min(fh, cy + half)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        lab = cv2.cvtColor(crop, cv2.COLOR_BGR2LAB)
        all_pixels.append(lab.reshape(-1, 3))
        count += 1
        print('.', end='', flush=True)

    print(' done')

    pixels = np.vstack(all_pixels).astype(float)
    mean   = pixels.mean(axis=0)
    std    = pixels.std(axis=0)

    lo = np.clip(mean - STD_MARGIN * std - FIXED_PAD, 0, 255).astype(int)
    hi = np.clip(mean + STD_MARGIN * std + FIXED_PAD, 0, 255).astype(int)

    print(f"  Mean   L={mean[0]:.0f}  A={mean[1]:.0f}  B={mean[2]:.0f}")
    print(f"  StdDev L={std[0]:.1f}  A={std[1]:.1f}  B={std[2]:.1f}")
    print(f"  Range  L={lo[0]}-{hi[0]}  A={lo[1]}-{hi[1]}  B={lo[2]}-{hi[2]}")

    return {'lower': tuple(lo.tolist()), 'upper': tuple(hi.tolist())}


def main():
    print("=" * 60)
    print("LAB COLOR SAMPLING")
    print("=" * 60)
    print()

    with Robot() as robot:
        print("Moving arm to camera-down position...")
        robot.arm.camera_down()
        time.sleep(1.0)
        print("Ready.")

        results = {}
        for color in COLORS:
            results[color] = sample_color(robot, color)

    print()
    print("=" * 60)
    print("RESULTS - paste into block_detect.py")
    print("=" * 60)
    print()
    print("LAB_RANGES = {")
    for color, r in results.items():
        lo, hi = r['lower'], r['upper']
        print(f"    '{color}': {{")
        print(f"        'lower': ({lo[0]}, {lo[1]}, {lo[2]}),")
        print(f"        'upper': ({hi[0]}, {hi[1]}, {hi[2]}),")
        print(f"    }},")
    print("}")


if __name__ == '__main__':
    main()
