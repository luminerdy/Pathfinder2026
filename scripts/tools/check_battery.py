#!/usr/bin/env python3
"""
Quick battery voltage check for Pathfinder2026 robot.

Usage:
    python3 check_battery.py           # Display voltage
    python3 check_battery.py --strict  # Exit 1 if below platform runtime minimum
"""

import sys
import os
import time

# Add the repository root so this tool can import lib/ when run from anywhere.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board, PLATFORM
from lib.battery import read_voltage, runtime_minimum, status_for_voltage


def check_battery(strict=False, minimum_voltage=None):
    """Check battery voltage and display status."""
    try:
        # The board object talks to the motor/servo controller on the robot.
        board = get_board()
        time.sleep(0.5)
        volts = read_voltage(board)

        if volts is None:
            print("ERROR: Cannot read battery voltage")
            print("Check robot power, battery connection, and the motor board connection before continuing.")
            if strict:
                sys.exit(1)
            return None

        # Different robot versions can have different safe runtime thresholds.
        minimum_voltage = minimum_voltage or runtime_minimum(PLATFORM)
        status, message, safe = status_for_voltage(volts, PLATFORM)

        print("Platform: %s" % PLATFORM)
        print("Battery:  %.2fV" % volts)
        print("Status:   %s" % status)
        print("Note:     %s" % message)

        # Strict mode is useful in demos: stop instead of running on a low battery.
        if strict and not safe:
            print("\nERROR: Battery below minimum (%.1fV)" % minimum_voltage)
            sys.exit(1)

        return volts

    except Exception as e:
        print("ERROR: %s" % e)
        print("Check robot power, battery connection, and the motor board connection before continuing.")
        if strict:
            sys.exit(1)
        return None


if __name__ == "__main__":
    # Normal mode reports the voltage. --strict also returns an error code if low.
    strict_mode = "--strict" in sys.argv
    print("Pathfinder2026 Battery Check")
    print("-" * 40)
    voltage = check_battery(strict=strict_mode)
