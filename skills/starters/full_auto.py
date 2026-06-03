#!/usr/bin/env python3
"""
Full Autonomous Loop (⭐⭐⭐⭐ Expert)

Complete autonomous competition routine:
  1. Find nearest block of any color
  2. Pick it up
  3. Navigate to matching color basket
  4. Deliver
  5. Return to block zone
  6. REPEAT until time runs out or no blocks left

This is the endgame template. A working version of this can score
100+ points in a 10-minute match with autonomous bonus.

CUSTOMIZE: Change PRIORITIES for which colors to target first.
CUSTOMIZE: Adjust timing, power, and navigation parameters.
CUSTOMIZE: Add battery monitoring to return to start when low.

Usage:
    python3 full_auto.py              # Run autonomous loop
    python3 full_auto.py red          # Only target red blocks
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

# Color priority: which blocks to target first
PRIORITIES = ['red', 'yellow', 'blue']

# Basket-to-tag mapping
BASKET_TAGS = {
    'blue':   578,
    'yellow': 579,
    'red':    580,
}

# Return point: tag to navigate to after delivery (back to block zone)
RETURN_TAG = 582    # South wall tag — near block zone / start zones

# Power and speed
DRIVE_POWER = 40
ROTATION_POWER = 35

# Battery — stop if too low
BATTERY_MIN = 7.2   # Return to start below this

# Timing
MAX_CYCLE_TIME = 120    # Max seconds per pickup-deliver cycle
MATCH_TIME = 600        # 10 minutes total (stop after this)

# ============================================================
# REUSABLE STEPS (import or modify these)
# ============================================================

def scan_for_block(robot, detector, priorities):
    """Scan for blocks in priority order. Returns color or None."""
    robot.arm.camera_forward()

    for step in range(24):
        frame = robot.camera.get_frame()
        if frame is None: continue

        for color in priorities:
            blocks = detector.detect(frame, colors=[color])
            if blocks and blocks[0].confidence >= 0.5:
                b = blocks[0]
                if abs(b.offset_from_center) < 80:
                    return color
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
    return None


def pickup_block(robot, detector, color):
    """Drive to block and grab it."""
    frame = robot.camera.get_frame()
    est = 30
    if frame is not None:
        blocks = detector.detect(frame, colors=[color])
        if blocks: est = blocks[0].estimated_distance_mm / 10.0

    t = max(0.5, min((est + 5) / 15.0, 4.0))
    robot.drive(DRIVE_POWER, DRIVE_POWER - 3, DRIVE_POWER, DRIVE_POWER - 3)
    time.sleep(t)
    robot.stop()

    robot.backward(30)
    time.sleep(0.12)
    robot.stop()
    time.sleep(0.3)

    robot.arm.move(POS_PICKUP_DOWN, 1000)
    time.sleep(0.5)
    robot.arm.move(POS_PICKUP_GRAB, 400)
    time.sleep(0.5)
    robot.arm.move(POS_LIFT, 1000)


def navigate_to_tag(robot, tag_id, tag_area_target=5000):
    """Navigate to an AprilTag. Returns True if reached."""
    robot.arm.move(POS_LIFT, 800)  # Keep holding block

    def detect(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        det = apriltag.Detector(families='tag36h11')
        return det.detect(gray)

    def area(tag):
        c = tag.corners
        a = 0
        for i in range(4):
            j = (i+1) % 4
            a += c[i][0]*c[j][1] - c[j][0]*c[i][1]
        return abs(a) / 2

    for cycle in range(100):
        robot.stop()
        time.sleep(0.05)

        frame = robot.camera.get_frame()
        if frame is None: continue

        tags = detect(frame)
        tag = None
        for t in tags:
            if t.tag_id == tag_id: tag = t; break

        if not tag:
            robot.rotate_right(ROTATION_POWER)
            time.sleep(0.20)
            robot.stop()
            time.sleep(0.15)
            continue

        offset = tag.center[0] - 320
        a = area(tag)

        if a >= tag_area_target and abs(offset) < 100:
            robot.stop()
            return True

        if abs(offset) > 100:
            if offset > 0:
                robot.rotate_right(ROTATION_POWER)
            else:
                robot.rotate_left(ROTATION_POWER)
            time.sleep(min(0.10, abs(offset)/2000.0))
            robot.stop()
        else:
            robot.forward(DRIVE_POWER)
            time.sleep(0.25)

    robot.stop()
    return False


def deliver_block(robot):
    """Gentle place into basket."""
    robot.arm.gentle_place()
    robot.backward(DRIVE_POWER)
    time.sleep(1.5)
    robot.stop()


# ============================================================
# MAIN AUTONOMOUS LOOP
# ============================================================

def main():
    target_only = None
    if len(sys.argv) > 1:
        target_only = sys.argv[1].lower()

    priorities = [target_only] if target_only else PRIORITIES

    print("=" * 60)
    print("FULL AUTONOMOUS LOOP")
    print("Priorities: %s" % priorities)
    print("Match time: %d seconds" % MATCH_TIME)
    print("=" * 60)

    detector = BlockDetector()

    with Robot() as robot:
        print("Battery: %.2fV" % (robot.battery or 0))

        v = robot.battery
        if v and v < BATTERY_MIN:
            print("Battery too low!")
            return

        match_start = time.time()
        blocks_delivered = 0

        try:
            while True:
                elapsed = time.time() - match_start
                remaining = MATCH_TIME - elapsed

                if remaining <= 0:
                    print("\n  TIME'S UP!")
                    break

                print("\n--- CYCLE %d (%.0fs remaining) ---" % (blocks_delivered + 1, remaining))

                # Battery check
                v = robot.battery
                if v and v < BATTERY_MIN:
                    print("  Battery low (%.2fV) — stopping" % v)
                    break

                cycle_start = time.time()

                # STEP 1: Find block
                print("  Finding block...")
                color = scan_for_block(robot, detector, priorities)
                if not color:
                    print("  No blocks found — done!")
                    break

                basket_tag = BASKET_TAGS[color]
                print("  Found %s -> Tag %d" % (color.upper(), basket_tag))

                # STEP 2: Pickup
                print("  Picking up...")
                pickup_block(robot, detector, color)

                # STEP 3: Navigate to basket
                print("  Navigating to %s basket..." % color)
                if navigate_to_tag(robot, basket_tag):
                    # STEP 4: Deliver
                    print("  Delivering...")
                    deliver_block(robot)
                    blocks_delivered += 1

                    cycle_time = time.time() - cycle_start
                    print("  SCORED! (%s, %.1fs)" % (color.upper(), cycle_time))
                else:
                    print("  Couldn't reach basket — dropping block")
                    robot.arm.gripper_open()
                    time.sleep(0.5)
                    robot.arm.camera_forward()

                # STEP 5: Return to block zone (optional — skip if time is short)
                if remaining > 60:
                    print("  Returning to block zone...")
                    navigate_to_tag(robot, RETURN_TAG, tag_area_target=3000)

        except KeyboardInterrupt:
            print("\nStopped")

        elapsed = time.time() - match_start
        print()
        print("=" * 60)
        print("MATCH COMPLETE")
        print("  Blocks delivered: %d" % blocks_delivered)
        print("  Time: %.1f seconds" % elapsed)
        print("  Points (est): %d" % (blocks_delivered * 15))
        print("  Autonomous bonus: %d" % (blocks_delivered * 10))
        print("  TOTAL (est): %d" % (blocks_delivered * 25))
        print("=" * 60)


if __name__ == '__main__':
    main()
