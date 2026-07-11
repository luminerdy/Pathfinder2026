#!/usr/bin/env python3
"""
Web Control Interface for Pathfinder2026

Provides:
- Live video stream
- Drive controls (WASD/arrows)
- Servo sliders (6 servos)
- Save/load arm positions
- Real-time battery monitoring

Usage:
    python3 web_control.py
    Then open: http://<ROBOT_IP>:8080
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import json
import sys, os
import threading
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.board import get_board
from lib.battery import read_voltage
BoardController = None  # Use get_board() instead

app = Flask(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
SAVED_POSITIONS_PATH = REPO_ROOT / 'saved_positions.json'

# Global state
board = get_board()
camera = None  # Opened lazily to avoid locking camera on import
state_lock = threading.Lock()
board_lock = threading.Lock()
battery_cache = {
    'voltage': None,
    'updated_at': 0,
}

ALLOWED_DIRECTIONS = {
    'forward', 'backward', 'left', 'right',
    'strafe_left', 'strafe_right', 'stop',
}

SERVO_LIMITS = {
    1: (1550, 2500),  # Claw/gripper. 1550=closed, 2500=open.
    3: (500, 2500),   # Wrist
    4: (500, 2500),   # Elbow
    5: (500, 2500),   # Shoulder
    6: (500, 2500),   # Base
}


def clamp(value, low, high):
    return max(low, min(high, int(value)))


def get_battery_voltage(max_age=5.0, retries=1, delay=0.0):
    """Return a recent battery voltage without blocking drive controls."""
    now = time.time()
    if battery_cache['voltage'] is not None and now - battery_cache['updated_at'] <= max_age:
        return battery_cache['voltage']

    with board_lock:
        voltage = read_voltage(board, retries=retries, delay=delay)

    if voltage is not None:
        battery_cache['voltage'] = voltage
        battery_cache['updated_at'] = time.time()
    return voltage


def set_drive_motors(commands):
    """Send drive motor commands without sharing the board port with other requests."""
    with board_lock:
        board.set_motor_duty(commands)


def get_camera():
    """Get or open camera (lazy initialization)"""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(0.5)
    return camera

# Servo positions (match startup script camera-forward position)
servo_positions = {
    1: 2500,  # Claw (Gripper open)
    3: 590,   # Wrist
    4: 2450,  # Elbow
    5: 700,   # Shoulder
    6: 1500   # Base (center/forward)
}

# Saved positions
saved_positions = {}

# Motor power (global, can be adjusted via web interface)
motor_power = {
    'drive': 30,
    'turn': 30
}

def generate_frames():
    """Generate video frames for streaming"""
    while True:
        cam = get_camera()
        success, frame = cam.read()
        if not success:
            break

        # Add battery voltage overlay
        voltage = get_battery_voltage(max_age=5.0, retries=1, delay=0.0)
        if voltage:
            color = (0, 255, 0) if voltage > 8.2 else (0, 165, 255) if voltage > 8.0 else (0, 0, 255)
            cv2.putText(frame, f"Battery: {voltage:.2f}V", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Add servo positions overlay
        y_pos = 70
        for servo_id in sorted(servo_positions.keys()):
            pos = servo_positions[servo_id]
            cv2.putText(frame, f"S{servo_id}: {pos}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_pos += 30

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Serve main control page"""
    return render_template('control.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/drive', methods=['POST'])
def drive():
    """Drive motor control"""
    try:
        data = request.json
        direction = data.get('direction')
        if direction not in ALLOWED_DIRECTIONS:
            return jsonify({'status': 'error', 'message': 'Invalid direction'}), 400

        if direction == 'stop':
            set_drive_motors([(1, 0), (2, 0), (3, 0), (4, 0)])
            return jsonify({'status': 'ok'})

        # Safety check: prevent motor commands at low battery
        voltage = get_battery_voltage(max_age=10.0, retries=1, delay=0.0)
        if voltage:
            if voltage < 7.8:
                return jsonify({'status': 'error',
                              'message': f'Battery too low ({voltage:.2f}V) - Replace batteries!'})

        drive_pwr = motor_power['drive']
        turn_pwr = motor_power['turn']

        # Limit max power to prevent crashes
        drive_pwr = min(drive_pwr, 40)
        turn_pwr = min(turn_pwr, 40)

        if direction == 'forward':
            set_drive_motors([(1, drive_pwr), (2, drive_pwr),
                                  (3, drive_pwr), (4, drive_pwr)])
        elif direction == 'backward':
            set_drive_motors([(1, -drive_pwr), (2, -drive_pwr),
                                  (3, -drive_pwr), (4, -drive_pwr)])
        elif direction == 'left':
            set_drive_motors([(1, -turn_pwr), (2, turn_pwr),
                                  (3, -turn_pwr), (4, turn_pwr)])
        elif direction == 'right':
            set_drive_motors([(1, turn_pwr), (2, -turn_pwr),
                                  (3, turn_pwr), (4, -turn_pwr)])
        elif direction == 'strafe_left':
            set_drive_motors([(1, -drive_pwr), (2, drive_pwr),
                                  (3, drive_pwr), (4, -drive_pwr)])
        elif direction == 'strafe_right':
            set_drive_motors([(1, drive_pwr), (2, -drive_pwr),
                                  (3, -drive_pwr), (4, drive_pwr)])

        return jsonify({'status': 'ok'})

    except Exception as e:
        # Emergency stop on any error
        print(f"Error in drive(): {e}")
        try:
            set_drive_motors([(1, 0), (2, 0), (3, 0), (4, 0)])
        except:
            pass
        return jsonify({'status': 'error', 'message': 'Drive command failed'}), 500

