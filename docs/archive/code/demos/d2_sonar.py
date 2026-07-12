"""
D2 - Sonar Distance Detection
Introduction to ultrasonic sensor and obstacle detection
"""

import time
import logging

logger = logging.getLogger(__name__)


def _read_cm(sonar):
    distance_mm = sonar.get_distance()
    return distance_mm / 10.0 if distance_mm is not None else None


def _filtered_cm(sonar, samples=10):
    readings = []
    for _ in range(samples):
        distance_cm = _read_cm(sonar)
        if distance_cm is not None:
            readings.append(distance_cm)
        time.sleep(0.05)

    if not readings:
        return None

    readings.sort()
    return readings[len(readings) // 2]


def _motion_detected(sonar, threshold_cm=5, duration_s=2):
    start = time.time()
    previous = _read_cm(sonar)

    while time.time() - start < duration_s:
        current = _read_cm(sonar)
        if previous is not None and current is not None:
            if abs(current - previous) >= threshold_cm:
                return True
        previous = current
        time.sleep(0.1)

    return False


def _explore(robot, duration_s=15.0, speed=40, threshold_cm=20):
    start = time.time()

    while time.time() - start < duration_s:
        distance_cm = _read_cm(robot.sonar)

        if distance_cm is not None and distance_cm < threshold_cm:
            print(f"   Obstacle at {distance_cm:.1f} cm. Turning...")
            robot.stop()
            robot.sonar.set_led_color(255, 0, 0)
            time.sleep(0.2)
            robot.rotate_right(speed)
            time.sleep(0.6)
        else:
            robot.sonar.set_led_color(0, 255, 0)
            robot.forward(speed)
            time.sleep(0.2)

    robot.stop()


def run(robot):
    """
    D2 Demo: Sonar sensor and obstacle avoidance

    Teaches:
    - Distance measurement
    - Obstacle detection
    - RGB indicators
    - Collision avoidance
    """
    logger.info("=== D2: Sonar Demo ===")

    if robot.sonar is None:
        print("Error: Sonar not available")
        return

    try:
        # 1. Basic distance reading
        print("\n1. Reading distance (10 samples)...")
        for i in range(10):
            dist = _read_cm(robot.sonar)
            if dist is not None:
                print(f"   Sample {i+1}: {dist:.1f} cm")
                robot.sonar.set_led_by_distance(dist * 10.0)
            time.sleep(0.5)

        robot.sonar.off()
        time.sleep(1)

        # 2. Filtered distance
        print("\n2. Filtered distance measurement...")
        filtered = _filtered_cm(robot.sonar, samples=10)
        if filtered is not None:
            print(f"   Median distance: {filtered:.1f} cm")
        time.sleep(1)

        # 3. Obstacle detection test
        print("\n3. Obstacle detection test (20cm threshold)...")
        print("   Place hand in front of sensor...")
        for i in range(10):
            dist = _read_cm(robot.sonar)
            if dist is not None and dist < 20:
                print(f"   OBSTACLE DETECTED at {dist:.1f} cm!" if dist else "   OBSTACLE DETECTED!")
                robot.sonar.set_led_color(255, 0, 0)  # Red
            else:
                print(f"   Clear ({dist:.1f} cm)" if dist else "   Clear (no reading)")
                robot.sonar.set_led_color(0, 255, 0)  # Green
            time.sleep(0.5)

        robot.sonar.off()
        time.sleep(1)

        # 4. Motion detection
        print("\n4. Motion detection (wave hand for 2 seconds)...")
        if _motion_detected(robot.sonar, threshold_cm=5, duration_s=2):
            print("   Motion detected!")
        else:
            print("   No motion detected")
        time.sleep(1)

        # 5. Move with obstacle avoidance
        print("\n5. Forward movement with obstacle avoidance...")
        print("   WARNING: robot will move. Clear a 4-foot by 4-foot area on the floor.")
        print("   Robot will stop if obstacle within 15cm")

        start = time.time()
        stopped_for_obstacle = False
        robot.forward(40)

        while time.time() - start < 5.0:
            dist = _read_cm(robot.sonar)
            if dist is not None and dist < 15:
                stopped_for_obstacle = True
                break
            time.sleep(0.1)

        robot.stop()

        if stopped_for_obstacle:
            print("   Movement stopped - obstacle detected!")
        else:
            print("   Movement completed successfully")

        time.sleep(1)

        # 6. Autonomous exploration
        print("\n6. Autonomous exploration (15 seconds)...")
        print("   WARNING: robot will move. Clear a 4-foot by 4-foot area on the floor.")
        print("   Robot will explore and avoid obstacles")
        _explore(robot, duration_s=15.0, speed=40)

        print("\nD2 Demo complete!")

    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        robot.stop()
        robot.sonar.off()


if __name__ == '__main__':
    print("Run via: python pathfinder.py --demo d2_sonar")
