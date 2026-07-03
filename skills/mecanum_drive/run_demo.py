#!/usr/bin/env python3
"""
Mecanum Drive Demo (Level 1: Just Run It!)

Demonstrates all 8 basic movement patterns:
1. Forward
2. Backward  
3. Strafe Right
4. Strafe Left
5. Rotate Clockwise
6. Rotate Counter-Clockwise
7. Diagonal (Forward-Right)
8. Square Pattern

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

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board, PLATFORM
from lib.battery import read_voltage, status_for_voltage

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
        # Mecanum wheel equations
        L = 1.0  # Keep rotation input in motor-duty units for the workshop demo
        fl = vy + vx + omega * L
        fr = vy - vx - omega * L
        rl = vy - vx + omega * L
        rr = vy + vx - omega * L
        
        # Normalize if any wheel exceeds max
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
    
    def rotate_ccw(self, speed, duration):
        """Rotate counter-clockwise."""
        print(f"  Rotating counter-clockwise at {speed}% for {duration}s...")
        # Counter-clockwise/left turn: left side backward, right side forward.
        self._set_motors(-speed, speed, -speed, speed)
        time.sleep(duration)
        self.stop()
    
    def diagonal(self, speed, duration):
        """Move diagonally (forward-right)."""
        print(f"  Moving diagonally (forward-right) at {speed}% for {duration}s...")
        self.drive(speed, speed)
        time.sleep(duration)
        self.stop()
    
    def square(self, speed, side_duration):
        """Drive in a square pattern."""
        print(f"  Executing square pattern...")
        for i in range(4):
            print(f"    Side {i+1}/4")
            self.forward(speed, side_duration)
            time.sleep(0.5)
            self.rotate_cw(40, 1.0)  # 90° turn (approximate)
            time.sleep(0.5)
        self.stop()


def main():
    """Run the complete demonstration."""
    print("=" * 60)
    print("MECANUM DRIVE DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo shows 8 basic movement patterns.")
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
    
    # Check battery
    demo = MecanumDemo(max_speed=50)
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
        duration = 2.0  # seconds per movement
        pause = 1.5     # pause between movements
        speed = 40      # motor speed (0-100)
        
        # Pattern 1: Forward
        print("[1/8] Forward")
        demo.forward(speed, duration)
        time.sleep(pause)
        
        # Pattern 2: Backward
        print("[2/8] Backward")
        demo.backward(speed, duration)
        time.sleep(pause)
        
        # Pattern 3: Strafe Right
        print("[3/8] Strafe Right")
        demo.strafe_right(speed, duration)
        time.sleep(pause)
        
        # Pattern 4: Strafe Left
        print("[4/8] Strafe Left")
        demo.strafe_left(speed, duration)
        time.sleep(pause)
        
        # Pattern 5: Rotate Clockwise
        print("[5/8] Rotate Clockwise")
        demo.rotate_cw(40, 1.2)  # Turns need enough power to overcome floor friction
        time.sleep(pause)
        
        # Pattern 6: Rotate Counter-Clockwise
        print("[6/8] Rotate Counter-Clockwise")
        demo.rotate_ccw(40, 1.2)
        time.sleep(pause)
        
        # Pattern 7: Diagonal
        print("[7/8] Diagonal (Forward-Right)")
        demo.diagonal(speed, duration)
        time.sleep(pause)
        
        # Pattern 8: Square
        print("[8/8] Square Pattern")
        demo.square(speed=35, side_duration=1.5)
        
        print()
        print("=" * 60)
        print("DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("What you just saw:")
        print("  [OK] Forward/Backward - standard wheeled robot can do this")
        print("  [OK] Strafe Left/Right - MECANUM SUPERPOWER! Pure sideways motion")
        print("  [OK] Rotate in place - no turning radius needed")
        print("  [OK] Diagonal - simultaneous forward + strafe")
        print("  [OK] Square pattern - combining movements")
        print()
        print("Next steps:")
        print("  - If motors did not move, re-check battery and Step 3 motor wiring.")
        print("  - If movement direction was wrong, go back to B1: robot Assembly Guide and check motor wiring before changing code.")
        print("  - If everything looked correct, continue with the next C3 test.")
        
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
        # Always stop motors
        demo.stop()
        print()
        print("Motors stopped. Demo complete.")


if __name__ == "__main__":
    main()
