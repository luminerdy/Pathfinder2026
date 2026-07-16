#!/usr/bin/env python3
"""
Sonar Sensors Demo (Level 1: Just Run It!)

Demonstrates 6 sonar capabilities:
1. Distance Reading (10 samples with RGB feedback)
2. Filtered Reading (median of 10 samples)
3. Obstacle Detection (red if <20cm, green if clear)
4. Range Zones (red/yellow/green for danger/caution/safe)
5. Safe Movement (drives forward, stops if obstacle)
6. Obstacle Avoidance (backs up and turns when blocked)

No code changes needed - just run and watch!

Usage:
    python3 run_demo.py

Safety:
    - Clear a 4-foot by 4-foot area around the robot
    - Put the robot on the floor only. It can drive off a table.
    - Press Ctrl+C to emergency stop

Press Ctrl+C to stop at any time.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board
from lib.sonar import Sonar


# TEAM TUNING: Change one value at a time, save, and run this demo again.
DANGER_DISTANCE_CM = 15
CAUTION_DISTANCE_CM = 30
OBSTACLE_DISTANCE_CM = 20
SAFE_MOVE_SPEED = 35
SAFE_MOVE_DURATION_SECONDS = 5.0
AVOID_MOVE_SPEED = 30
AVOID_DEMO_DURATION_SECONDS = 10.0
BACKUP_DURATION_SECONDS = 0.5
TURN_DURATION_SECONDS = 0.6


def stop_motors(board):
    """Stop all drive motors."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def read_cm(sonar):
    """Read sonar distance in centimeters."""
    distance_mm = sonar.get_distance()
    return distance_mm / 10.0 if distance_mm is not None else None


