#!/usr/bin/env python3
"""
Check sonar distance readings.

Run from the repository root:
    python3 scripts/tools/check_sonar.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from lib.sonar import Sonar


def main():
    print("Pathfinder2026 Sonar Check")
    print("-" * 40)
    print("This reads the sonar five times and updates the sonar LEDs.")
    print("Run it once, move your hand in front of the sonar, then run it again.")
    print()

    sonar = Sonar()

    try:
        readings = []
        for i in range(5):
            distance_mm = sonar.get_distance()
            if distance_mm is None:
                print("Reading %d: no reading" % (i + 1))
            else:
                readings.append(distance_mm)
                print("Reading %d: %.0f mm (%.1f cm)" % (i + 1, distance_mm, distance_mm / 10.0))
                sonar.set_led_by_distance(distance_mm)
            time.sleep(0.5)

        print()
        if readings:
            avg = sum(readings) / len(readings)
            print("Average: %.0f mm (%.1f cm)" % (avg, avg / 10.0))
            print("Sonar check complete")
        else:
            print("ERROR: No valid sonar readings")
            print("Check I2C, sonar cable, and address 77 with: sudo i2cdetect -y 1")
            sys.exit(1)

    finally:
        sonar.off()


if __name__ == "__main__":
    main()
