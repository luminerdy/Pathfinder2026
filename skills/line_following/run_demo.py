#!/usr/bin/env python3
"""
Line Following Demo

Follow a lime green tape line on the floor.

Usage:
    python3 run_demo.py

SAFETY: Robot will drive! Clear the path.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.line_following.line_follower import LineFollower


def callback(detection, strafe, turn):
    """Print a short status line every few frames while the robot follows."""
    def center(value):
        return '---' if value is None else str(value)

    print("  far=%s mid=%s near=%s err=%+d heading=%+d strafe=%+.1f turn=%+.1f" % (
        center(detection['far_cx']), center(detection['mid_cx']),
        center(detection['near_cx']), detection['error'],
        detection['heading_error'], strafe, turn))


def main():
    print("=" * 60)
    print("LINE FOLLOWING DEMO")
    print("=" * 60)
    print()
    print("Follow a lime green tape line on the floor.")
    print()
    print("SAFETY:")
    print("  - Lay lime green tape on floor in a line or curve")
    print("  - Place robot at start of line")
    print("  - Clear the path")
    print("  - Press Ctrl+C to stop")
    print()
    input("Press Enter to start...")
    print()

    # LineFollower handles camera setup, color detection, and motor correction.
    # This demo file stays small so students can start here, then open
    # line_follower.py to see how the control loop works.
    follower = LineFollower()

    try:
        print("Following line...")
        print("-" * 40)
        # The callback prints the line center, steering error, strafe command,
        # and turn command so teams can connect camera data to robot movement.
        result = follower.follow(timeout=30, callback=callback)

        print()
        print("=" * 60)
        if result['reason'] == 'line_ended':
            print("LINE ENDED - Reached end of tape!")
        elif result['reason'] == 'timeout':
            print("TIMEOUT - Still on line after %ds" % result['duration'])
        elif result['reason'] == 'interrupted':
            print("STOPPED by user")
        
        print("  Frames processed: %d" % result['frames'])
        print("  Duration: %.1fs" % result['duration'])
        if result['frames'] > 0 and result['duration'] > 0:
            print("  FPS: %.1f" % (result['frames'] / result['duration']))
        print("=" * 60)
        print()
        print("What you learned:")
        print("  [OK] HSV thresholding detects colored line on floor")
        print("  [OK] Centroid calculation finds line center")
        print("  [OK] Mecanum strafe keeps the robot centered over the line")
        print("  [OK] Small turn corrections help follow curves")
        print("  [OK] End-of-line detection stops when tape ends")

    except KeyboardInterrupt:
        print("\nStopped by user")

    finally:
        # Always stop motors and release the camera even if Ctrl+C is pressed.
        follower.cleanup()

if __name__ == "__main__":
    main()
