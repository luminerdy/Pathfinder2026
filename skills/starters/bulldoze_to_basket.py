#!/usr/bin/env python3
"""
Bulldoze to Basket (⭐ Easy)

Simplest scoring strategy: drive straight at a basket,
pushing any blocks in your path. No arm needed.

How it works:
  1. Face a basket (find AprilTag on north wall)
  2. Drive forward at full speed
  3. Whatever blocks are in the way get pushed into/near the basket
  4. Back up, repeat from a different angle

Scores: 3-5 pts per block that ends up in a basket.
Not elegant, but it works.

CUSTOMIZE: Change target_tag to aim at different baskets.
CUSTOMIZE: Change DRIVE_POWER for speed vs control.
CUSTOMIZE: Add sonar checks to avoid getting stuck on barriers.

Usage:
    python3 bulldoze_to_basket.py
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from robot import Robot
import pupil_apriltags as apriltag

# ============================================================
# CUSTOMIZE THESE
# ============================================================

target_tag = 580        # Which basket? 578=blue, 579=yellow, 580=red
DRIVE_POWER = 40        # How fast to bulldoze (30=gentle, 50=aggressive)
DRIVE_TIME = 3.0        # How long to drive per push (seconds)
NUM_PUSHES = 3          # How many pushes before stopping
ROTATION_POWER = 35     # Turn speed

# ============================================================
# DON'T CHANGE BELOW (unless you know what you're doing)
# ============================================================

def detect_tags(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    det = apriltag.Detector(families='tag36h11')
    return det.detect(gray)

def find_and_face_tag(robot, tag_id):
    """Rotate until we see the target tag and it's roughly centered."""
    CENTER = 320
    TOLERANCE = 100

    for step in range(24):
        frame = robot.camera.get_frame()
        if frame is None:
            continue

        tags = detect_tags(frame)
        for t in tags:
            if t.tag_id == tag_id:
                offset = t.center[0] - CENTER
                if abs(offset) < TOLERANCE:
                    print("  Facing tag %d" % tag_id)
                    return True
                # Rotate toward tag
                if offset > 0:
                    robot.rotate_right(ROTATION_POWER)
                else:
                    robot.rotate_left(ROTATION_POWER)
                time.sleep(0.08)
                robot.stop()
                time.sleep(0.2)
                break
        else:
            # Tag not visible, blind rotate
            robot.rotate_right(ROTATION_POWER)
            time.sleep(0.2)
            robot.stop()
            time.sleep(0.2)

    print("  Could not find tag %d" % tag_id)
    return False

def bulldoze(robot):
    """Drive forward for DRIVE_TIME seconds, pushing everything in the way."""
    print("  BULLDOZE! (%.1fs at power %d)" % (DRIVE_TIME, DRIVE_POWER))
    robot.forward(DRIVE_POWER)
    time.sleep(DRIVE_TIME)
    robot.stop()

def backup(robot):
    """Back up to reset for next push."""
    print("  Backing up...")
    robot.backward(DRIVE_POWER)
    time.sleep(2.0)
    robot.stop()


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 50)
    print("BULLDOZE TO BASKET")
    print("Target: Tag %d" % target_tag)
    print("=" * 50)

    with Robot() as robot:
        robot.arm.camera_forward()

        try:
            for push in range(NUM_PUSHES):
                print("\nPush %d/%d:" % (push + 1, NUM_PUSHES))

                # Face the basket
                if find_and_face_tag(robot, target_tag):
                    # Charge!
                    bulldoze(robot)
                    # Back up for next run
                    backup(robot)
                else:
                    print("  Skipping — can't find basket")

            print("\nDone! Check if any blocks made it into the basket.")

        except KeyboardInterrupt:
            print("\nStopped")

if __name__ == '__main__':
    main()
