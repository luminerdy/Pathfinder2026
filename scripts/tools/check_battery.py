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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board, PLATFORM
from lib.battery import read_voltage, runtime_minimum, status_for_voltage


def check_battery(strict=False, minimum_voltage=None):
    """Check battery voltage and display status."""
    try:
        board = get_board()
        time.sleep(0.5)
        volts = read_voltage(board)

        if volts is None:
            print("ERROR: Cannot read battery voltage")
            if strict:
                sys.exit(1)
            return None

        minimum_voltage = minimum_voltage or runtime_minimum(PLATFORM)
        status, message, safe = status_for_voltage(volts, PLATFORM)

        print("Platform: %s" % PLATFORM)
        print("Battery:  %.2fV" % volts)
        print("Status:   %s" % status)
        print("Note:     %s" % message)

        if strict and not safe:
            print("\nERROR: Battery below minimum (%.1fV)" % minimum_voltage)
            sys.exit(1)

        return volts

    except Exception as e:
        print("ERROR: %s" % e)
        if strict:
            sys.exit(1)
        return None


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv
    print("Pathfinder2026 Battery Check")
    print("-" * 40)
    voltage = check_battery(strict=strict_mode)
