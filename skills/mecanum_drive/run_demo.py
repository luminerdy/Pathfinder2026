#!/usr/bin/env python3
"""
Mecanum Drive Demo (Level 1: Just Run It!)

Demonstrates three square patterns:
1. Standard square: drive forward, right turn, repeat
2. Mecanum square: forward, strafe right, back up, strafe left
3. Diagonal square: four diagonal wheel-pair movements

No code changes needed - just run and watch!

Usage:
    python3 run_demo.py

Safety:
    - Clear a 4-foot by 4-foot area around the robot
    - The robot may move about 2 feet in any direction
    - Robot on floor only. It can drive off a table.
    - Battery check passes
    - Press Ctrl+C to emergency stop

Press Ctrl+C to stop at any time.
"""

import sys
import os
import time

# Add the repository root so this demo can import lib/ when run directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board, PLATFORM
from lib.battery import read_voltage, status_for_voltage


# TEAM TUNING: Change one value at a time, save, and run this demo again.
MAX_MOTOR_SPEED = 50
DRIVE_SPEED = 40
DIAGONAL_SPEED = 50
TURN_SPEED = 40
SIDE_DURATION_SECONDS = 1.4
TURN_DURATION_SECONDS = 1.0
PATTERN_PAUSE_SECONDS = 1.5

class MecanumDemo:
    """Simple mecanum drive demonstration."""
    
    def __init__(self, max_speed=50):
        self.board = get_board()
        self.max_speed = max_speed
    
    def stop(self):
        """Stop all motors."""
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

    def _clamp(self, speed):
        """Clamp motor duty cycle to the robot's safe range."""
        return int(max(-100, min(100, speed)))

    def _set_motors(self, front_left, front_right, rear_left, rear_right):
        """Set all four drive motors using the Pathfinder motor numbering."""
        # The board expects a list of (motor_number, duty_cycle) pairs.
        self.board.set_motor_duty([
            (1, self._clamp(front_left)),   # Front left
            (2, self._clamp(front_right)),  # Front right
            (3, self._clamp(rear_left)),    # Rear left
            (4, self._clamp(rear_right)),   # Rear right
        ])
    
    def drive(self, vx, vy, omega=0):
        """
        Drive with mecanum wheels.
        
        Args:
            vx: Strafe speed (-100 to 100, + = right)
            vy: Forward speed (-100 to 100, + = forward)
            omega: Rotation speed (-100 to 100, + = clockwise/right)
        """
        # Mecanum wheel equations combine sideways, forward, and turning motion.
        L = 1.0  # Keep rotation input in motor-duty units for the workshop demo
        fl = vy + vx + omega * L
        fr = vy - vx - omega * L
        rl = vy - vx + omega * L
        rr = vy + vx - omega * L
        
        # If one wheel would be too fast, scale all wheels down together.
        # That keeps the movement direction the same while staying within limits.
        max_wheel = max(abs(fl), abs(fr), abs(rl), abs(rr))
        if max_wheel > self.max_speed:
            scale = self.max_speed / max_wheel
            fl *= scale
            fr *= scale
            rl *= scale
            rr *= scale
        
        self._set_motors(fl, fr, rl, rr)
    
    def forward(self, speed, duration):
        """Move forward."""
        print(f"  Moving forward at {speed}% for {duration}s...")
        self.drive(0, speed)
        time.sleep(duration)
        self.stop()
    
    def backward(self, speed, duration):
        """Move backward."""
        print(f"  Moving backward at {speed}% for {duration}s...")
        self.drive(0, -speed)
        time.sleep(duration)
        self.stop()
    
    def strafe_right(self, speed, duration):
        """Strafe right."""
        print(f"  Strafing right at {speed}% for {duration}s...")
        self.drive(speed, 0)
        time.sleep(duration)
        self.stop()
    
    def strafe_left(self, speed, duration):
        """Strafe left."""
        print(f"  Strafing left at {speed}% for {duration}s...")
        self.drive(-speed, 0)
        time.sleep(duration)
        self.stop()
    
    def rotate_cw(self, speed, duration):
        """Rotate clockwise."""
        print(f"  Rotating clockwise at {speed}% for {duration}s...")
        # Clockwise/right turn: left side forward, right side backward.
        self._set_motors(speed, -speed, speed, -speed)
        time.sleep(duration)
        self.stop()

    def right_turn(self, speed, duration):
        """Turn right in place."""
        self.rotate_cw(speed, duration)
    
    def rotate_ccw(self, speed, duration):
        """Rotate counter-clockwise."""
        print(f"  Rotating counter-clockwise at {speed}% for {duration}s...")
        # Counter-clockwise/left turn: left side backward, right side forward.
        self._set_motors(-speed, speed, -speed, speed)
        time.sleep(duration)
        self.stop()
    
    def diagonal_forward_right(self, speed, duration):
        """Move diagonally forward using front-left and rear-right motors."""
        print(f"  Moving diagonally forward with front-left and rear-right at {speed}% for {duration}s...")
        self._set_motors(speed, 0, 0, speed)
        time.sleep(duration)
        self.stop()

    def diagonal_forward_left(self, speed, duration):
        """Move diagonally forward using front-right and rear-left motors."""
        print(f"  Moving diagonally forward with front-right and rear-left at {speed}% for {duration}s...")
        self._set_motors(0, speed, speed, 0)
        time.sleep(duration)
        self.stop()

    def diagonal_backward_left(self, speed, duration):
        """Move diagonally backward using front-left and rear-right motors."""
        print(f"  Moving diagonally backward with front-left and rear-right at {speed}% for {duration}s...")
        self._set_motors(-speed, 0, 0, -speed)
        time.sleep(duration)
        self.stop()

    def diagonal_backward_right(self, speed, duration):
        """Move diagonally backward using front-right and rear-left motors."""
        print(f"  Moving diagonally backward with front-right and rear-left at {speed}% for {duration}s...")
        self._set_motors(0, -speed, -speed, 0)
        time.sleep(duration)
        self.stop()
    
    def square(self, speed, side_duration, turn_speed, turn_duration):
        """Drive a standard square by turning at each corner."""
        print("  Executing standard square pattern...")
        for i in range(4):
            print(f"    Side {i+1}/4: forward")
            self.forward(speed, side_duration)
            time.sleep(0.5)
            print(f"    Corner {i+1}/4: right turn")
            # A 90-degree turn is approximate because battery, floor, and tires vary.
            self.right_turn(turn_speed, turn_duration)
            time.sleep(0.5)
        self.stop()

    def mecanum_square(self, speed, side_duration):
        """Drive a square using mecanum sideways movement instead of turns."""
        print("  Executing mecanum square pattern...")
        print("    Side 1/4: forward")
        self.forward(speed, side_duration)
        time.sleep(0.5)
        print("    Side 2/4: strafe right")
        self.strafe_right(speed, side_duration)
        time.sleep(0.5)
        print("    Side 3/4: back up")
        self.backward(speed, side_duration)
        time.sleep(0.5)
        print("    Side 4/4: strafe left")
        self.strafe_left(speed, side_duration)
        time.sleep(0.5)
        self.stop()

    def diagonal_square(self, speed, side_duration):
        """Drive a square/diamond using diagonal mecanum movement."""
        print("  Executing diagonal square pattern...")
        print("    Side 1/4: forward with front-left and rear-right")
        self.diagonal_forward_right(speed, side_duration)
        time.sleep(0.5)
        print("    Side 2/4: forward with front-right and rear-left")
        self.diagonal_forward_left(speed, side_duration)
        time.sleep(0.5)
        print("    Side 3/4: backward with front-left and rear-right")
        self.diagonal_backward_left(speed, side_duration)
        time.sleep(0.5)
        print("    Side 4/4: backward with front-right and rear-left")
        self.diagonal_backward_right(speed, side_duration)
        time.sleep(0.5)
        self.stop()