def filtered_cm(sonar, samples=10):
    """Median-filter sonar readings in centimeters."""
    readings = []
    for _ in range(samples):
        distance = read_cm(sonar)
        if distance is not None:
            readings.append(distance)
        time.sleep(0.05)

    if not readings:
        return None

    readings.sort()
    return readings[len(readings) // 2]


def set_zone_led(sonar, distance_cm):
    """Set sonar LEDs based on distance in centimeters."""
    if distance_cm is None:
        sonar.off()
    elif distance_cm < DANGER_DISTANCE_CM:
        sonar.set_led_color(255, 0, 0)
    elif distance_cm < CAUTION_DISTANCE_CM:
        sonar.set_led_color(255, 255, 0)
    else:
        sonar.set_led_color(0, 255, 0)

def main():
    print("=" * 60)
    print("SONAR SENSORS DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo shows 6 sonar capabilities.")
    print()
    print("SAFETY:")
    print("  - Clear a 4-foot by 4-foot area around the robot")
    print("  - Put the robot on the floor only. It can drive off a table.")
    print("  - Press Ctrl+C to emergency stop")
    print()
    input("Press Enter to start demo...")
    print()

    board = get_board()
    sonar = Sonar()

    try:
        # Demo 1: Distance Reading
        print("[1/6] Distance Reading (10 samples)")
        print("  Watch RGB LEDs change color...")
        for i in range(10):
            dist = read_cm(sonar)
            if dist is not None:
                print(f"    Sample {i+1}: {dist:.1f} cm")
                set_zone_led(sonar, dist)
            time.sleep(0.5)
        sonar.off()
        time.sleep(2)

        # Demo 2: Filtered Reading
        print("\n[2/6] Filtered Reading (median of 10)")
        filtered = filtered_cm(sonar, samples=10)
        if filtered is not None:
            print(f"    Median distance: {filtered:.1f} cm")
        else:
            print("    No sonar reading")
        time.sleep(2)

        # Demo 3: Obstacle Detection
        print("\n[3/6] Obstacle Detection Test")
        print("  Wave hand in front of sensor...")
        print(f"  Red LED = obstacle <{OBSTACLE_DISTANCE_CM}cm, Green = clear")
        for i in range(15):
            dist = read_cm(sonar)
            if dist is not None and dist < OBSTACLE_DISTANCE_CM:
                print(f"    OBSTACLE at {dist:.1f} cm!" if dist else "    OBSTACLE!")
                sonar.set_led_color(255, 0, 0)
            else:
                print(f"    Clear ({dist:.1f} cm)" if dist else "    Clear")
                sonar.set_led_color(0, 255, 0)
            time.sleep(0.3)
        sonar.off()
        time.sleep(2)

        # Demo 4: Range Zones
        print("\n[4/6] Range Zones (red/yellow/green)")
        print(f"  Red (<{DANGER_DISTANCE_CM}cm) = DANGER")
        print(f"  Yellow ({DANGER_DISTANCE_CM}-{CAUTION_DISTANCE_CM}cm) = CAUTION")
        print(f"  Green (>{CAUTION_DISTANCE_CM}cm) = SAFE")
        print("  Move hand to see zones...")
        for i in range(15):
            dist = read_cm(sonar)
            if dist is not None:
                if dist < DANGER_DISTANCE_CM:
                    zone = "DANGER"
                elif dist < CAUTION_DISTANCE_CM:
                    zone = "CAUTION"
                else:
                    zone = "SAFE"
                set_zone_led(sonar, dist)
                print(f"    {dist:.1f} cm - {zone}")
            time.sleep(0.3)
        sonar.off()
        time.sleep(2)

        # Demo 5: Safe Movement
        print("\n[5/6] Safe Movement Test")
        print(f"  Robot will drive forward at {SAFE_MOVE_SPEED}% speed")
        print(f"  Will STOP if obstacle detected <{DANGER_DISTANCE_CM}cm")
        print("  Try blocking its path...")
        time.sleep(2)

        start_time = time.time()
        max_duration = SAFE_MOVE_DURATION_SECONDS
        speed = SAFE_MOVE_SPEED
        stop_threshold = DANGER_DISTANCE_CM

        while time.time() - start_time < max_duration:
            dist = read_cm(sonar)
            if dist is not None and dist < stop_threshold:
                print(f"    STOPPING! Obstacle at {dist:.1f} cm")
                stop_motors(board)
                sonar.set_led_color(255, 0, 0)
                break
            else:
                # Drive forward
                board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])
                sonar.set_led_color(0, 255, 0)
            time.sleep(0.05)

        stop_motors(board)
        sonar.off()
        time.sleep(2)

        # Demo 6: Obstacle Avoidance
        print("\n[6/6] Obstacle Avoidance")
        print("  Robot will explore and avoid obstacles")
        print("  Block its path to see avoidance behavior")
        time.sleep(2)

        start_time = time.time()
        max_duration = AVOID_DEMO_DURATION_SECONDS
        speed = AVOID_MOVE_SPEED

        while time.time() - start_time < max_duration:
            dist = read_cm(sonar)

            if dist is not None and dist < OBSTACLE_DISTANCE_CM:
                # Obstacle! Back up and turn
                print(f"    Obstacle at {dist:.1f} cm - backing up...")
                # Back up
                board.set_motor_duty([(1, -speed), (2, -speed), (3, -speed), (4, -speed)])
                time.sleep(BACKUP_DURATION_SECONDS)
                # Turn right
                print("    Turning right...")
                board.set_motor_duty([(1, speed), (2, -speed), (3, speed), (4, -speed)])
                time.sleep(TURN_DURATION_SECONDS)
                stop_motors(board)
                time.sleep(0.3)
            else:
                # Clear - drive forward
                board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])

            time.sleep(0.05)

        stop_motors(board)
        sonar.off()

        print()
        print("=" * 60)
        print("DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("What you just saw:")
        print("  [OK] Distance measurement (ultrasonic echo timing)")
        print("  [OK] RGB feedback (visual distance indicator)")
        print("  [OK] Obstacle detection (threshold logic)")
        print("  [OK] Range zones (danger/caution/safe)")
        print("  [OK] Safe movement (stops before collision)")
        print("  [OK] Avoidance behavior (backs up and turns)")
        print()
        print("Next steps:")
        print("  - Try editing the TEAM TUNING constants near the top of run_demo.py")
        print("  - Read SKILL.md to understand how ultrasonic works")
        print("  - Integrate with mecanum drive (mecanum + sonar = safe navigation)")

        # Victory beep
        board.set_buzzer(1000, 0.1, 0.1, 2)

    except KeyboardInterrupt:
        print("\nDemo stopped by user (Ctrl+C)")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        stop_motors(board)
        sonar.off()
        print("\nMotors stopped, LEDs off. Demo complete.")

if __name__ == "__main__":
    main()