@app.route('/servo', methods=['POST'])
def servo():
    """Servo control"""
    try:
        data = request.json or {}
        servo_id = int(data.get('servo'))
        position = int(data.get('position'))
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Invalid servo request'}), 400

    if servo_id not in SERVO_LIMITS:
        return jsonify({'status': 'error', 'message': 'Invalid servo id'}), 400

    low, high = SERVO_LIMITS[servo_id]
    position = clamp(position, low, high)

    # Update position
    with state_lock:
        servo_positions[servo_id] = position

    # Send to board
    with board_lock:
        board.set_servo_position(500, [(servo_id, position)])

    return jsonify({'status': 'ok', 'servo': servo_id, 'position': position})

@app.route('/save_position', methods=['POST'])
def save_position():
    """Save current arm position"""
    data = request.json
    name = str(data.get('name', '')).strip()[:40]
    if not name:
        return jsonify({'status': 'error', 'message': 'Position name required'}), 400

    with state_lock:
        saved_positions[name] = servo_positions.copy()

        # Save to file
        with open(SAVED_POSITIONS_PATH, 'w') as f:
            json.dump(saved_positions, f, indent=2)

    return jsonify({'status': 'ok', 'name': name, 'positions': servo_positions})

@app.route('/load_position', methods=['POST'])
def load_position():
    """Load saved arm position"""
    data = request.json
    name = data.get('name')
    if not isinstance(name, str):
        return jsonify({'status': 'error', 'message': 'Position name required'}), 400

    with state_lock:
        position_found = name in saved_positions
        positions = saved_positions[name].copy() if position_found else None

    if position_found:
        clamped_positions = {}
        for sid, pos in positions.items():
            sid = int(sid)
            if sid in SERVO_LIMITS:
                low, high = SERVO_LIMITS[sid]
                clamped_positions[sid] = clamp(pos, low, high)

        # Apply all servos
        servo_list = [(sid, pos) for sid, pos in clamped_positions.items()]
        with board_lock:
            board.set_servo_position(500, servo_list)

        # Update state
        with state_lock:
            servo_positions.update(clamped_positions)

        return jsonify({'status': 'ok', 'name': name, 'positions': clamped_positions})
    else:
        return jsonify({'status': 'error', 'message': 'Position not found'}), 404

@app.route('/get_positions', methods=['GET'])
def get_positions():
    """Get all saved positions"""
    with state_lock:
        return jsonify({'positions': list(saved_positions.keys()),
                       'current': servo_positions})

@app.route('/battery', methods=['GET'])
def battery():
    """Get battery voltage"""
    voltage = get_battery_voltage(max_age=2.0, retries=1, delay=0.0) or 0

    return jsonify({'voltage': voltage,
                   'status': 'good' if voltage > 8.2 else 'low' if voltage > 8.0 else 'critical'})

@app.route('/motor_power', methods=['GET'])
def get_motor_power():
    """Get current motor power settings"""
    return jsonify(motor_power)

@app.route('/motor_power', methods=['POST'])
def set_motor_power():
    """Set motor power"""
    data = request.json
    try:
        with state_lock:
            if 'drive' in data:
                motor_power['drive'] = clamp(data['drive'], 0, 50)
            if 'turn' in data:
                motor_power['turn'] = clamp(data['turn'], 0, 50)
            return jsonify({'status': 'ok', 'motor_power': motor_power})
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Invalid motor power'}), 400

# Load saved positions on startup
try:
    with open(SAVED_POSITIONS_PATH, 'r') as f:
        saved_positions = json.load(f)
        # Convert string keys to ints for servo_positions dict
        for name, positions in saved_positions.items():
            saved_positions[name] = {int(k): v for k, v in positions.items()}
except FileNotFoundError:
    pass

if __name__ == '__main__':
    print("="*70)
    print("Pathfinder2026 Web Control")
    print("="*70)
    print()

    # Position robot to startup/camera-forward position
    print("Positioning robot to startup position...")
    try:
        # Turn off sonar LEDs (both LEDs on the sonar)
        with board_lock:
            board.set_rgb([(0, 0, 0, 0), (1, 0, 0, 0)])

        # Stop motors
        set_drive_motors([(1, 0), (2, 0), (3, 0), (4, 0)])

        # Move to camera-forward position (ONE SERVO AT A TIME to avoid power spike)
        camera_forward = [
            (1, 2500),  # Claw open
            (6, 1500),  # Base center
            (5, 700),   # Shoulder
            (4, 2450),  # Elbow
            (3, 590),   # Wrist
        ]

        print("  Moving servos sequentially...")
        for servo_id, pwm in camera_forward:
            with board_lock:
                board.set_servo_position(800, [(servo_id, pwm)])  # Slower speed (800ms)
            time.sleep(0.5)  # Longer delay between servos

        print("  Robot positioned to camera-forward")
    except Exception as e:
        print(f"  Warning: Could not position robot: {e}")

    print()
    print("Starting web server...")
    print("Open in browser: http://<ROBOT_IP>:8080")
    print()
    print("Controls:")
    print("  WASD or Arrow keys - Drive")
    print("  Q/E - Strafe left/right")
    print("  Space - Stop")
    print("  Sliders - Servo control")
    print("  Save/Load - Store arm positions")
    print()

    app.run(host='0.0.0.0', port=8080, threaded=True)