def main():
    """Run the complete demonstration."""
    print("=" * 60)
    print("MECANUM DRIVE DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo shows three square patterns:")
    print("  1. Standard square")
    print("  2. Mecanum square")
    print("  3. Diagonal square")
    print()
    print("SAFETY:")
    print("  - Clear a 4-foot by 4-foot area around the robot")
    print("  - The robot may move about 2 feet in any direction")
    print("  - Put the robot on the floor only. It can drive off a table.")
    print("  - Press Ctrl+C to emergency stop")
    print()
    print("Press Ctrl+C to stop at any time.")
    print("-" * 60)
    print()
    
    # Check battery before driving so a weak battery does not look like bad code.
    demo = MecanumDemo(max_speed=MAX_MOTOR_SPEED)
    print("Checking battery...")
    v = read_voltage(demo.board)
    if v is not None:
        status, message, ok = status_for_voltage(v, PLATFORM)
        print(f"  Battery: {v:.2f}V")
        print(f"  Status: {status} - {message}")
        if not ok:
            print("  Replace or charge batteries before motor operation.")
            return
    else:
        print("  [WARNING] Could not read battery")
        print("  Check robot power, battery connection, and the motor board connection before continuing.")
    
    print()
    input("Press Enter to start demo...")
    print()
    
    try:
        print("[1/3] Standard Square Pattern")
        demo.square(
            speed=DRIVE_SPEED,
            side_duration=SIDE_DURATION_SECONDS,
            turn_speed=TURN_SPEED,
            turn_duration=TURN_DURATION_SECONDS,
        )
        time.sleep(PATTERN_PAUSE_SECONDS)

        print("[2/3] Mecanum Square Pattern")
        demo.mecanum_square(speed=DRIVE_SPEED, side_duration=SIDE_DURATION_SECONDS)
        time.sleep(PATTERN_PAUSE_SECONDS)

        print("[3/3] Diagonal Square Pattern")
        demo.diagonal_square(speed=DIAGONAL_SPEED, side_duration=SIDE_DURATION_SECONDS)
        
        print()
        print("=" * 60)
        print("DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("What you just saw:")
        print("  [OK] Standard square - forward movement plus turns")
        print("  [OK] Mecanum square - sideways motion without turning")
        print("  [OK] Diagonal square - opposite wheel pairs for diagonal movement")
        print()
        print("Next steps:")
        print("  - If motors did not move, re-check battery and Step 3 motor wiring.")
        print("  - If movement direction was wrong, go back to robot Assembly Guide and check motor wiring before changing code.")
        print("  - If everything looked correct, continue with Sonar Sensors.")
        
        # Victory beep
        demo.board.set_buzzer(1000, 0.1, 0.1, 2)
    
    except KeyboardInterrupt:
        print()
        print("Demo stopped by user (Ctrl+C)")
    
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always stop motors, even after Ctrl+C or an error.
        demo.stop()
        print()
        print("Motors stopped. Demo complete.")


if __name__ == "__main__":
    main()
