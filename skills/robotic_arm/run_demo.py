#!/usr/bin/env python3
"""
Robotic Arm Demo (D3 - Level 2: Safe Basics)

This demo uses only conservative, verified movements:
- Home position
- Gripper open/close
- Base rotation left/right

It intentionally avoids unverified named reach/pickup/carry poses.

Servo mapping:
  Servo 1: Gripper/Claw  (1475=closed, 2500=open)
  Servo 3: Shoulder      (500-2500)
  Servo 4: Elbow         (500-2500)
  Servo 5: Wrist         (500-2500)
  Servo 6: Base          (500-2500, 1500=center)
  Note: Servo 2 does not exist on this platform.

Usage:
    python3 run_demo.py
"""

import os
import sys
import time

# Add project root for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from lib.board import get_board


HOME_POSITION = [
    (1, 2500),  # Gripper open
    (3, 1200),  # Shoulder neutral
    (4, 1500),  # Elbow neutral
    (5, 1500),  # Wrist neutral
    (6, 1500),  # Base center
]


def move_home(board, duration_ms=1000):
    """Move the arm to the known-good home position."""
    print("  Moving to home position...")
    board.set_servo_position(duration_ms, HOME_POSITION)
    time.sleep(duration_ms / 1000.0 + 0.3)


def main():
    """Demonstrate safe arm basics."""

    print("=" * 60)
    print("ROBOTIC ARM DEMO - Safe Basics")
    print("=" * 60)
    print()
    print("This demo tests home position, gripper, and base rotation.")
    print("Keep hands clear of the arm and gripper.")
    print("Press Ctrl+C to stop at any time.")
    print("-" * 60)
    print()

    board = get_board()

    try:
        # Demo 1: Home position
        print("[Demo 1] Home Position")
        move_home(board, duration_ms=1200)
        print("  Home position complete")
        print()
        time.sleep(0.5)

        # Demo 2: Gripper control
        print("[Demo 2] Gripper Control")
        print("  Opening gripper (PWM 2500)...")
        board.set_servo_position(500, [(1, 2500)])
        time.sleep(1)

        print("  Closing gripper (PWM 1475)...")
        board.set_servo_position(500, [(1, 1475)])
        time.sleep(1)

        print("  Opening gripper again...")
        board.set_servo_position(500, [(1, 2500)])
        time.sleep(1)
        print("  Gripper control complete")
        print()
        time.sleep(0.5)

        # Demo 3: Base rotation
        print("[Demo 3] Base Rotation")
        move_home(board, duration_ms=800)

        print("  Rotating left (PWM 1300)...")
        board.set_servo_position(800, [(6, 1300)])
        time.sleep(1)

        print("  Rotating right (PWM 1700)...")
        board.set_servo_position(800, [(6, 1700)])
        time.sleep(1)

        print("  Back to center (PWM 1500)...")
        board.set_servo_position(800, [(6, 1500)])
        time.sleep(1)
        print("  Base rotation complete")
        print()

        print("Returning to home position...")
        move_home(board, duration_ms=1000)

        print()
        print("=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print()
        print("What you checked:")
        print("  [OK] Home arm position")
        print("  [OK] Gripper open/close")
        print("  [OK] Base rotation left/right")

    except KeyboardInterrupt:
        print("\nDemo stopped by user (Ctrl+C)")

    except Exception as e:
        print("\nERROR: %s" % e)
        import traceback
        traceback.print_exc()

    finally:
        print("\nReturning to home...")
        try:
            move_home(board, duration_ms=1000)
        except Exception:
            pass
        print("Done.")


if __name__ == "__main__":
    main()
