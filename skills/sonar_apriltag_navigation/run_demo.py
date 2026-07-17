#!/usr/bin/env python3
"""
Sonar-assisted AprilTag navigation demo.

This experimental Area 2 script drives toward AprilTag 583 while the forward
sonar continuously watches for fixed cardboard barriers. When a barrier is
detected, the robot strafes along the barrier until the sonar sees the edge,
then strafes a little farther so the wheels clear before resuming AprilTag
navigation.

Usage:
    python3 skills/sonar_apriltag_navigation/run_demo.py
    python3 skills/sonar_apriltag_navigation/run_demo.py --strafe-direction left

Safety:
    - The robot will drive, strafe, and turn.
    - Use only on the floor.
    - Keep hands clear of wheels, barriers, arm, and claw.
    - Press Ctrl+C to stop immediately.
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import PLATFORM
from lib.battery import is_runtime_safe, read_voltage, status_for_voltage
from skills.strafe_nav import StrafeNavigator


AREA2_TAG_ID = 583
CAMERA_FORWARD_POSITION = [
    (1, 2500),  # Claw open
    (3, 590),   # Wrist
    (4, 2450),  # Elbow
    (5, 700),   # Shoulder/camera forward
    (6, 1500),  # Base centered
]


class SonarAprilTagNavigator:
    """Navigate to one AprilTag while using sonar to clear fixed barriers."""

    def __init__(
            self,
            tag_id=AREA2_TAG_ID,
            target_distance=0.50,
            barrier_cm=28.0,
            clear_cm=55.0,
            strafe_direction='right',
            extra_clearance_seconds=0.45,
            forward_power=36,
            turn_power=35,
            strafe_power=42,
            timeout=60.0):
        self.tag_id = tag_id
        self.target_distance = target_distance
        self.barrier_cm = barrier_cm
        self.clear_cm = clear_cm
        self.strafe_direction = strafe_direction
        self.extra_clearance_seconds = extra_clearance_seconds
        self.forward_power = forward_power
        self.turn_power = turn_power
        self.strafe_power = strafe_power
        self.timeout = timeout

        self.nav = StrafeNavigator()
        self.board = self.nav.board
        self.sonar = self.nav.sonar

    def stop(self):
        """Stop all drive motors."""
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

    def cleanup(self):
        """Stop motors, release camera, and turn off sonar LEDs."""
        self.stop()
        if self.sonar is not None:
            try:
                self.sonar.off()
            except Exception:
                pass
        self.nav.cleanup()

    def set_camera_forward(self):
        """Put the arm/camera in the AprilTag viewing position."""
        self.board.set_servo_position(1000, CAMERA_FORWARD_POSITION)
        time.sleep(1.1)

    def read_sonar_cm(self, samples=3):
        """Read sonar several times and return the median distance in cm."""
        if self.sonar is None:
            return None

        readings = []
        for _ in range(samples):
            distance_mm = self.sonar.get_distance()
            if distance_mm is not None:
                readings.append(distance_mm / 10.0)
            time.sleep(0.025)

        if not readings:
            return None

        readings.sort()
        return readings[len(readings) // 2]

    def set_sonar_led(self, distance_cm):
        """Show sonar state on the sensor LEDs."""
        if self.sonar is None:
            return
        if distance_cm is None:
            self.sonar.set_led_color(0, 0, 0)
        elif distance_cm <= self.barrier_cm:
            self.sonar.set_led_color(255, 0, 0)
        elif distance_cm <= self.clear_cm:
            self.sonar.set_led_color(255, 255, 0)
        else:
            self.sonar.set_led_color(0, 255, 0)

    def drive_arc(self, forward, turn=0, strafe=0):
        """Drive using mecanum forward, turn, and strafe commands."""
        fl = forward + strafe + turn
        fr = forward - strafe - turn
        rl = forward - strafe + turn
        rr = forward + strafe - turn

        max_wheel = max(abs(fl), abs(fr), abs(rl), abs(rr), 1)
        if max_wheel > 100:
            scale = 100.0 / max_wheel
            fl *= scale
            fr *= scale
            rl *= scale
            rr *= scale

        self.board.set_motor_duty([
            (1, int(fl)), (2, int(fr)), (3, int(rl)), (4, int(rr))
        ])

    def strafe_once(self, direction_value, seconds=0.10):
        """Strafe briefly, then stop so sonar can be read again."""
        self.drive_arc(forward=0, strafe=self.strafe_power * direction_value)
        time.sleep(seconds)
        self.stop()
        time.sleep(0.04)

    def rotate_once(self, direction_value, seconds=0.08):
        """Rotate briefly while searching for or centering the AprilTag."""
        self.drive_arc(forward=0, turn=self.turn_power * direction_value)
        time.sleep(seconds)
        self.stop()
        time.sleep(0.08)

    def detect_tag(self):
        """Return (tag_id, distance_m, angle_deg), or (None, None, None)."""
        frame = self.nav._get_frame()
        if frame is None:
            return None, None, None
        tag_id, _x, _y, _z, distance, angle = self.nav._detect_tags(
            frame, target_id=self.tag_id
        )
        if tag_id is None:
            return None, None, None
        return tag_id, distance, angle

    def clear_barrier_edge(self, barrier_number):
        """
        Strafe until sonar no longer sees the barrier, then add wheel clearance.

        The course can contain several fixed boxes. This method handles one
        barrier edge and returns to the main loop so sonar can catch the next.
        """
        direction_value = 1 if self.strafe_direction == 'right' else -1
        clear_count = 0
        start = time.time()

        print()
        print("Barrier %d detected. Strafing %s to find the edge." % (
            barrier_number, self.strafe_direction))

        while time.time() - start < 8.0:
            distance_cm = self.read_sonar_cm()
            self.set_sonar_led(distance_cm)

            if distance_cm is not None and distance_cm >= self.clear_cm:
                clear_count += 1
                print("  edge check %d/3: %.1f cm" % (clear_count, distance_cm))
                if clear_count >= 3:
                    break
            else:
                clear_count = 0
                label = 'no reading' if distance_cm is None else '%.1f cm' % distance_cm
                print("  barrier still ahead: %s" % label)

            self.strafe_once(direction_value)

        self.stop()

        if clear_count < 3:
            return False, 'edge_not_found'

        print("  Edge found. Adding wheel clearance for %.2fs." % (
            self.extra_clearance_seconds))
        clearance_start = time.time()
        while time.time() - clearance_start < self.extra_clearance_seconds:
            # Keep reading sonar during the extra clearance move so a second
            # box close to the first can still be noticed immediately after.
            distance_cm = self.read_sonar_cm(samples=1)
            self.set_sonar_led(distance_cm)
            self.drive_arc(forward=0, strafe=self.strafe_power * direction_value)
            time.sleep(0.05)

        self.stop()
        time.sleep(0.15)
        return True, 'cleared'

    def navigate(self):
        """Run the sonar plus AprilTag route."""
        voltage = read_voltage(self.board)
        status, message, safe = status_for_voltage(voltage, PLATFORM)
        print("Battery: %s" % ("%.2fV" % voltage if voltage is not None else "unknown"))
        print("Status: %s - %s" % (status, message))
        if not is_runtime_safe(voltage, PLATFORM):
            return {
                'success': False,
                'reason': 'battery_not_safe',
                'barriers': 0,
                'final_distance': 0,
                'final_angle': 0,
            }

        self.nav._open_camera()
        self.set_camera_forward()

        if self.sonar is None:
            return {
                'success': False,
                'reason': 'sonar_unavailable',
                'barriers': 0,
                'final_distance': 0,
                'final_angle': 0,
            }

        start = time.time()
        barrier_count = 0
        last_distance = 0
        last_angle = 0
        search_direction = 1

        print()
        print("Navigating toward AprilTag %d with continuous sonar checks." % self.tag_id)
        print("Barrier stop: %.0f cm | clear edge: %.0f cm | strafe: %s" % (
            self.barrier_cm, self.clear_cm, self.strafe_direction))
        print("-" * 60)

        while time.time() - start < self.timeout:
            distance_cm = self.read_sonar_cm()
            self.set_sonar_led(distance_cm)

            if distance_cm is not None and 0 < distance_cm <= self.barrier_cm:
                self.stop()
                barrier_count += 1
                print("SONAR barrier %d at %.1f cm" % (barrier_count, distance_cm))
                ok, reason = self.clear_barrier_edge(barrier_count)
                if not ok:
                    return {
                        'success': False,
                        'reason': reason,
                        'barriers': barrier_count,
                        'final_distance': last_distance,
                        'final_angle': last_angle,
                    }
                continue

            tag_id, tag_distance, angle = self.detect_tag()

            if tag_id is None:
                # If the tag is not visible, rotate in small pulses. Sonar is
                # checked again before every pulse in the next loop iteration.
                print("Tag %d not visible. Searching..." % self.tag_id)
                self.rotate_once(search_direction)
                search_direction *= -1
                continue

            last_distance = tag_distance
            last_angle = angle

            print("Tag %d: %.2fm %+0.1fdeg | sonar %s" % (
                tag_id,
                tag_distance,
                angle,
                '---' if distance_cm is None else '%.0fcm' % distance_cm,
            ))

            if tag_distance <= self.target_distance and abs(angle) <= 12:
                self.stop()
                return {
                    'success': True,
                    'reason': 'reached',
                    'barriers': barrier_count,
                    'final_distance': tag_distance,
                    'final_angle': angle,
                }

            if abs(angle) > 22:
                turn = 1 if angle > 0 else -1
                self.rotate_once(turn)
                continue

            distance_error = max(0.0, tag_distance - self.target_distance)
            forward = min(max(distance_error * 85.0, 32.0), self.forward_power)
            turn = max(-12.0, min(12.0, angle * 1.0))

            # Move in short pulses. The next loop reads sonar again before the
            # robot is allowed to continue, so multiple barriers are handled.
            self.drive_arc(forward=forward, turn=turn)
            time.sleep(0.08)
            self.stop()
            time.sleep(0.04)

        self.stop()
        return {
            'success': False,
            'reason': 'timeout',
            'barriers': barrier_count,
            'final_distance': last_distance,
            'final_angle': last_angle,
        }


def parse_args():
    parser = argparse.ArgumentParser(
        description='Navigate to Area 2 AprilTag using sonar barrier edges.'
    )
    parser.add_argument('--tag-id', type=int, default=AREA2_TAG_ID,
                        help='AprilTag ID to approach. Default: 583.')
    parser.add_argument('--target-distance', type=float, default=0.50,
                        help='Stop distance from tag in meters. Default: 0.50.')
    parser.add_argument('--barrier-cm', type=float, default=28.0,
                        help='Sonar distance that means barrier ahead.')
    parser.add_argument('--clear-cm', type=float, default=55.0,
                        help='Sonar distance that means barrier edge is clear.')
    parser.add_argument('--strafe-direction', choices=('left', 'right'),
                        default='right',
                        help='Direction to strafe when a barrier is detected.')
    parser.add_argument('--extra-clearance', type=float, default=0.45,
                        help='Extra strafe seconds after edge is found.')
    parser.add_argument('--timeout', type=float, default=60.0,
                        help='Maximum run time in seconds.')
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("SONAR + APRILTAG NAVIGATION DEMO")
    print("=" * 60)
    print()
    print("Goal: reach Area 2 AprilTag %d while clearing fixed barriers." % args.tag_id)
    print()
    print("SAFETY:")
    print("  - The robot will drive, strafe, and turn.")
    print("  - Use only on the floor. It can drive off a table.")
    print("  - Keep hands clear of wheels, barriers, arm, and claw.")
    print("  - Press Ctrl+C to stop.")
    print()
    input("Press Enter when the robot area is clear...")

    navigator = SonarAprilTagNavigator(
        tag_id=args.tag_id,
        target_distance=args.target_distance,
        barrier_cm=args.barrier_cm,
        clear_cm=args.clear_cm,
        strafe_direction=args.strafe_direction,
        extra_clearance_seconds=args.extra_clearance,
        timeout=args.timeout,
    )

    try:
        result = navigator.navigate()
        print()
        print("=" * 60)
        print("Result: %s" % ("SUCCESS" if result['success'] else "STOPPED"))
        print("Reason: %s" % result['reason'])
        print("Barriers cleared: %d" % result['barriers'])
        print("Final tag distance: %.2fm" % result['final_distance'])
        print("Final tag angle: %+0.1fdeg" % result['final_angle'])
        print("=" * 60)

        if result['success']:
            navigator.board.set_buzzer(1000, 0.1, 0.1, 2)

    except KeyboardInterrupt:
        print()
        print("Stopped by user.")
    except Exception as error:
        print()
        print("ERROR: %s" % error)
        import traceback
        traceback.print_exc()
    finally:
        navigator.cleanup()
        print("Motors stopped. Demo complete.")


if __name__ == '__main__':
    main()
