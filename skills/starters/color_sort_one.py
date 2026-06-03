#!/usr/bin/env python3
"""
Color Sort One Block (⭐⭐⭐ Hard)

Pick up one colored block and deliver it to the matching basket.

How it works:
  1. Scan for a block (any color, or specify one)
  2. Identify the color → look up matching basket tag
  3. Drive to block and pick it up (bump_grab)
  4. Navigate to matching basket (with obstacle avoidance)
  5. Drop block in basket
  6. Back up

This is one complete scoring cycle worth 15 points.

CUSTOMIZE: Change TARGET_COLOR to focus on specific blocks.
CUSTOMIZE: Change BASKET_TAGS if your field uses different tag IDs.
CUSTOMIZE: Adjust navigation parameters for your field.

Usage:
    python3 color_sort_one.py          # Pick up any block
    python3 color_sort_one.py red      # Red block only
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from robot import Robot
from lib.arm_positions import POS_PICKUP_DOWN, POS_PICKUP_GRAB, POS_LIFT
from skills.block_detect import BlockDetector
import pupil_apriltags as apriltag

# ============================================================
# CUSTOMIZE THESE
# ============================================================

# Which color to pick up? None = any, or 'red', 'yellow', 'blue'
TARGET_COLOR = None

# Basket-to-tag mapping (match your field setup)
BASKET_TAGS = {
    'blue':   578,
    'yellow': 579,
    'red':    580,
}

DRIVE_POWER = 40
ROTATION_POWER = 35

# ============================================================
# STEPS
# ============================================================

def step1_find_block(robot, detector, color=None):
    """Scan and face a colored block. Returns the color found."""
    print("STEP 1: Find block")

    robot.arm.camera_forward()
    time.sleep(0.5)

    colors_to_find = [color] if color else ['red', 'yellow', 'blue']

    for step in range(24):
        frame = robot.camera.get_frame()
        if frame is None: continue

        for c in colors_to_find:
            blocks = detector.detect(frame, colors=[c])
            if blocks and blocks[0].confidence >= 0.5:
                b = blocks[0]
                if abs(b.offset_from_center) < 80:
                    print("  Found %s block (offset=%+d)" % (c, b.offset_from_center))
                    return c

                # Rotate toward
                if b.offset_from_center > 0:
                    robot.rotate_right(ROTATION_POWER)
                else:
                    robot.rotate_left(ROTATION_POWER)
                time.sleep(0.08 if abs(b.offset_from_center) < 150 else 0.15)
                robot.stop()
                time.sleep(0.3)
                break
        else:
            robot.rotate_right(ROTATION_POWER)
            time.sleep(0.25)
            robot.stop()
            time.sleep(0.3)

    print("  No block found")
    return None


def step2_pickup(robot, detector, color):
    """Drive to block and pick it up."""
    print("STEP 2: Pick up %s block" % color)

    frame = robot.camera.get_frame()
    est_dist = 30
    if frame is not None:
        blocks = detector.detect(frame, colors=[color])
        if blocks:
            est_dist = blocks[0].estimated_distance_mm / 10.0

    drive_time = max(0.5, min((est_dist + 5) / 15.0, 4.0))
    print("  Driving %.1fs toward block (~%.0fcm)" % (drive_time, est_dist))

    robot.drive(DRIVE_POWER, DRIVE_POWER - 3, DRIVE_POWER, DRIVE_POWER - 3)
    time.sleep(drive_time)
    robot.stop()
    time.sleep(0.3)

    # Tiny backup
    robot.backward(30)
    time.sleep(0.12)
    robot.stop()
    time.sleep(0.3)

    # Grab
    print("  Lowering arm (open)...")
    robot.arm.move(POS_PICKUP_DOWN, 1000)
    time.sleep(0.5)

    print("  Closing gripper...")
    robot.arm.move(POS_PICKUP_GRAB, 400)
    time.sleep(0.5)

    print("  Lifting...")
    robot.arm.move(POS_LIFT, 1000)
    time.sleep(0.5)

    print("  Picked up! (hopefully)")
    return True


def step3_navigate_to_basket(robot, color):
    """Navigate to the matching colored basket."""
    tag_id = BASKET_TAGS[color]
    print("STEP 3: Navigate to %s basket (Tag %d)" % (color, tag_id))

    def detect_tags(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        det = apriltag.Detector(families='tag36h11')
        return det.detect(gray)

    def tag_area(tag):
        corners = tag.corners
        n = len(corners)
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1] - corners[j][0] * corners[i][1]
        return abs(area) / 2

    # Keep gripper closed while navigating
    robot.arm.move(POS_LIFT, 800)

    for cycle in range(100):
        robot.stop()
        time.sleep(0.05)

        frame = robot.camera.get_frame()
        if frame is None: continue

        tags = detect_tags(frame)
        tag = None
        for t in tags:
            if t.tag_id == tag_id:
                tag = t
                break

        if tag is None:
            robot.rotate_right(ROTATION_POWER)
            time.sleep(0.20)
            robot.stop()
            time.sleep(0.15)
            continue

        offset = tag.center[0] - 320
        area = tag_area(tag)

        if cycle % 10 == 0:
            print("  Tag %d: offset=%+d area=%.0f" % (tag_id, int(offset), area))

        # Arrived?
        if area >= 5000 and abs(offset) < 100:
            robot.stop()
            print("  ARRIVED at basket!")
            return True

        # Steer
        if abs(offset) > 100:
            if offset > 0:
                robot.rotate_right(ROTATION_POWER)
            else:
                robot.rotate_left(ROTATION_POWER)
            time.sleep(min(0.10, abs(offset) / 2000.0))
            robot.stop()
        else:
            robot.forward(DRIVE_POWER)
            time.sleep(0.25)

    print("  Navigation timeout")
    return False


def step4_deliver(robot):
    """Drop block in basket."""
    print("STEP 4: Deliver")

    # Lower arm, open gripper, retract
    robot.arm.gentle_place()

    # Back up
    print("  Backing up...")
    robot.backward(DRIVE_POWER)
    time.sleep(1.5)
    robot.stop()

    print("  DELIVERED!")


# ============================================================
# MAIN
# ============================================================

def main():
    global TARGET_COLOR
    if len(sys.argv) > 1:
        TARGET_COLOR = sys.argv[1].lower()

    print("=" * 50)
    print("COLOR SORT: One Block")
    print("Target: %s" % (TARGET_COLOR or "any"))
    print("=" * 50)

    detector = BlockDetector()

    with Robot() as robot:
        try:
            # Step 1: Find
            color = step1_find_block(robot, detector, TARGET_COLOR)
            if not color:
                print("\nNo block found. Try repositioning robot.")
                return

            basket_tag = BASKET_TAGS[color]
            print("  %s -> Tag %d" % (color.upper(), basket_tag))

            # Step 2: Pickup
            step2_pickup(robot, detector, color)

            # Step 3: Navigate
            if not step3_navigate_to_basket(robot, color):
                print("\nCouldn't reach basket. Block may still be in gripper.")
                return

            # Step 4: Deliver
            step4_deliver(robot)

            print("\n" + "=" * 50)
            print("SUCCESS! %s block -> %s basket (15 pts!)" % (color.upper(), color))
            print("=" * 50)

        except KeyboardInterrupt:
            print("\nStopped")

if __name__ == '__main__':
    main()
